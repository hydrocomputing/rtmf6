"""Run all sub models."""

import multiprocessing as mp
from pathlib import Path
import shelve
import shutil

from phreeqpy.phreeqcrm.rm_model import PhreeqcRMModel
from pymf6.api import States
from pymf6.mf6 import MF6
from pymf6.datastructures import TIME_UNIT_VALUES


def run_model(
    model_path,
    queue_from_mf6,
    queue_from_phrq,
    reaction_model_name,
    reaction_start_stress_range,
):
    """Run a model in its own process."""
    mf6 = MF6(sim_path=Path(model_path), do_solution_loop=False)
    time_conversion_factor = TIME_UNIT_VALUES[mf6.simulation.TDIS.ITMUNI.value]
    gwt_models = mf6.models['gwt6']
    gwt = gwt_models[reaction_model_name]
    start, end = reaction_start_stress_range
    for model_step in mf6.model_loop():
        if reaction_model_name not in model_step.simulation_group.model_names:
            continue
        if start <= gwt.kper <= end:
            if model_step.state == States.timestep_end:
                var_name = f'SLN_{gwt.solution_id}/X'
                queue_from_mf6.put({
                    'totim': gwt.totim * time_conversion_factor,
                    'conc': mf6.vars[var_name]}
                    )
                # pylint: disable=protected-access
                mf6._mf6.set_value(var_name, queue_from_phrq.get())
    queue_from_mf6.put(None)


def run_rtmf6(config, reactions=True):
    """Run all sub models."""
    # pylint: disable=too-many-locals
    phreeqcrm_model = PhreeqcRMModel(
        str(config.project_settings['phreeqcrm']['model_yaml_file'])
    )
    output_config = config.project_settings.get('output')
    output = None
    if output_config:
        output = Output(config.project_path, output_config=output_config,
                        phreeqcrm_model=phreeqcrm_model)
    processes = {}
    queues_from_mf6 = {}
    queues_from_phrq = {}
    for path in (config.internal_paths.component_models_path).glob('*'):
        model_name = path.name
        queue_from_mf6 = mp.Queue()
        queue_from_phrq = mp.Queue()
        process = mp.Process(
            target=run_model,
            kwargs={
                'model_path': path,
                'queue_from_mf6': queue_from_mf6,
                'queue_from_phrq':queue_from_phrq,
                'reaction_model_name': config.reaction_model_name,
                'reaction_start_stress_range': config.reaction_start_stress_range,
            },
        )
        processes[model_name] = process
        queues_from_mf6[model_name] = queue_from_mf6
        queues_from_phrq[model_name] = queue_from_phrq
        process.start()
    done = False
    step = 0
    last_totim = 0
    while True:
        step += 1
        print(f'step: {step:5d}', end='\r')
        conc_mf6 = {}
        totims = set()
        for component, queue in queues_from_mf6.items():
            res = queue.get()
            if res is None:
                done = True
                break
            conc_mf6[component] = res['conc']
            totims.add(res['totim'])
        if done:
            break
        assert len(totims) == 1
        totim = tuple(totims)[0]
        delta_t = totim - last_totim
        last_totim = totim
        for component, mf6_conc in conc_mf6.items():
            if reactions:
                phreeqcrm_conc = phreeqcrm_model.concentrations[component]
                phreeqcrm_conc[:] = mf6_conc
            else:
                queues_from_phrq[component].put(mf6_conc)
        if reactions:
            if output:
                output.save(step)
            phreeqcrm_model.write_conc_back()
            phreeqcrm_model._rm.SetTimeStep(delta_t)
            phreeqcrm_model.update()
            for component, mf6_conc in conc_mf6.items():
                phreeqcrm_conc = phreeqcrm_model.concentrations[component]
                queues_from_phrq[component].put(phreeqcrm_conc)
    for process in processes.values():
        process.join()


class Output:

    def __init__(self, project_path, phreeqcrm_model, output_config):
        self.project_path = project_path
        self.phreeqcrm_model = phreeqcrm_model
        self.output_config = output_config
        self.equilibrium_phases_files = self._init_phase_output()
        self.concentrations_files = self._init_conc_output()

    def _create_outdir(self, dir_name):
        dir_path = self.project_path / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True)
        return dir_path

    def _init_conc_output(self):
        concentrations_files = {}
        concentrations_dir_name = self.output_config.get('concentrations')
        if concentrations_dir_name:
            concentrations_dir = self._create_outdir(concentrations_dir_name)
            for name in self.phreeqcrm_model.concentrations.names:
                db_file_name = f'{name}.shelve'
                concentrations_files[name] = concentrations_dir / db_file_name
        return concentrations_files

    def _init_phase_output(self):
        equilibrium_phases_files = {}
        equilibrium_phases_dir_name = self.output_config.get('equilibrium_phases')
        if equilibrium_phases_dir_name:
            equilibrium_phases_dir = self._create_outdir(equilibrium_phases_dir_name)
            for name in self.phreeqcrm_model.rm_variables.names:
                if name.startswith('equilibrium_phases_moles_'):
                    db_file_name = f'{name.rsplit('_', 1)[-1]}.shelve'
                    equilibrium_phases_files[name] = equilibrium_phases_dir / db_file_name
        return equilibrium_phases_files

    def save(self, step):
        """Save PhreeqcRM output."""
        for name, db_file in self.equilibrium_phases_files.items():
            value = getattr(self.phreeqcrm_model.rm_variables, name).value
            with shelve.open(db_file) as db:
                db[str(step)] = value
        for name, db_file in self.concentrations_files.items():
            value = self.phreeqcrm_model.concentrations[name]
            with shelve.open(db_file) as db:
                db[str(step)] = value


if __name__ == '__main__':
    import sys

    mp.set_start_method('spawn')
    run_rtmf6(sys.argv[1], reactions=True)

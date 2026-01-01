"""Run all sub models."""

import multiprocessing as mp
from pathlib import Path

from phreeqpy.phreeqcrm.rm_model import PhreeqcRMModel

from pymf6.api import States
from pymf6.mf6 import MF6


def run_model(
    model_path, queue_from_mf6, queue_from_phrq, kpers=(1,), sim_file_name='mfsim.nam'
):
    """Run a model in its own process."""
    mf6 = MF6(sim_path=Path(model_path))
    gwt_models = mf6.models['gwt6']
    gwt = gwt_models[list(gwt_models.keys())[0]]
    for model_step in mf6.model_loop():
        if gwt.kper in kpers and model_step.state == States.timestep_end:
            var_name = f'SLN_{gwt.solution_id}/X'
            queue_from_mf6.put(mf6.vars[var_name])
            mf6._mf6.set_value(var_name, queue_from_phrq.get())
    queue_from_mf6.put(None)


def main(model_path, phreeqcrm_yaml, reactions=True, component_models_path='component_models'):
    """Run all sub models."""
    phreeqcrm_model = PhreeqcRMModel(str(phreeqcrm_yaml))
    processes = {}
    queues_from_mf6 = {}
    queues_from_phrq = {}
    for path in (model_path / component_models_path).glob('*'):
        model_name = path.name
        queue_from_mf6 = mp.Queue()
        queue_from_phrq = mp.Queue()
        process = mp.Process(
            target=run_model,
            kwargs=dict(model_path=path, queue_from_mf6=queue_from_mf6,
                        queue_from_phrq=queue_from_phrq))
        processes[model_name] = process
        queues_from_mf6[model_name] = queue_from_mf6
        queues_from_phrq[model_name] = queue_from_phrq
        process.start()
    done = False
    step = 1
    while True:
        step += 1
        print(f'step: {step:5d}', end='\r')
        conc_mf6 = {component: queue.get() for component, queue in
                    queues_from_mf6.items()}
        for component, mf6_conc in conc_mf6.items():
            if mf6_conc is None:
                done = True
                break
            if reactions:
                phreeqcrm_conc = phreeqcrm_model.concentrations[component]
                phreeqcrm_conc[:] = mf6_conc
            else:
                queues_from_phrq[component].put(mf6_conc)
        if done:
            break
        if reactions:
            phreeqcrm_model.write_conc_back()
            phreeqcrm_model.update()
            for component, mf6_conc in conc_mf6.items():
                phreeqcrm_conc = phreeqcrm_model.concentrations[component]
                queues_from_phrq[component].put(phreeqcrm_conc)
    for process in processes.values():
        process.join()


if __name__ == '__main__':

    mp.set_start_method('spawn')
    main()

"""Run all sub models."""

import multiprocessing as mp
from pathlib import Path
from time import sleep

from pymf6.api import States
from pymf6.mf6 import MF6


def run_model(
    model_path, queue_in, queue_out, kpers=(1,), sim_file_name='mfsim.nam'
):
    """Run a model in its own process."""
    mf6 = MF6(nam_file=Path(model_path) / sim_file_name)
    for model in mf6.model_loop():
        if (
            model.kper in kpers
            and model.type == 'gwt6'
            and model.state == States.timestep_end
        ):
            var_name = f'SLN_{model.solution_id}/X'
            queue_out.put(model.conc.flatten())
            mf6._mf6.set_value(var_name, queue_in.get())
    queue_out.put(None)


def main(model_path, sub_models_path='sub_models'):
    """Run all sub models."""
    processes = {}
    queues_in = {}
    queues_out = {}
    for path in (model_path / sub_models_path).glob('*'):
        model_name = path.name
        queue_in = mp.Queue()
        queue_out = mp.Queue()
        process = mp.Process(
            target=run_model,
            args=(path, queue_in, queue_out))
        processes[model_name] = process
        queues_in[model_name] = queue_in
        queues_out[model_name] = queue_out
        process.start()
    done = False
    while True:
        conc_mf6 = {
            component: queue.get() for component, queue in queues_out.items()}
        for component, conc in conc_mf6.items():
            if conc is None:
                done = True
                break
            queues_in[component].put(conc * 0.99)
        if done:
            break
    for process in processes.values():
        process.join()


if __name__ == '__main__':
    mp.set_start_method('spawn')
    main()

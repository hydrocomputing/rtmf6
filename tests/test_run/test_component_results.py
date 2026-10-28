"""Tests for receiving results from component model processes."""

import multiprocessing as mp
import sys
import time

import pytest

from rtmf6.run import (
    ComponentModelError,
    MainProcessError,
    get_component_result,
    get_main_result,
)


def test_result_of_running_process():
    queue = mp.Queue()
    process = mp.Process(target=time.sleep, args=(5,))
    process.start()
    queue.put({'conc': 1})
    assert get_component_result(queue, process, 'Na') == {'conc': 1}
    process.terminate()
    process.join()


def test_dead_process_raises():
    queue = mp.Queue()
    process = mp.Process(target=sys.exit, args=(3,))
    process.start()
    with pytest.raises(ComponentModelError, match='Na.*exit code 3'):
        get_component_result(queue, process, 'Na', poll_interval=0.1)


class _Parent:
    """Stand-in for the parent process."""

    def __init__(self, alive):
        self.alive = alive

    def is_alive(self):
        return self.alive


def test_result_from_main_process():
    queue = mp.Queue()
    queue.put([1.0, 2.0])
    assert get_main_result(queue, parent=_Parent(alive=True)) == [1.0, 2.0]


def test_dead_main_process_raises():
    queue = mp.Queue()
    with pytest.raises(MainProcessError):
        get_main_result(queue, parent=_Parent(alive=False), poll_interval=0.1)

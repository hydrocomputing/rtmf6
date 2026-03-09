"""Read shelve output."""


from pathlib import Path
import shelve

import numpy as np

from pymf6.mf6 import MF6
from rtmf6.config import Config


class ShelveViewer:
    """Show values savee in shelve files."""

    def __init__(self, config_file=None, config=None, ):
        if config:
            self._config = config
        elif config_file:
            self._config = Config(config_file)
        else:
            raise Exception('need to specify either `config` or `config_file`')
        shape = self._get_shape()
        self._attr_names = []
        for directory in self._config.out_path.iterdir():
            name = directory.name
            setattr(self, name, OutputType(directory, shape))
            self._attr_names.append(name)

    def _get_shape(self):
        mf6 = MF6(sim_path=self._config.mf6_path)
        model_name=self._config.project_settings['models']['reaction_models'][0]
        transport_models = mf6.models['gwt6']
        gwt = transport_models[model_name]
        return gwt.shape

    def _repr_html_(self):
        return _repr_html(self._attr_names)


class OutputType:
    """Type of output."""

    def __init__(self, path, shape):
        self._attr_names = []
        for directory in path.iterdir():
            name = directory.name.split('.')[0]
            setattr(self, name, Value(directory, shape))
            self._attr_names.append(name)

    def _repr_html_(self):
        return _repr_html(self._attr_names)


class Value:
    """Output values."""

    def __init__(self, path, shape):
        self._path = path
        self._shape = shape

    @property
    def time_steps(self):
        with shelve.open(self._path) as db:
            return sorted(int(step) for step in db.keys())

    def get_value(self, time_step):
        """Get a value for a time step."""
        with shelve.open(self._path) as db:
            value = db[str(time_step)]
            if type(value) is dict:
                return {key: arr.reshape(self._shape) for key, arr in value.items()}
            elif type(value) is np.ndarray:
                return value.reshape(self._shape)
            else:
                raise ValueError(f'unkown type {type(value)}')

    def _repr_html_(self):
        return _repr_html([name for name in self.__class__.__dict__ if not name.startswith('_')])


def _repr_html(names):
    """Make HTML representation."""
    out = '<table>'
    out += '<tr><th>Available Attributes</th></tr>'
    out += '\n'.join(f'<tr><td>{name}</td></tr>' for name in names)
    out += '</table>'
    return out

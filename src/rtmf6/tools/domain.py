"""Calculation domain.

MODFLOW 6 uses IDOMAIN in the DIS package to specify which cells are
active in the flow and transport models. Positive values indicate active
cells. IDOMAIN values of 0 and -1 indicate inactive cells that are not
included in the solution.
Cells with value of -1 are referred to as “vertical pass through” cells.
There is no difference of 0 and -1 for coupling with PhreeqcRM.

The transport solution is one-dimensional and contains only the active
cells. Only the active cells are included in the solution and passed to
PhreeqcRM. Therefore, if there are inactive cells, the total number of
cells in the solution will be smaller than the total number of cells in
the grid.

In addition, there can be cells that are active in MODFLOW but are set
to inactive in PhreeqcRM via CreateMapping(). These cells include the
CNC cells that keep the concentration constant ans should not trigger
reactions in PhreeqcRM.

The concept of inactive PhreeqcRM cells can also be used to reduce
the number of reaction cells. Since the non-active PhreeqcRM cells are
computed for each stress period, it can be used to dynamically reduce
the number of reaction cells and thus reduce the computational time.
Currently, this is not implemented in rtmf6 but it is a potential future
improvement.
"""

import numpy as np


class Domain:
    """Domain of the model."""

    def __init__(self, sim, model_name):
        self.sim = sim
        self.active_cells = self._get_active_cells_mask(model_name)
        self.nxyz = int(np.sum(self.active_cells))
        self.all_cells_active = self.active_cells.sum() == self.active_cells.size

    def _get_active_cells_mask(self, model_name):
        """Get distribution of solution numbers."""
        dis = self.sim.get_model(model_name).get_package('dis')
        idomain = dis.idomain.array
        if idomain is None:
            init = self.sim.get_model(model_name).get_package('ic')
            size = init.strt.array.size
            return np.ones(size, dtype=bool)
        return (idomain > 0).flatten()
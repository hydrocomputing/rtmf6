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

from importlib.metadata import version
import numpy as np
import phreeqcrm


class Domain:
    """Domain of the model."""

    def __init__(self, sim, model_name):
        self.sim = sim
        self.idomain_3d = self._get_active_cells_mask(model_name)
        idomain_1d = self.idomain_3d.flatten()
        self.active_cells = idomain_1d > 0
        self.nxyz = int(np.sum(self.active_cells))
        self.all_cells_active = self.active_cells.sum() == self.active_cells.size
        self.domain_all = np.ones_like(self.idomain_3d, dtype=bool)
        self.good_version = False

    def _get_active_cells_mask(self, model_name):
        """Find active cells."""
        dis = self.sim.get_model(model_name).get_package('dis')
        idomain_array = dis.idomain.array
        if idomain_array is None:
            init = self.sim.get_model(model_name).get_package('ic')
            idomain_3d = np.ones_like(init.strt.array, dtype=bool)
        else:
            idomain_3d = idomain_array > 0
        return idomain_3d

    def process_bcs(self, bc_concs):
        """Process bc concentrations."""
        inactive_indices = {}
        grid2chems = {}
        for bc_conc in bc_concs:
            for period_no, inactive_coords in bc_conc.inactive_indices.items():
                mask = self.domain_all.copy()
                for coords in inactive_coords:
                    mask[coords] = False
                flat_mask = mask.flatten()[self.idomain_3d.flatten()]
                inactive = np.argwhere(~flat_mask).flatten()
                inactive_indices[period_no] = np.array(inactive)
                continuous_indices = iter(range(self.nxyz))
                grid2chem = []
                for index in range(self.nxyz):
                    if index in inactive:
                        grid2chem.append(-1)
                    else:
                        grid2chem.append(next(continuous_indices))
                grid2chems[period_no] = np.array(grid2chem)
        self.inactive_indices = inactive_indices
        self.grid2chems = grid2chems

    def create_mapping(self, rm, kper):
        """Create mapping for the current stress period."""
        inactive = self.inactive_indices.get(kper)
        if inactive is None:
            # if there are no inactive cells, create a one-to-one mapping
            rm.CreateMapping(np.arange(self.nxyz))
        else:
            self.check_phreeqcrm_version()
            grid2chem = self.grid2chems[kper]
            rm.CreateMapping(grid2chem)
        return inactive

    def check_phreeqcrm_version(self, min_version='0.0.17'):
        """Check minimum phreeqcrm version."""
        if self.good_version:
            return

        def version_tuple(v):
            return tuple(map(int, v.split('.')))

        current_version = version('phreeqcrm')
        if version_tuple(current_version) < version_tuple(min_version):
            raise ImportError(
                f'phreeqcrm version must be at least {min_version}, found {current_version}'

        )
        self.good_version = True

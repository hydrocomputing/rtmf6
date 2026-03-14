import flopy
import numpy as np
import matplotlib.pyplot as plt


sim_name = 'ex10_simple'
gwf_name = f'gwf_{sim_name}'
gwt_name = f'gwt_{sim_name}'
sim_ws = './mf6'

sim = flopy.mf6.MFSimulation.load(sim_name=sim_name, sim_ws=sim_ws)
gwf = sim.get_model(gwf_name)

species = 'Tolu'
path = './.internal/component_models/'+species+'/'
ucn_file = path + f"{gwt_name}.ucn"

# Read concentration file
ucnobj = flopy.utils.HeadFile(ucn_file, text="CONCENTRATION")

# Get times
times = ucnobj.get_times()
#print("Output times:", times)

# Get last timestep concentration
conc_all = ucnobj.get_alldata()

# Access model grid
mg = gwf.modelgrid

# Get cell center coordinates
x = mg.xcellcenters
y = mg.ycellcenters
i = -1
conc2 = conc_all[-1]

#conc[conc>35]=35
plt.pcolor(x,y,conc2[0,:,:],cmap='jet')
plt.colorbar()
plt.show()
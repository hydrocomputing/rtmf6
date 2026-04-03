import flopy
import matplotlib.pyplot as plt
from rtmf6.postprocessing.output_reader import ShelveViewer
import numpy as np

#%% Shelve
viewer = ShelveViewer('rtmf6.toml') ## load from selected output

#%% LOAD MODEL
sim_name = 'cat_ex_1d'
gwf_name = f'gwf_{sim_name}'
gwt_name = f'gwt_{sim_name}'
sim_ws = './mf6'

sim = flopy.mf6.MFSimulation.load(
    sim_name,
    'mf6',
    exe_name='mf6',
    sim_ws=sim_ws
)

gwf = sim.get_model(gwf_name)

mg = gwf.modelgrid
x = mg.xcellcenters
y = mg.ycellcenters

#%% extract from selected output
ntimes = gwf.modeltime.nstp[-1]
Orgc_im = viewer.selected_output.selected_output_1.get_value(ntimes)['Orgc_im']
Orgc = viewer.selected_output.selected_output_1.get_value(ntimes)['Orgc']

plt.plot(x[0,:]*100,Orgc_im[0,0,:],'o')
plt.xlabel('Length (cm)')
plt.ylabel('OrgC_immobile (KINETIC) (mol/L)')
plt.title('Profile over x\nInitial Orgc_immobile concentration = 0.001 mol/L')

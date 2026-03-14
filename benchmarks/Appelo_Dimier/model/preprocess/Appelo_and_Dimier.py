#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 08:34:42 2026 in the year of the Lord

@author: janek
"""

import flopy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
#%% units and names
length_units = 'meters'
time_units = 'days'
sim_name = 'appelo_uran'
gwf_name = f'gwf_{sim_name}'
gwt_name = f'gwt_{sim_name}'
sim_ws = '../mf6'
concentration_name = 'concentration' # name for concentration
rtmf6_sol_number_name = 'rtmf6_sol_number' # solution number of PHREEQC solution


sim = flopy.mf6.MFSimulation(sim_name=sim_name, sim_ws=sim_ws)

nper = 1
perlen = 7300
nstp = 100

#%% TIME DIS
tdis = flopy.mf6.ModflowTdis(
    sim,
    nper=nper,
    perioddata=[(perlen, nstp, 1.0)],
    time_units=time_units)

#%% gwf

gwf = flopy.mf6.ModflowGwf(
    sim,
    modelname=gwf_name,
    save_flows=True,
    model_nam_file=f"{gwf_name}.nam",
)

#%% Flow solver parameters
nouter, ninner = 300, 600
hclose, rclose, relax = 1e-6, 1e-6, 1.0


imsgwf = flopy.mf6.ModflowIms(
    sim,
    complexity="complex",
    print_option="SUMMARY",
    outer_dvclose=hclose,
    outer_maximum=nouter,
    under_relaxation="NONE",
    inner_maximum=ninner,
    inner_dvclose=hclose,
    rcloserecord=rclose,
    linear_acceleration="CG",
    scaling_method="NONE",
    reordering_method="NONE",
    relaxation_factor=relax,
    filename=f"{gwf_name}.ims",
)
sim.register_ims_package(imsgwf, [gwf.name])

#%% DIS
nlay = 1  # Number of layers
ncol = 100 # Number of columns
nrow = 40  # Number of rows
delr = 20 #
delc = 1.25
top = 1
botm = np.array([0])
dis = flopy.mf6.ModflowGwfdis(
    gwf,
    length_units=length_units,
    nlay=nlay,
    nrow=nrow,
    ncol=ncol,
    delr=delr,
    delc=delc,
    top = top,
    botm = botm,
    filename=f"{gwf_name}.dis",
    nogrb=True,
)

#%% NPF
k11 = 100.0  # Horizontal hydraulic conductivity ($m/d$)
k33 = k11  # Vertical hydraulic conductivity ($m/d$)
icelltype = 0 #


npf = flopy.mf6.ModflowGwfnpf(
    gwf,
    save_flows=True,
    save_saturation=True,
    icelltype=icelltype,
    k=k11,
    k33=k33,
    save_specific_discharge=True,
    filename=f"{gwf_name}.npf",
)

flopy.mf6.ModflowGwfic(gwf, strt=1, filename=f"{gwf_name}.ic")

#%% Injection
q = 1.5 #injection rate m3/d
concentration = 0  # will be replaced

wel_spd = [[(0, 0, 0), q, concentration, 1],[(0, 39, 0), q, concentration, 3]] # well stress period data
auxiliary = [
    concentration_name, # name for concentration
    rtmf6_sol_number_name # solution number of PHREEQC solution
]
wel = flopy.mf6.ModflowGwfwel(
        gwf,
        stress_period_data=wel_spd,
        save_flows=True,
        auxiliary=auxiliary,
        pname='wel',
        filename=f"{gwf_name}.wel"
    )


#%% CHD
chd_spd = []
auxiliary = [
    concentration_name, # name for concentration
    rtmf6_sol_number_name # solution number of PHREEQC solution
]


chd_spd.append([(0, 19, 99), 10,0,0])


chd = flopy.mf6.ModflowGwfchd(
    gwf,
    maxbound=len(chd_spd),
    stress_period_data=chd_spd,
    save_flows=False,
    auxiliary=auxiliary,
    pname="CHD",
    filename=f"{gwf_name}.chd",
)


#%% OC
oc_gwf = flopy.mf6.ModflowGwfoc(
    gwf,
    head_filerecord=f"{gwf_name}.hds",
    budget_filerecord=f"{gwf_name}.cbb",
    headprintrecord=[("COLUMNS", 10, "WIDTH", 15, "DIGITS", 6, "GENERAL")],
    saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    printrecord=[("HEAD", "LAST"), ("BUDGET", "LAST")],
)

#%% Transport
gwt = flopy.mf6.MFModel(
    sim,
    model_type="gwt6",
    modelname=gwt_name,
    model_nam_file=f"{gwt_name}.nam"
)



#%% Transport solver parameters
imsgwt = flopy.mf6.ModflowIms(
    sim,
    print_option="SUMMARY",
    outer_dvclose=hclose,
    outer_maximum=nouter,
    under_relaxation="NONE",
    inner_maximum=ninner,
    inner_dvclose=hclose,
    rcloserecord=rclose,
    linear_acceleration="BICGSTAB",
    scaling_method="NONE",
    reordering_method="NONE",
    relaxation_factor=relax,
    filename=f"{gwt_name}.ims",
)
sim.register_ims_package(imsgwt, [gwt.name])


#%% Trabsport DIS
gwt_dis = flopy.mf6.ModflowGwtdis(
    gwt,
    length_units=length_units,
    nlay=nlay,
    nrow=nrow,
    ncol=ncol,
    delr=delr,
    delc=delc,
    top = top,
    botm = botm,
    filename=f"{gwt_name}.dis",
    nogrb=True,
)

#%% Transport IC
zones = np.flipud(np.loadtxt('./zones.txt'))
gwt_ic = flopy.mf6.ModflowGwtic(
    gwt,
    strt=zones,  # rtmf6 solution number
    filename=f"{gwt_name}.ic")

#%% Transport SSM
sourcerecarray = ['wel', 'aux', concentration_name]

ssm = flopy.mf6.ModflowGwtssm(
    gwt,
    sources=sourcerecarray,
    save_flows=True,
    print_flows=True,
    filename=f"{gwt_name}.ssm"
)

#%% CNC
# stress_period_data = []
# col = 0
# cnc = np.zeros(nrow)
# cnc[13:25] = 1.0
# for layer in [0, 1]:
#     for row, conc in enumerate(cnc):
#         stress_period_data.append([layer, row, col, conc])

# gwt_cnc = flopy.mf6.ModflowGwtcnc(gwt,stress_period_data=stress_period_data)

#%% ADV
adv = flopy.mf6.ModflowGwtadv(
    gwt,
    scheme="UPSTREAM",
)


#%% DISP
dispersivity = 10
transverse_horizontal_dispersivity = dispersivity * 0.01
transverse_vertical_dispersivity = dispersivity * 0.01

dsp = flopy.mf6.ModflowGwtdsp(
            gwt,
            xt3d_off=True,
            alh=dispersivity,
            ath1=transverse_horizontal_dispersivity,
            atv=transverse_vertical_dispersivity,
            filename=f"{gwt_name}.dsp",
        )

#%% MST
first_order_decay = None
porosity = 0.2

mst = flopy.mf6.ModflowGwtmst(
    gwt,
    porosity=porosity,
    first_order_decay=first_order_decay,
    filename=f"{gwt_name}.mst",
)

#%% OBSWELL
#lay = 0
#obs_dict = {
#    f'{gwt_name}.obs.csv':
#    [(
#        'concentration',
#        concentration_name,
#        (lay, nrow // 2, ncol - 2)
#     )
#    ]
#}
#flopy.mf6.ModflowUtlobs(
#    gwt, print_input=False, continuous=obs_dict
#)


#%% Transport OC
oc_gwt = flopy.mf6.ModflowGwtoc(
    gwt,
    budget_filerecord=f"{gwt_name}.cbb",
    concentration_filerecord=f"{gwt_name}.ucn",
    concentrationprintrecord=[
        ("COLUMNS", 10, "WIDTH", 15, "DIGITS", 10, "GENERAL")
    ],
    saverecord=[("CONCENTRATION", "ALL"),
                ("BUDGET", "ALL")
                ],
    printrecord=[("CONCENTRATION", "ALL"),
                 ("BUDGET", "ALL")
                    ],
)

#%% GWF-GWT Exchange
flopy.mf6.ModflowGwfgwt(
    sim,
    exgtype="GWF6-GWT6",
    exgmnamea=gwf_name,
    exgmnameb=gwt_name,
    filename=f"{sim_name}.gwfgwt",
)

#%% Write SIM
sim.write_simulation()



#%% OUTPUT MF6 test
species = 'species'
path = './mf6/'
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
i = 0
conc2 = conc_all[i]

#conc[conc>35]=35
plt.pcolor(x,y,conc2[0,:,:],cmap='jet')
#cs=plt.contour(x,y,conc2[0,:,:]*1000,np.arange(0.0,1,0.1),color='b')
plt.colorbar()


#%%

mg = gwf.modelgrid
x = mg.xcellcenters
y = mg.ycellcenters

plt.figure(1,figsize=(20,12))
pht3d_path ='../ex10_pht3d'

### TOLU
plt.subplot(3,3,1)

fname = pht3d_path + "/PHT3D002.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(0.0,1.1,0.1),cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(0.0,1.1,0.1),colors='b',linewidths=0.3)


species = 'Tolu'
path = './.internal/component_models/'+species+'/'
ucn_file = path + f"{gwt_name}.ucn"
ucnobj = flopy.utils.HeadFile(ucn_file, text="CONCENTRATION")
c_rtmf6 = ucnobj.get_alldata()

csp=plt.contour(x,y,c_rtmf6[-1,0,:,:]*1000,np.arange(0.0,1.1,0.1),colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')


# eigene Legendenelemente
legend_lines = [
    Line2D([0], [0], color='b', lw=1, label='PHT3D'),
    Line2D([0], [0], color='k', lw=1, linestyle='--', label='RTMF6')
]

plt.legend(handles=legend_lines, loc=1,fontsize=16)

plt.title('Toluene (mmol/L)',fontsize=18)
#plt.xlabel('X (m)',fontsize=16)
plt.ylabel('Y (m)',fontsize=18)
plt.xticks([])
plt.yticks(fontsize=14)

### pH
plt.subplot(3,3,2)
fname = pht3d_path + "/PHT3D021.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:],np.arange(6.46,6.9,0.04),cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:],np.arange(6.46,6.9,0.04),colors='b',linewidths=0.3)


pH = np.load('./pH.npy')

csp=plt.contour(x,y,pH[0,:,:],np.arange(6.46,6.9,0.04),colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')

plt.title('pH',fontsize=18)
#plt.xlabel('X (m)',fontsize=16)
#plt.ylabel('Y (m)',fontsize=18)
plt.xticks([])
plt.yticks([])


### CA
plt.subplot(3,3,3)
fname = pht3d_path + "/PHT3D006.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(2.6,4.6,0.2),cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(2.6,4.6,0.2),colors='b',linewidths=0.3)


species = 'Ca'
path = './.internal/component_models/'+species+'/'
ucn_file = path + f"{gwt_name}.ucn"
ucnobj = flopy.utils.HeadFile(ucn_file, text="CONCENTRATION")
c_rtmf6 = ucnobj.get_alldata()

csp=plt.contour(x,y,c_rtmf6[-1,0,:,:]*1000,np.arange(2.6,4.6,0.2),colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')



plt.title('Ca (mmol/L)',fontsize=18)
#plt.xlabel('X (m)',fontsize=16)
#plt.ylabel('Y (m)',fontsize=18)
plt.xticks([])
plt.yticks([])



### S(6)
plt.subplot(3,3,4)
fname = pht3d_path + "/PHT3D016.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(0.0,4.5,0.5),cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(0.0,4.5,0.5),colors='b',linewidths=0.3)


SO4 = np.load('./SO4.npy')

csp=plt.contour(x,y,SO4[0,:,:]*1000,np.arange(0.0,4.5,0.5),colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')

plt.title('SO4 (mmol/L)',fontsize=18)
#plt.xlabel('X (m)',fontsize=16)
plt.ylabel('Y (m)',fontsize=18)
plt.yticks(fontsize=14)
plt.xticks([])

### S(-2)
plt.subplot(3,3,5)
fname = pht3d_path + "/PHT3D017.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(0.4,3.5,0.6),cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(0.4,3.5,0.6),colors='b',linewidths=0.3)


HS = np.load('./HS.npy')

csp=plt.contour(x,y,HS[0,:,:]*1000,np.arange(0.4,3.5,0.6),colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')

plt.title('HS (mmol/L)',fontsize=18)
#plt.xlabel('X (m)',fontsize=16)
#plt.ylabel('Y (m)',fontsize=18)
plt.xticks([])
plt.yticks([])




### Fe(2)
plt.subplot(3,3,6)
fname = pht3d_path + "/PHT3D010.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:]*1000e3,[1,5,50,70,150,300,350],cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:]*1000e3,[1,5,50,70,150,300,350],colors='b',linewidths=0.3)


species = 'Fe'
path = './.internal/component_models/'+species+'/'
ucn_file = path + f"{gwt_name}.ucn"
ucnobj = flopy.utils.HeadFile(ucn_file, text="CONCENTRATION")
c_rtmf6 = ucnobj.get_alldata()

csp=plt.contour(x,y,c_rtmf6[-1,0,:,:]*1000e3,[1,5,50,70,150,300,350],colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')



plt.title('Fe (umol/L)',fontsize=18)
#plt.xlabel('X (m)',fontsize=16)
#plt.ylabel('Y (m)',fontsize=18)
plt.xticks([])
plt.yticks([])


## Calcite
plt.subplot(3,3,7)
fname = pht3d_path + "/PHT3D027.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:],np.arange(3.331,3.35,0.004),cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:],np.arange(3.331,3.35,0.004),colors='b',linewidths=0.3)


Calcite = np.load('./Calcite.npy')

csp=plt.contour(x,y,Calcite[0,:,:],np.arange(3.331,3.35,0.004),colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')


plt.title('Calcite (mol/L_w)',fontsize=18)
plt.xlabel('X (m)',fontsize=16)
plt.ylabel('Y (m)',fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)



## Goethite
plt.subplot(3,3,8)
fname = pht3d_path + "/PHT3D028.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(1,5,1),cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(1,5,1),colors='b',linewidths=0.3)


Goethite = np.load('./Goethite.npy')

csp=plt.contour(x,y,Goethite[0,:,:]*1000,np.arange(1,5,1),colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')


plt.title('Goethite (mmol/L_w)',fontsize=18)
plt.xlabel('X (m)',fontsize=16)
#plt.ylabel('Y (m)',fontsize=18)
plt.xticks(fontsize=14)
plt.yticks([])


## Pyrite
plt.subplot(3,3,9)
fname = pht3d_path + "/PHT3D029.UCN"
ucnobj = flopy.utils.UcnFile(fname, precision='auto')
times = ucnobj.get_times()
c_pht3d= ucnobj.get_alldata()
ucnobj.close()

cs=plt.contourf(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(1,5,1),cmap='Blues')
plt.colorbar()

csl=plt.contour(x,y,c_pht3d[-1,0,:,:]*1000,np.arange(1,5,1),colors='b',linewidths=0.3)


Pyrite = np.load('./Pyrite.npy')

csp=plt.contour(x,y,Pyrite[0,:,:]*1000,np.arange(1,5,1),colors='k',linestyles='dashed')
plt.clabel(csp,fmt='%1.2f')


plt.title('Pyrite (mmol/L_w)',fontsize=18)
plt.xlabel('X (m)',fontsize=16)
#plt.ylabel('Y (m)',fontsize=18)
plt.xticks(fontsize=14)
plt.yticks([])


plt.tight_layout()



plt.savefig('./PHT3D_RTMF6_compare.png')

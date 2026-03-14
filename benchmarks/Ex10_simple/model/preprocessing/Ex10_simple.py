#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 08:34:42 2026 in the year of the Lord

@author: janek
"""

import flopy
import numpy as np
import matplotlib.pyplot as plt
#%% units and names
length_units = 'meters'
time_units = 'days'
sim_name = 'ex10_simple'
gwf_name = f'gwf_{sim_name}'
gwt_name = f'gwt_{sim_name}'
sim_ws = '.../mf6'
concentration_name = 'concentration' # name for concentration
rtmf6_sol_number_name = 'rtmf6_sol_number' # solution number of PHREEQC solution


sim = flopy.mf6.MFSimulation(sim_name=sim_name, sim_ws=sim_ws)

nper = 1
perlen = 500
nstp = 50

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
nlay = 2  # Number of layers
Lx = 0.08 #m Length of domain in x-direction (ncol * delr)
ncol = 80 # Number of columns
nrow = 40  # Number of rows
delr = 2.5 #
delc = 1.25
top = 10
botm = np.array([5,0])
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
k11 = 10.0  # Horizontal hydraulic conductivity ($m/d$)
k33 = k11  # Vertical hydraulic conductivity ($m/d$)
icelltype = 0 # saturated thickness varies with computed head when head is below the cell top


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
# q = 0 #injection rate m3/d
# concentration = 0  # will be replaced
# rtmf6_sol_number = 0  # use solution from phreeqcrm/advect.pqi
# wel_spd = [[(0, 0, 0), q, concentration, rtmf6_sol_number]] # well stress period data
# auxiliary = [
#     concentration_name, # name for concentration
#     rtmf6_sol_number_name # solution number of PHREEQC solution
# ]
# wel = flopy.mf6.ModflowGwfwel(
#         gwf,
#         stress_period_data=wel_spd,
#         save_flows=True,
#         auxiliary=auxiliary,
#         pname='wel',
#         filename=f"{gwf_name}.wel"
#     )


#%% CHD
headup = 5
headdwn = 3
chd_spd = []

sourcec = np.zeros(nrow)
sourcec[13:25]=1.0

auxiliary = [
    concentration_name, # name for concentration
    rtmf6_sol_number_name # solution number of PHREEQC solution
]

for i in range(nrow):
  chd_spd.append([(0, i, 0), headup,sourcec[i],sourcec[i]])
  chd_spd.append([(1, i, 0), headup,sourcec[i],sourcec[i]])
  chd_spd.append([(0, i, ncol-1), headdwn,sourcec[i],sourcec[i]])
  chd_spd.append([(1, i, ncol-1), headdwn,sourcec[i],sourcec[i]])

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
gwt_ic = flopy.mf6.ModflowGwtic(
    gwt,
    strt=0,  # rtmf6 solution number
    filename=f"{gwt_name}.ic")

#%% Transport SSM
sourcerecarray = ['CHD', 'aux', concentration_name]

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
dispersivity = 2.0
transverse_horizontal_dispersivity = dispersivity * 0.2
transverse_vertical_dispersivity = dispersivity * 0.1

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
porosity = 0.3

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

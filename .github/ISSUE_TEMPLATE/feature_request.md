---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: enhancement
assignees: ''
type: Feature

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**Provide a minimal rtm6 model that could use your feature**

If possible, please provide a minimal rtmf6 model that runs. If should be designed  in way that it would be able ti use  your requested feature if this feature existed. The model should show different results if the new, not yet existing f feature would be enabled.  

Ideally this model should:

1. Have a minimal number of cells and layers. Sometimes even a two-cell model may do.
2. Have only boundary conditions (BCs) that are needed for the new feature. Make these BCs as simple as possible.
3. Have a minimal chemical reactions. If reactions are not important to demonstrate  the new feature, consider using only a tracer. If reactions are needed to show the behavior of the new feature,  consider using a NaCl solution or a similarly simple setup as long as it sufficient.   
4. Include the PHREEQC database you use, if you modified this database.

Please attach all model files in zipped file to this issue. If this file is to big, please provide download link. Alternatively to actualy attaching all model files, you may provide flopy scripts that can create all or some MODFLOW 6 input files. Typically,  PHREEQC input files and rtmf6-specific input files should be small enough to be attached here.

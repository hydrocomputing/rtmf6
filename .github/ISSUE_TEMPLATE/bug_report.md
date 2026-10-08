---
name: Bug report
about: Create a report to help us improve rtmf6
title: ''
labels: bug
assignees: ''
type: Bug

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**

Please provide a minimal model that reproduces the behavior that:

1. Has a minimal number of cells and layers. Sometimes even a two-cell model may do.
2. Has only boundary conditions that are needed to reproduce the bug. Make them as simple as possible.
3. Has a minimal chemical reactions. If reactions are not important to demonstrate  the bug, consider using only a tracer. If reactions are needed to show the buggy behavior consider using a NaCl solution or a similarly simple setup as long as it sufficient to trigger the buggy model behavior.   
4. Include the PHREEQC database you use, if you modified this database.

Please attach all model files in zipped file to this issue. If this file is to big, please provide download link. Alternatively to actualy attaching all model files, you may provide flopy scripts that can create all or some MODFLOW 6 input files. Typically,  PHREEQC input files and rtmf6-specific input files should be small enough to be attached here.

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
 - Operating system (e.g. macOS, Linux, Windows) and version
 - rtfm6 version
- MODFLOW 6 version
- PhreeqcRM version
 - Installation method (e.g. pip, conda, Pixi, cloned repo etc.)

 **Additional context**
Add any other context about the problem here.

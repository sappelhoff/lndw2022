# lndw2022

- lndw = "Lange Nacht der Wissenschaften" (German for "Long Night of the Sciences")
- see: https://www.langenachtderwissenschaften.de/en/

This repository contains code for the LNdW 2022 at the Max Planck Institute for Human Development (MPIB)
for the Adaptive Memory and Decision Making group (AMD).
In 2022, the LNdW will happen on the 2nd of July.

The repository is hosted on GitHub: https://github.com/sappelhoff/lndw2022
And it is mirrored on the ARC GitLab (internal only): https://arc-git.mpib-berlin.mpg.de/appelhoff/lndw2022

# General overview

The general plan for this presentation is by Bernhard Spitzer.

We will show visitors a brain computer interface (BCI) and have a discussion about "mind reading".

- A participant from the AMD lab will wear an EEG cap and we record data live and show it on the screen
- Furthermore, a screen window (via PsychoPy) will be shown in one of two possible colors
- When commanded, the participant will either:
    - (i) close their eyes and not move them
    - (ii) close their eyes and move them behind closed eyelids
- In the EEG data, (i) will register in high alpha power (frequencies 8-12 Hz) in posterior channels,
  whereas (ii) will register in high alpha power in frontal channels
- Internally, we continuously compute the difference between posterior and frontal average alpha power
  and take the resulting "sign" to flip the color of the PsychoPy window between the two possible colors
  (depending on the sign of our computations)
- To visitors it will seem as if the participant thinks about a certain color, and the BCI can "read
  that color" from their mind, whereas in truth -- we are using a simple "trick" to achieve this.
- After a short presentation of this, we debrief the visitors, explain the "trick" and enter into a
  discussion of what **is** possible via BCIs, and what is (currently) not easily possible.

# Required hardware

- A Windows laptop (minimum 2 USB-A slots: one for the BrainVision Recorder dongle, one for connecting to the BrainAmp)
- A BrainAmp + 2x cable (fibreoptics, ribbon)
- A power pack + cable + charger
- A controlbox + USB cable
- 4 batteries + charger
- A set of 32 electrodes
- A set of REF + GND electrodes
- A BUA (BrainVision USB adapter) + USB cable
- A "signal tester" box + cable (ribbon)

And additionally:

- One more laptop and big screen for showing the presentation
- A power strip to plug all the devices

# Software dependencies and installation

First, if you don't have it installed already, download miniconda:
https://docs.conda.io/en/latest/miniconda.html

Then install mamba into your base environment.
From your conda prompt or shell, run: `conda install -c conda-forge mamba --yes`

Then you can use the `environment.yml` file in this repository to install the
remaining dependencies: `mamba env create -f environment.yml`

Running `conda activate lndw2022` will then provide you with an appropriate environment.

The most important dependencies are:

- `pylsl` for getting the live EEG data
- `mne` for processing the EEG data
- `psychopy` for showing a window and switching its color

Furthermore, you will need the following software:

- BrainVision Recorder (plus license dongle)
- The BrainVision Recorder Remote Data Access LabStreamingLayer (LSL) client: https://github.com/brain-products/LSL-BrainVisionRDA
- Any presentation software (to show the presentation during the LNdW)

# Running the project

1. In the BrainVision Recorder settings, make sure Remote Data Access (RDA) is **enabled** (see manual)
1. Setup the hardware (see manual) with the laptop
    1. Set the sampling frequency in BrainVision Recorder to 250 Hz
    1. Use the "green" slot for the 32 electrodes
1. Start recording data, run the RDA LSL client and "link" it to stream the data live to the local network
1. From a command line prompt, run `python main.py` (after activating the conda environment, see above)

# Files in this repository

- `README.md` --> the README file you are reading
- `main.py` --> the main script for running the project
- `environment.yml` --> a list of most of the software dependencies
- `LICENSE` --> how the code and documentation in this project are licensed (but not the general idea)
- `.gitignore` --> which files to ignore in the version control via git
- `setup.cfg` --> configuration that is relevant when developing the code

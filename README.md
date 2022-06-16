# lndw2022

- lndw = "Lange Nacht der Wissenschaften" (German for "Long Night of the Sciences")
- see: https://www.langenachtderwissenschaften.de/en/

This repository contains code for the LNdW 2022 at the Max Planck Institute for Human Development (MPIB)
for the Adaptive Memory and Decision Making group (AMD).
In 2022, the LNdW will happen on the 2nd of July.

The repository is hosted on GitHub: https://github.com/sappelhoff/lndw2022

It is mirrored on the ARC GitLab (internal only): https://arc-git.mpib-berlin.mpg.de/appelhoff/lndw2022

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

**NOTE: The BCI can also be controlled in another way (see below)**

The list above describes what in `main.py` is defined as `SWITCH_TYPE="sign"`.
Instead, one can change to `SWITCH_TYPE="frontal boost"`.
In that case, the participant is supposed to have their eyes open and either:

- (i) focus on **not blinking**
- (ii) blinking several times without anyone noticing

Here the switch is "1" when the participant does not blink (frontal and posterior average alpha power are approximately equal), and "0" when the
participant blinks (frontal average alpha power is much higher than
posterior; see `FRONTAL_BOOST_FACTOR` in `main.py`).

Depending on the participant and training, one `SWITCH_TYPE` may work better
than the other one.

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

See also the `setup_drawing` directory.

![Image](setup_drawing/lndw_setup_drawing.png "Hardware setup")

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
1. From a command line prompt, run `python -u main.py` (after activating the conda environment, see above)
1. You can stop the program by clicking on the colorful PsychoPy window and pressing "escape"
   (or interrupt it by pressing ctrl+c in the command line prompt)

# Testing data

In the `testing_data/` directory you will find data to play around with for optimizing the BCI.
The `offline_test` data contains four markers:

- `open_relax`
- `open_blink`
- `closed_relax`
- `closed_blink`

where the first factor before the `_` refer to the state of the eyes, and the second factor
(after the `_`) refers to the activity.
After each marker, there are at least 8 seconds of data during which the respective activity was
performed by the test session participant.

# Files in this repository

- `README.md` --> the README file you are reading
- `main.py` --> the main script for running the project
- `environment.yml` --> a list of most of the software dependencies
- `LICENSE` --> how the code and documentation in this project are licensed (but not the general idea)
- `.gitignore` --> which files to ignore in the version control via git
- `setup.cfg` --> configuration that is relevant when developing the code
- `testing_data/offline_test.*` --> a BrainVision file triplet (`.eeg`, `.vhdr`, `.vmrk`) for testing offline
- `testing_data/analyze_testing_data.py` --> script for exploring the testing data
- `setup_drawing/lndw_setup_*` --> three files that show the hardware setup
- `slides/*.pptx` --> the presentation slide show for the evening

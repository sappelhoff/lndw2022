"""Setup BCI for Long Night of the Sciences (LNdW) 2022.

For more information, see the `README.md` file and follow the steps from the
"Running the project" section.

"""
# %%
# Imports
import time
from pathlib import Path

import mne
import numpy as np
import matplotlib
from psychopy import event, visual
from pylsl import StreamInlet, resolve_stream

# %%
# Settings
# Width and height of the PsychoPy window in pixels
WIN_SIZE_PIXELS = (600, 300)

# how many seconds of data to get per iteration
# (this determines the "update" speed)
SECONDS_TO_GET = 2

# Low and high boundary over which frequencies to average
FREQS = [8, 14]

# Over which channels to average
POSTERIOR_CHS = ["P7", "P3", "P4", "P8", "O1", "Oz", "O2"]
FRONTAL_CHS = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8"]

# Factors by which to scale either posterior or fronal average power
SCALE_POSTERIOR = 1
SCALE_FRONTAL = 1

# Which frequency decomposition to use: "multitaper" or "welch"
FREQ_DECOMP_METHOD = "welch"

# How to implement the BCI: Use "SWITCH_TYPE"
# (generally: high posterior power = blue, high frontal power = red)
# ----------
# "sign" means take the difference between frontal and posterior average alpha power
# ----------
# "frontal boost" means switch is 1 (=blue) unless frontal is at least "x" times higher
# than posterior: 0 (=red), where FRONTAL_BOOST_FACTOR below controls the "x"
# ----------
# "continuous" takes log10(posterior / frontal) and colors the window continuously
# from red over purple to blue
SWITCH_TYPE = "sign"

# if "SWITCH_TYPE" is "frontal boost", what should "x" be (see above); else is ignored
FRONTAL_BOOST_FACTOR = 2

# if "SWITCH_TYPE" is "continuous", control which value "log10(posterior / frontal)"
# corresponds to the extreme blue or extreme red
# good defaults are -1.5 and 1.5, which means total blue if posterior is about 30 times
# higher than frontal and vice versa for total red
# NOTE: you could use unsymmetric limits like [-1.5, 1] --> this would make it "easier"
# for the window to become red again
VLIMS = [-1.5, 1.5]

# %%
# Create the information about the data we expect
# channel names correspond to "green" slot of electrodes in the control box
bvef = Path("./electrode_cap/AC-32.bvef").resolve()
montage = mne.channels.read_custom_montage(bvef)
ch_names = montage.ch_names
ch_names.remove("GND")
ch_names.remove("REF")
assert len(ch_names) == 32, "expected exactly 32 channels"
sfreq = 100
ch_types = ["eeg"] * len(ch_names) + ["misc"]
ch_names += ["marker"]  # there is an additional marker channel inserted by LSL

info = mne.create_info(ch_names, sfreq, ch_types)

# %%
# EEG Settings
# How many samples to pull: sfreq = 1 second (Hz)
n_samples = sfreq * SECONDS_TO_GET

# How many seconds to wait until data is there
max_wait = (n_samples / sfreq) * 2

# Default "events" that we will use for each incoming data
events = np.expand_dims(np.array([0, 1, 1]), axis=0)

# Later on, we will only be interested in EEG channels
picks = mne.pick_types(info, eeg=True)
info = mne.pick_info(info, picks)

# The frequencies we want to average over (alpha power)
fmin = FREQS[0]
fmax = FREQS[1]

# Needed for psd_welch
n_fft = n_samples
assert n_fft <= n_samples, "n_fft must be <= n_samples"

# We will subtract power from posterior and frontal channels
picks_posterior = mne.pick_channels(info.ch_names, POSTERIOR_CHS)
picks_frontal = mne.pick_channels(info.ch_names, FRONTAL_CHS)

# %%
# Psychopy window settings
# The colors that are going to be switched: RGB 0-1
# For binary switching (red/blue): "sign" or "frontal boost"
c_red = (0.5, 0, 0)
c_blue = (0, 0, 0.5)

# ... or for continuous switching (red to blue): "continuous"
cm_r2b = matplotlib.colors.LinearSegmentedColormap.from_list("red2blue", ["r", "b"])
cnorm = matplotlib.colors.Normalize(vmin=VLIMS[0], vmax=VLIMS[1])
cpick = matplotlib.cm.ScalarMappable(norm=cnorm, cmap=cm_r2b)
cpick.set_array([])

# Opening a window
# NOTE: We don't define a monitor so this will raise an expected and benign warning
win = visual.Window(
    color=(0.5, 0.5, 0.5),  # starting with gray color
    fullscr=False,
    size=WIN_SIZE_PIXELS,  # pixels
    colorSpace="rgb1",  # RGB scaled from 0 to 1
)

# %%
# Connect to the BrainVision Recorder RDA (Remote Data Access)
# (needs to be switched on in BrainVision Recorder settings)
streams = resolve_stream("type", "EEG")
assert len(streams) == 1, f"expected one stream, but found: {len(streams)}"
inlet = StreamInlet(streams[0])

msg = "Is the sampling rate in BrainVision Recorder correct?"
assert inlet.info().nominal_srate() == sfreq, msg

msg = "Is the number of channels in BrainVision Recorder correct?"
assert inlet.info().channel_count() == len(ch_names), msg
# %%
# Begin the loop

# First clear all present not-yet-pulled samples from the buffer
_ = inlet.flush()

print(
    "Starting the program. Click on the PsychoPy window and press 'escape' to quit."
    "\n------------------------------"
)
while True:

    # Pull a chunk of data: `chunk` is a list of lists, each list corresponding to a
    # sample with an associated timestamp. Each list is of length n_channels + 1, in
    # order as defined in BrainVision Recorder workspace setup. The last channel ("+1")
    # is a marker channel that can be ignored.
    chunk, _ = inlet.pull_chunk(timeout=max_wait, max_samples=n_samples)

    # Measure time that this iteration takes
    tstart_ns = time.perf_counter_ns()

    # Then convert to mne Epochs
    data = np.vstack(chunk).T
    epochs = mne.EpochsArray(data[picks][np.newaxis], info, events, verbose=0)

    # Calculate power spectrum, ´psds´ is of shape (n_epochs, n_channels, n_freqs)
    if FREQ_DECOMP_METHOD == "welch":
        psds, _ = mne.time_frequency.psd_welch(
            epochs, fmin, fmax, n_fft=n_fft, average="mean", verbose=0
        )
    elif FREQ_DECOMP_METHOD == "multitaper":
        psds, _ = mne.time_frequency.psd_multitaper(epochs, fmin, fmax, verbose=0)
    else:
        raise ValueError(f"Unknown FREQ_DECOMP_METHOD: {FREQ_DECOMP_METHOD}")

    # Separatetly average power for posterior and frontal channels
    power_posterior = np.mean(psds[0, picks_posterior, :])
    power_frontal = np.mean(psds[0, picks_frontal, :])

    # Scale the powers depending on settings
    power_posterior *= SCALE_POSTERIOR
    power_frontal *= SCALE_FRONTAL

    if SWITCH_TYPE == "sign":
        # Take the sign of the difference: this is our "color switch"
        # 0 if frontal > posterior (=red)
        # 1 if posterior > frontal (=blue)
        # (if equal, defaults to 0)
        switch = int((1 + np.sign(power_posterior - power_frontal)) / 2)
    elif SWITCH_TYPE == "frontal boost":
        # 1 by default (=blue)
        # 0 if frontal is much much higher than posterior (=red)
        switch = 0 if power_frontal > (FRONTAL_BOOST_FACTOR * power_posterior) else 1
    elif SWITCH_TYPE == "continuous":
        # continuous measure (rather than 0 or 1)
        # frontal > posterior = more red
        # posterior > frontal = more blue
        # (if equal = purple)
        try:
            switch = np.log10(power_posterior / power_frontal)
        except ZeroDivisionError:
            switch = np.inf
    else:
        raise ValueError(f"Unknown SWITCH_TYPE: {SWITCH_TYPE}")

    print(
        f"State of switch: {switch}    "
        f"(posterior vs frontal: {power_posterior:.1f} vs {power_frontal:.1f})"
    )

    # Switch the window color
    # ... need to flip twice because we change the window *background*
    if SWITCH_TYPE == "continuous":
        # continuous color
        win.color = cpick.to_rgba(switch)[:3]
    else:
        # binary color red or blue
        win.color = c_blue if switch else c_red
    _ = win.flip()
    _ = win.flip()

    # Check if somebody pressed escape. If yes, exit gracefully
    keys = event.getKeys(keyList=["escape"])
    if keys:
        print("\n    >>>> Registered an 'escape' key ... terminating program.\n")
        win.close()
        inlet.close_stream()
        break

    # If this iteration took too long, we need to flush the buffer,
    # so that we always have fresh data
    tstop_ns = time.perf_counter_ns()
    titer_s = (tstop_ns - tstart_ns) * 1e-9
    if titer_s > (n_samples / sfreq):
        dropped_samples = inlet.flush()
        print(
            f"\n    >>>> Iteration took {titer_s} s ... clearing buffer to start new."
            f"\n    >>>> (dropped {dropped_samples} samples)\n"
        )

    # Start next iteration and repeat until the end
    ...

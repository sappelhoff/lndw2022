"""Setup BCI for Long Night of the Sciences (LNdW) 2022.

For more information, see the `README.md` file and follow the steps from the
"Running the project" section.

"""
# %%
# Imports
import time

import mne
import numpy as np
from psychopy import event, visual
from pylsl import StreamInlet, resolve_stream

# %%
# Create the information about the data we expect
# channel names correspond to "green" slot of electrodes in the control box
# fmt: off
ch_names = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FT9", "FC5", "FC1", "FC2", "FC6",
    "FT10", "T7", "C3", "Cz", "C4", "T8", "CP5", "CP1", "CP2", "CP6", "TP9", "P7",
    "P3", "Pz", "P4", "P8", "TP10", "O1", "Oz", "O2"]
# fmt: on
sfreq = 250
ch_types = ["eeg"] * len(ch_names) + ["misc"]
ch_names += ["marker"]  # there is an additional marker channel inserted by LSL

info = mne.create_info(ch_names, sfreq, ch_types)

# Add standard 10-20 positions: "easycap-M1" corresponds to the acticap-64ch-standard2
# caps that we use in the lab
info.set_montage("easycap-M1")

# %%
# EEG Settings
# how many samples to pull: sfreq = 1 second (Hz)
n_samples = sfreq

# how many seconds to wait until data is there
max_wait = (n_samples / sfreq) * 5

# default "events" that we will use for each incoming data
events = np.expand_dims(np.array([0, 1, 1]), axis=0)

# Later on, we will only be interested in EEG channels
picks = mne.pick_types(info, eeg=True)
info = mne.pick_info(info, picks)

# The frequencies we want to average over (alpha power)
fmin = 8
fmax = 12

# needed for psd_welch
n_fft = 128
assert n_fft < n_samples, "n_fft must be <= n_samples"

# We will subtract power from posterior and frontal channels
posterior_chs = ["P7", "P3", "P4", "P8", "O1", "Oz", "O2"]
frontal_chs = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8"]
picks_posterior = mne.pick_channels(info, posterior_chs)
picks_frontal = mne.pick_channels(info, frontal_chs)

# %%
# Psychopy window settings
# The colors that are going to be switched
c0 = (1, 0, 0)
c1 = (0, 0, 1)

# Opening a window
# NOTE: We don't define a monitor so this will raise an expected and benign warning
win = visual.Window(
    color=c0,
    fullscr=False,
    size=(300, 150),  # pixels
)

# %%
# Connect to the BrainVision Recorder RDA (Remote Data Access)
# (needs to be switched on in BrainVision Recorder)
streams = resolve_stream("type", "EEG")
assert len(streams) == 1, f"expected one stream, but found: {len(streams)}"
inlet = StreamInlet(streams[0])

# %%
# Begin the loop

# first clear all present not-yet-pulled samples from the buffer
_ = inlet.flush()

# end this program by clicking on the psychopy window and pressing "escape"
finished = False
while not finished:

    # measure time that this iteration takes
    tstart_ns = time.perf_counter_ns()

    # pull a chunk of data: `chunk` is a list of lists, each list corresponding to a
    # sample with an associated timestamp. Each list is of length n_channels + 1, in
    # order as defined in BrainVision Recorder workspace setup. The last channel ("+1")
    # is a marker channel that can be ignored.
    chunk, timestamps = inlet.pull_chunk(timeout=max_wait, max_samples=n_samples)

    # Then convert to mne Epochs
    data = np.vstack(chunk).T
    epochs = mne.EpochsArray(data[picks][np.newaxis], info, events, verbose=0)

    # Calculate power spectrum, ´psds´ is of shape (n_epochs, n_channels, n_freqs)
    psds, freqs = mne.time_frequency.psd_welch(
        epochs, fmin, fmax, n_fft=n_fft, average="mean", verbose=0
    )

    # Separatetly average power for posterior and frontal channels
    power_posterior = np.mean(psds[0, picks_posterior, :])
    power_frontal = np.mean(psds[0, picks_frontal, :])

    # Take the sign of the difference: this is our "color switch"
    # This can be zero or 1 and defaults to 0, if power is equal in
    # posterior and frontal channels
    switch = int((1 + np.sign(power_posterior - power_frontal)) / 2)
    print(
        f"State of switch: {switch}    "
        f"(posterior vs frontal: {power_posterior:.1f} vs {power_frontal:.1f})"
    )

    # switch the window color
    # here we need to flip twice because we change the window background color
    c = c1 if switch else c0
    win.color = c
    _ = win.flip()
    _ = win.flip()

    # Check if somebody pressed escape. If yes, exit gracefully
    keys = event.getKeys(keyList=["escape"])
    if keys:
        print("\n    >>>> Registered an 'escape' key ... terminating program.\n")
        win.close()
        inlet.close_stream()
        finished = True

    # If this iteration took too long, we need to flush the buffer,
    # so that we always have fresh data
    tstop_ns = time.perf_counter_ns()
    titer_s = tstop_ns - tstart_ns * 1e-9
    if titer_s > (n_samples / sfreq):
        dropped_samples = inlet.flush()
        print(
            f"\n    >>>> Iteration took {titer_s} s ... clearing buffer."
            f"\n    >>>> (dropped {dropped_samples} samples)\n"
        )

    # Start next iteration and repeat until the end
    ...

"""Setup BCI for Long Night of the Sciences (LNdW) 2022.

For more information, see the `README.md` file and follow the steps from the
"Running the project" section.

buffer len: 1s
bandpass between 1Hz and 30Hz

"""
# %%
# Imports
import mne
import numpy as np
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
sfreq = 250.0
ch_types = ["eeg"] * len(ch_names) + ["misc"]
ch_names += ["marker"]  # there is an additional marker channel inserted by LSL

info = mne.create_info(ch_names, sfreq, ch_types)

# Add standard 10-20 positions: "easycap-M1" corresponds to the acticap-64ch-standard2
# caps that we use in the lab
info.set_montage("easycap-M1")


# %%
# Connect to the BrainVision Recorder RDA (Remote Data Access)
# (needs to be switched on in BrainVision Recorder)
streams = resolve_stream("type", "EEG")
assert len(streams) == 1
inlet = StreamInlet(streams[0])

# clears all present not-yet-pulled samples from the buffer
inlet.flush()

# pull a chunk of data: `chunk` is a list of lists, each list corresponding to a sample
# with an associated timestamp. Each list is of length n_channels + 1, in order as
# defined in BrainVision Recorder workspace setup. The last channel ("+1") is a
# marker channel that can be ignored.
chunk, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=1000)

# Then convert to mne Epochs
info = 1
n_samples = 1000
wait_time = n_samples * 5.0 / info["sfreq"]
samples, _ = inlet.pull_chunk(max_samples=n_samples, timeout=wait_time)
data = np.vstack(samples).T

events = np.expand_dims(np.array([0, 1, 1]), axis=0)
picks = mne.io.pick._picks_to_idx(info, "eeg", "all", exclude=())
info = mne.io.pick.pick_info(info, picks)
epochs = mne.EpochsArray(data[picks][np.newaxis], info, events)

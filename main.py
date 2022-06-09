"""Setup BCI for Long Night of the Sciences (LNdW) 2022.

For more information, see the `README.md` file.

sfreq: 250hz
buffer len: 1s
bandpass between 1Hz and 30Hz

"""
from pylsl import StreamInlet, resolve_stream
import mne
import numpy as np

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
wait_time = n_samples * 5. / info['sfreq']
samples, _ = inlet.pull_chunk(max_samples=n_samples, timeout=wait_time)
data = np.vstack(samples).T

events = np.expand_dims(np.array([0, 1, 1]), axis=0)
picks = mne.io.pick._picks_to_idx(info, "eeg", 'all', exclude=())
info = mne.io.pick.pick_info(info, picks)
epochs = mne.EpochsArray(data[picks][np.newaxis], info, events)

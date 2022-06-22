"""Analyze and explore the testing data.

For more information, see the `README.md` file and the "testing data" section.
"""

# %%
# Imports
import json
import time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import mne
import numpy as np
from psychopy import visual

# %%
# Settings
vhdr = Path("./offline_test.vhdr")
SECONDS_TO_GET = 2
assert SECONDS_TO_GET <= 8, "Longest common epoch length in test data is 8s."

# Low and high boundary over which frequencies to average
FREQS = [8, 12]

FREQ_DECOMP_METHOD = "welch"

# %%
# Read data
# (TP10 is bad, but we can leave it included)
# NOTE: Perhaps the "eyes closed" event markers were accidentally exchanged (no idea)
# NOTE: offline_test2 may be a bad test set ...just use offline_test
raw = mne.io.read_raw_brainvision(vhdr)

# %%
# Get channel selections
posterior_chs = ["O1", "Oz", "O2"]  # ["P7", "P3", "P4", "P8", "O1", "Oz", "O2"]
frontal_chs = ["Fp1", "Fp2"]  # ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8"]
picks_posterior = mne.pick_channels(raw.ch_names, posterior_chs)
picks_frontal = mne.pick_channels(raw.ch_names, frontal_chs)

# %%
# Inspect the raw data
raw.plot(
    n_channels=len(raw.ch_names),
    clipping=None,
)

# %%
# obtain events and form epochs
event_id = {
    "Comment/blink_closed": 1,
    "Comment/blink_open": 2,
    "Comment/relax_closed": 3,
    "Comment/relax_open": 4,
}

events, event_id = mne.events_from_annotations(raw, event_id)

# Cut long epochs (at least 8 seconds) into smaller epochs
new_events = []
for ev in events:
    new_events += [ev]
    new_ev = ev[...]
    for i in range(int(8 / SECONDS_TO_GET) - 1):
        new_ev = new_ev + [int(raw.info["sfreq"] * SECONDS_TO_GET), 0, 0]
        new_events += [new_ev]

new_events = np.vstack(new_events)

event_id = {
    key.lstrip("Comment/").replace("_", "/"): val for key, val in event_id.items()
}

epochs = mne.Epochs(
    raw, new_events, event_id, tmin=0, tmax=SECONDS_TO_GET, baseline=None, preload=True
)
n_epos, n_channels, n_samples = epochs.get_data().shape

# %%
# Calculate power spectrum density
if FREQ_DECOMP_METHOD == "welch":
    psds, freqs = mne.time_frequency.psd_welch(
        epochs, FREQS[0], FREQS[1], n_fft=n_samples, average="mean", verbose=0
    )
elif FREQ_DECOMP_METHOD == "multitaper":
    psds, freqs = mne.time_frequency.psd_multitaper(
        epochs, FREQS[0], FREQS[1], verbose=0
    )
else:
    raise ValueError(f"Unknown FREQ_DECOMP_METHOD: {FREQ_DECOMP_METHOD}")

# %%
# Create continuous colormap for "continuous" switch method
cm1 = matplotlib.colors.LinearSegmentedColormap.from_list("red2blue", ["r", "b"])
cnorm = matplotlib.colors.Normalize(vmin=-1.5, vmax=1.5)
cpick = matplotlib.cm.ScalarMappable(norm=cnorm, cmap=cm1)
cpick.set_array([])

# %%
# Try out different switch methods
power_posterior = psds[:, picks_posterior].mean(axis=-1).mean(axis=-1)
power_frontal = psds[:, picks_frontal].mean(axis=-1).mean(axis=-1)

# sign
switch = (1 + np.sign(power_posterior - power_frontal)) / 2

# frontal boost
switch2 = [0 if i > 2 * j else 1 for i, j in zip(power_frontal, power_posterior)]

# continuous
switch3 = np.log10(power_posterior / power_frontal)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
ax1.plot(switch, label="switch=sign")
ax1.plot(switch2, label="switch=frontal boost")
ax1.plot(switch3, label="switch=continuous", color="black", lw=0.25)

for idot, dot in enumerate(switch3):
    ax1.plot(idot, dot, c=cpick.to_rgba(dot)[:3], marker="o")
ax1.legend()

ax2.plot(power_posterior, label="posterior")
ax2.plot(power_frontal, label="frontal")
ax2.plot(np.median(power_frontal) * epochs.events[:, -1], "k.")
ax2.set_title("black markers show levels: " + json.dumps(event_id))
ax2.legend()

# %%
# Get a visual experience of how "continuous" switch would look
win = visual.Window(
    color=cpick.to_rgba(0)[:3],
    fullscr=False,
    size=(600, 300),  # pixels
    colorSpace="rgb1",
)

for idot, dot in enumerate(switch3):
    win.color = cpick.to_rgba(dot)[:3]
    _ = win.flip()
    _ = win.flip()
    time.sleep(0.5)

win.close()

# %%

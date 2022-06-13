"""Analyze and explore the testing data.

For more information, see the `README.md` file and the "testing data" section.
"""

# %%
# Imports
from pathlib import Path

import mne
import numpy as np

# %%
# Settings
vhdr = Path("./offline_test.vhdr")
SECONDS_TO_GET = 2
assert SECONDS_TO_GET <= 8, "Longest common epoch length in test data is 8s."

# %%
# Read data
raw = mne.io.read_raw_brainvision(vhdr)
raw.info["bads"] = ["TP10", "CP1"]
raw.annotations.description

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

# %%


# %%

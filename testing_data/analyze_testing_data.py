"""Analyze and explore the testing data.

For more information, see the `README.md` file and the "testing data" section.
"""

# %%
# Imports
from pathlib import Path

import mne

# %%
# Settings
vhdr = Path("./offline_test.vhdr")


# %%
# Read data
raw = mne.io.read_raw_brainvision(vhdr)


# %%
raw.plot()

"""
Before and after running test.py script:
- test.py: unchanged
- file1.csv: changed
- file2.csv: deleted
- file3.csv: added
"""

import pandas as pd
import os

# Add 1 to file1.csv
df1 = pd.read_csv("runtime/file1.csv")
df1 = df1 + 1
df1.to_csv("runtime/file1.csv", index=False)

# Delete file2.csv
os.remove("runtime/file2.csv")

# Add file3.csv
pd.DataFrame({"v":["add"]}).to_csv("runtime/file3.csv", index=False)

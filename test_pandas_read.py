import pandas as pd
import os

# Test reading the HTML "XPT" file with pandas
xpt_file = "nhanes_data/1999-2000/diet/DBQ_1999_2000.xpt"

if os.path.exists(xpt_file):
    print(f"File exists: {xpt_file}")
    print(f"File size: {os.path.getsize(xpt_file)} bytes")

    try:
        print("Trying pd.read_sas...")
        df = pd.read_sas(xpt_file, format='xport')
        print(f"Success! DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:\n{df.head()}")
    except Exception as e:
        print(f"pd.read_sas failed: {e}")

    # Let's also check the first few bytes of the file
    with open(xpt_file, 'rb') as f:
        first_bytes = f.read(50)
        print(f"First 50 bytes: {first_bytes}")
        print(f"First 50 bytes as string: {first_bytes.decode('utf-8', errors='ignore')}")
else:
    print(f"File not found: {xpt_file}")
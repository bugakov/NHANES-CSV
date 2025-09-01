import os
import pandas as pd
import pyreadstat
from pathlib import Path
from sas7bdat import SAS7BDAT

def convert_xpt_to_csv():
    """Convert all .xpt files from downloads/xpt_files to .csv in csv folder"""

    # Define directories
    xpt_dir = Path("downloads/xpt_files")
    csv_dir = Path("csv")

    # Create csv directory if it doesn't exist
    csv_dir.mkdir(exist_ok=True)
    print(f"Created directory: {csv_dir}")

    # Counter for converted files
    converted_count = 0
    error_count = 0

    # Find all .xpt files in the directory
    xpt_files = list(xpt_dir.glob("*.xpt"))
    print(f"Found {len(xpt_files)} .xpt files to convert")

    for xpt_file in xpt_files:
        # Create the corresponding csv path
        csv_file = csv_dir / xpt_file.with_suffix('.csv').name

        print(f"Processing: {xpt_file.name} -> {csv_file.name}")

        try:
            # Try different methods to read the .xpt file
            df = None

            # Method 1: Try pandas read_sas
            try:
                print(f"Trying pandas read_sas for {xpt_file.name}...")
                df = pd.read_sas(str(xpt_file), format='xport')
                print(f"Successfully read with pandas, shape: {df.shape}")
            except Exception as e1:
                print(f"Pandas failed: {e1}")

                # Method 2: Try pyreadstat
                try:
                    print(f"Trying pyreadstat for {xpt_file.name}...")
                    df, meta = pyreadstat.read_xport(str(xpt_file))
                    print(f"Successfully read with pyreadstat, shape: {df.shape}")
                except Exception as e2:
                    print(f"Pyreadstat failed: {e2}")

                    # Method 3: Try sas7bdat
                    try:
                        print(f"Trying sas7bdat for {xpt_file.name}...")
                        with SAS7BDAT(str(xpt_file)) as f:
                            df = f.to_data_frame()
                        print(f"Successfully read with sas7bdat, shape: {df.shape}")
                    except Exception as e3:
                        print(f"Sas7bdat failed: {e3}")
                        raise Exception(f"All methods failed: pandas({e1}), pyreadstat({e2}), sas7bdat({e3})")

            if df is not None:
                # Save as .csv
                print(f"Saving to {csv_file}...")
                df.to_csv(str(csv_file), index=False)
                print(f"Successfully saved {csv_file}")
                converted_count += 1
            else:
                print(f"No data frame created for {xpt_file.name}")
                error_count += 1

        except Exception as e:
            print(f"Error converting {xpt_file.name}: {e}")
            error_count += 1

    print(f"\nConversion completed! {converted_count} files converted successfully, {error_count} errors.")

if __name__ == "__main__":
    convert_xpt_to_csv()
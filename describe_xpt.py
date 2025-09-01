import os
import pyreadstat
from pathlib import Path
from datetime import datetime

def describe_xpt_file(xpt_file_path):
    """Extract and return header information from an XPT file"""
    try:
        # Read the XPT file and get metadata
        df, meta = pyreadstat.read_xport(str(xpt_file_path))

        # Get file information
        file_size = os.path.getsize(xpt_file_path)
        file_name = xpt_file_path.name

        # Create description text
        description = []
        description.append(f"XPT File Description")
        description.append("=" * 50)
        description.append(f"File Name: {file_name}")
        description.append(f"File Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        description.append(f"Last Modified: {datetime.fromtimestamp(os.path.getmtime(xpt_file_path))}")
        description.append("")
        description.append(f"Dataset Information:")
        description.append(f"Number of Rows: {df.shape[0]:,}")
        description.append(f"Number of Columns: {df.shape[1]}")
        description.append("")
        description.append("Column Information:")
        description.append("-" * 30)

        # Add column details
        max_name_len = max(len(col) for col in meta.column_names) if meta.column_names else 0

        for i, col_name in enumerate(meta.column_names):
            # Get column type from DataFrame dtypes instead of meta.column_types
            col_type = str(df[col_name].dtype) if col_name in df.columns else "Unknown"
            col_label = meta.column_labels[i] if meta.column_labels and i < len(meta.column_labels) else ""

            # Format column information properly
            description.append(f"Column {i+1}: {col_name}")
            description.append(f"    Type: {col_type}")

            if col_label:
                description.append(f"    Label: {col_label}")
            description.append("")

        # Add additional metadata if available
        if hasattr(meta, 'file_encoding') and meta.file_encoding:
            description.append(f"File Encoding: {meta.file_encoding}")

        if hasattr(meta, 'table_name') and meta.table_name:
            description.append(f"Table Name: {meta.table_name}")

        if hasattr(meta, 'file_label') and meta.file_label:
            description.append(f"File Label: {meta.file_label}")

        # Add data preview
        description.append("")
        description.append("Data Preview (first 5 rows):")
        description.append("-" * 30)
        description.append(str(df.head()))
        description.append("")
        description.append("Data Types Summary:")
        description.append("-" * 20)
        description.append(str(df.dtypes))

        return "\n".join(description)

    except Exception as e:
        error_msg = f"Error processing {xpt_file_path.name}: {str(e)}"
        print(error_msg)
        return error_msg

def describe_all_xpt_files():
    """Process all XPT files in the downloads/xpt_files directory"""

    # Define directories
    xpt_dir = Path("downloads/xpt_files")

    if not xpt_dir.exists():
        print(f"Directory {xpt_dir} does not exist!")
        return

    # Find all .xpt files
    xpt_files = list(xpt_dir.glob("*.xpt"))
    print(f"Found {len(xpt_files)} .xpt files to process")

    # Counters
    processed_count = 0
    error_count = 0

    for xpt_file in xpt_files:
        print(f"Processing: {xpt_file.name}")

        try:
            # Extract description
            description = describe_xpt_file(xpt_file)

            # Create corresponding .txt file path
            txt_file = xpt_file.with_suffix('.txt')

            # Save description to .txt file
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(description)

            print(f"Saved description to: {txt_file.name}")
            processed_count += 1

        except Exception as e:
            print(f"Error processing {xpt_file.name}: {e}")
            error_count += 1

    print(f"\nProcessing completed!")
    print(f"Successfully processed: {processed_count} files")
    print(f"Errors: {error_count} files")
    print(f"Description files saved in: {xpt_dir}/")

if __name__ == "__main__":
    describe_all_xpt_files()

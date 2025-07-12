import os

def check_file_compatibility(filepath):
    """
    Checks if a file has the required Pelican metadata.

    Args:
        filepath (str): The path to the file.

    Returns:
        tuple: A tuple containing a boolean indicating compatibility
               and a list of missing metadata fields.
    """
    required_fields = {
        "Title",
        "Date",
        "Status",
        "Category",
        "Tags",
        "Author",
        "Summary"
    }
    
    present_fields = set()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 15:  # Only check the first 15 lines
                    break
                if ":" in line:
                    key = line.split(":", 1)[0].strip()
                    present_fields.add(key)
    except Exception as e:
        return False, [f"Error reading file: {e}"]

    missing_fields = required_fields - present_fields
    return not bool(missing_fields), list(missing_fields)

def main():
    """
    Main function to scan directories and report on file compatibility.
    """
    dirs_to_scan = [
        r"F:\Articles Temp",
        r"F:\Articles Ready"
    ]

    print("Starting Pelican compatibility check...")

    for directory in dirs_to_scan:
        print(f"\nScanning directory: {directory}")
        if not os.path.isdir(directory):
            print(f"  Error: Directory not found.")
            continue

        compliant_files = []
        non_compliant_files = {}

        for filename in os.listdir(directory):
            if filename.endswith(".md"):
                filepath = os.path.join(directory, filename)
                is_compliant, missing_info = check_file_compatibility(filepath)
                if is_compliant:
                    compliant_files.append(filename)
                else:
                    non_compliant_files[filename] = missing_info
        
        if compliant_files:
            print("\n--- Compliant Files ---")
            for f in compliant_files:
                print(f"  - {f}")

        if non_compliant_files:
            print("\n--- Non-Compliant Files ---")
            for f, missing in non_compliant_files.items():
                print(f"  - {f}: Missing {', '.join(missing)}")
    
    print("\nCheck complete.")

if __name__ == "__main__":
    main() 
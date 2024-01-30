# RegComp.py - for recursive comparison of registry subfolders
import winreg
import json
import base64

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8') # Convert binary data to base64 string
        return json.JSONEncoder.default(self, obj)


def read_registry(path):
    """
    Recursively reads the registry keys and values starting from the given path.
    :param path: The registry path to start reading from.
    :return: A dictionary representing the registry structure.
    """
    def recurse_keys(hkey, subkey_path):
        """
        Recursively navigates through the subkeys and values.
        :param hkey: Handle to the open registry key.
        :param subkey_path: Path of the current subkey being processed.
        :return: Nested dictionary of keys and their values.
        """
        with winreg.OpenKey(hkey, subkey_path) as current_key:
            data = {}
            # Read values in the current key
            try:
                i = 0
                while True:
                    value_name, value_data, _ = winreg.EnumValue(current_key, i)
                    data[value_name] = value_data
                    i += 1
            except OSError:
                pass  # No more values

            # Recursively read subkeys
            try:
                i = 0
                while True:
                    subkey_name = winreg.EnumKey(current_key, i)
                    data[subkey_name] = recurse_keys(hkey, f"{subkey_path}\\{subkey_name}")
                    i += 1
            except OSError:
                pass  # No more subkeys

            return data

    # Determine the registry hive and the subpath
    hive, _, subpath = path.partition("\\")
    hkey = getattr(winreg, hive)
    return recurse_keys(hkey, subpath)


def serialize_data(registry_data, filename):
    """
    Serializes the registry data into JSON & writes to a file.
    :param registry_data: the registry data to be serialized
    :param filename: the filename to save serialized data to
    """
    try:
        with open(filename, 'w') as file:
            json.dump(registry_data, file, cls=CustomJSONEncoder, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"An error occurred while writing to file: {e}")


def compare_registries(data1, data2):
    """
    Compares two sets of registry data output into JSON files
    :param data1: the first set of registry data
    :param data2: the second set of registry data
    :return: a structured dictionary with comparison results
    """
    results = {
        'unique_to_data1': {},
        'unique_to_data2': {},
        'different_values': {}
        }

    # Check for unique keys and different values
    for key in data1:
        if key not in data2:
            results['unique_to_data1'][key] = data1[key]
        elif data1[key] != data2[key]:
            results['different_values'][key] = {'data1': data1[key], 'data2': data2[key]}

    for key in data2:
        if key not in data1:
            results['unique_to_data2'][key] = data2[key]

    return results


if __name__ == "__main__":
    choice = input("Choose an option:\n1. Read and save registry data\n2. Compare registry data\nEnter your choice (1 or 2): ")

    if choice == '1':
    # Prompt the user for the registry path
        user_input = input("Enter the registry path to read (e.g., 'HKEY_CURRENT_USER\\Software'): ")
        try:
        # Attempt to read the registry data from the user-provided path
            registry_data = read_registry(user_input)
            print(registry_data)

            # Ask the user if data should be saved to file
            save_data = input("Do you want to save the registry data to a file?")
            if save_data == 'yes':
                filename = input("Enter the filename to save the data: ")
                serialize_data(registry_data, filename)

        except Exception as e:
            # Handle any errors that occur (e.g., invalid path)
            print(f"An error occurred: {e}")

    elif choice == '2':
        # Logic for comparing JSON files
        file1 = input("Enter the filename of the first registry data file: ")
        file2 = input("Enter the filename of the second registry data file: ")
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

        comparison_results = comparison_registries(data1, data2)
        # Logic to display or process the comparison results
        pass # placeholder for result processing logic

    else:
        print("Invalid choice. Please enter 1 or 2.")

# Example usage (Note: this should be run on Windows environment)
# registry_data = read_registry("HKEY_CURRENT_USER\\Software")
# print(registry_data)  # This will print the registry data for the specified path
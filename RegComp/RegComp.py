# registry_comparison.py
import winreg

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

if __name__ == "__main__":
    # Prompt the user for the registry path
    user_input = input("Enter the registry path to read (e.g., 'HKEY_CURRENT_USER\\Software'): ")
    try:
        # Attempt to read the registry data from the user-provided path
        registry_data = read_registry(user_input)
        print(registry_data)
    except Exception as e:
        # Handle any errors that occur (e.g., invalid path)
        print(f"An error occurred: {e}")

# Example usage (Note: this should be run on Windows environment)
# registry_data = read_registry("HKEY_CURRENT_USER\\Software")
# print(registry_data)  # This will print the registry data for the specified path


import pickle
import os

class SaveLoadSystem:
    """
    An all-in-one manager of save data.
    """
    def __init__(self, file_extension, save_folder):
        """
        Args:
            file_extension (str): str
            save_folder (str): str
        """
        self.file_extension = file_extension
        self.save_folder = save_folder

    def save_data(self, data, name):
        """
        Write data to a file.
        Args: 
            data: any
            name (str): str
        """
        with open(self.save_folder + "/" + name + self.file_extension, "wb") as data_file:
            pickle.dump(data, data_file)

    def load_data(self, name):
        """
        Fetch data from a file.
        Args: 
            name (str): str
        """
        try:
            with open(self.save_folder + "/" + name + self.file_extension, "rb") as data_file:
                if os.stat(self.save_folder + "/" + name + self.file_extension).st_size == 0:
                    print(f"Warning: {name}{self.file_extension} is empty.")
                    return None
                data = pickle.load(data_file)
            return data
        except EOFError:
            print(f"Error: Ran out of input while reading {name}{self.file_extension}")
            return None

    def check_for_file(self, name):
        """
        Args:
            name (str): str, the filename to check for.
        """
        return os.path.exists(self.save_folder + "/" + name + self.file_extension)

    def load_game_data(self, files_to_load, default_data):
        """
        Args:
            files_to_load (list): list, what filenames to check for.
            default_data (list): list, indicates what to load if the filename is not found.
        """
        variables = []
        for index, file in enumerate(files_to_load):
            if self.check_for_file(file):
                variables.append(self.load_data(file))
            else:
                variables.append(default_data[index])
        if len(variables) > 1:
            return tuple(variables)
        else:
            return variables[0]

    def save_game_data(self, data_to_save, file_names):
        """
        Args:
            data_to_save (list): list, the values which will be stored. Each value must have a filename at the corresponding index in file_names.
            file_names (list): list, the filenames under which the data is stored.
        """
        for index, file in enumerate(data_to_save):
            self.save_data(file, file_names[index])

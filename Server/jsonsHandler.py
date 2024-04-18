import json


class JsonHandle:

    #  Read the JSON file and load it back as a dictionary
    @staticmethod
    def read_json(name):
        try:
            with open(name, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print("Error: File not found. Please check the file path.")
            return None
        except json.JSONDecodeError:
            print(f"File '{name}' is empty or contains invalid JSON data.")
            return None

    @staticmethod
    def dict_to_json_file(data):
        """
        Converts a dictionary to a JSON string and writes it to a file.

        Parameters:
            data (dict): The dictionary to convert.
        """
        with open('Jsons/Past_Results.json', 'w') as json_file:
            json.dump(data, json_file)

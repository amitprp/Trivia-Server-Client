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

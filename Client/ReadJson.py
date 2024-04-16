import json


class JsonHandle:

    def __init__(self, dic):
        self.dic = dic

    #  Read the JSON file and load it back as a dictionary
    def read_json(self, name):
        path = self.dic + '/' + name
        try:
            with open(path, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print("Error: File not found. Please check the file path.")
            return None

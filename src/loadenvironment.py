import json
from pprint import pprint

def getSqlEngineString():
    file_location = "/home/ubuntu/settings.json"
    

    with open(file_location) as data_file:    
        data = json.load(data_file)

    return data["engine_string"]


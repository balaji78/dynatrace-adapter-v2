import json
class Config:
     
    def __init__(self) :
        config_file = open('./config.json')
        self.config = json.load(config_file)

    def setValue(self, key, value):
        self.config[key] = value        
        with open('./config.json', "w") as _file:
            json.dump(self.config, _file, indent=4)
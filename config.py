import json

config = {}
with open("config.json") as config_json:
    config = json.load(config_json)
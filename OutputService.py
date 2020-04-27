import json

class OutputService:
    @staticmethod
    def prettyJSON(title, content):
        print(title.upper())
        print(json.dumps(content, indent=4, sort_keys=True))
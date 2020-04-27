from config import config

class Store:
    def __init__(self, data):
        self.name = data['name']
        self.logo = data['logo_url']
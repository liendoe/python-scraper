from config import config

class User:
    email = None
    password = None
    def __init__(self, user):
        self.email = user['email']
        self.password = user['password']



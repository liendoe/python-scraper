from config import config
from Crawler import Crawler
from OutputService import OutputService
from User import User
from Store import Store

def main():
    crawler = Crawler()
    for user in config['users']:
        user = User(user)
        OutputService.prettyJSON('User:', user.__dict__)
        
        crawler.setUser(user)
        crawler.login()
        store_data = crawler.extractStoreData()
        store = Store(store_data)
        OutputService.prettyJSON('Store:', store.__dict__)
        
        blocks = crawler.extractProducts(store_data)
        OutputService.prettyJSON('Blocks:', blocks)
main()


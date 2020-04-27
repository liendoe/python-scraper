from config import config
from User import User

import bs4
import json
import requests
import string
import urllib.parse

class Crawler:
    user = None
    site = None
    csrf_token = None
    def __init__(self):
        self.site = config['site']

    def setUser(self, user:User):
        self.user = user

    def login(self):
        url = self.site["domain"] + self.site["paths"]["login"]
        params = json.dumps({
            'scope' : '',
            'grant_type' : 'password',
            'signup_v3_endpoints_web' : '',
            'email' : self.user.email,
            'password' : self.user.password,
            'address' : ''
        })
        headers = self.getJSONHeaders()
        r = requests.post(url = url, data = params, headers = headers)
        self.prevCookies = r.cookies
        return r
        
    def extractStoreData(self):
        store_page = self.getStorePage()
        soup = bs4.BeautifulSoup(store_page, features='html.parser')
        initial_bundle = soup.find('script',attrs={'id' : 'node-initial-bundle'})
        initial_bundle = json.loads(urllib.parse.unquote(initial_bundle.contents[0]))
        next_available_action = initial_bundle['bundle']['app_modules']['header']['data']['next_available_action']
        self.csrf_token = initial_bundle['bundle']['public_keys']['csrf_token']
        return {
            'name': next_available_action['data']['retailer']['name'],
            'slug': next_available_action['data']['retailer']['slug'],
            'logo_url': next_available_action['data']['retailer']['logo']['url'],
            'csrf_token': self.csrf_token
        }
    
    def getStorePage(self):
        url = self.site["domain"] + self.site["paths"]["store"]
        params = {}
        headers = self.getHTMLHeaders()
        cookies = self.extractResponseCookies(self.prevCookies)
        r = requests.get( url = url, params = params, headers = headers, cookies = cookies)
        
        self.prevCookies = r.cookies
        return r.text

    def extractProducts(self, store_data):
        storefront_page = json.loads(self.getStoreFrontPage(store_data))
        modules = storefront_page['container']['modules']
        products = {}
        for module in modules:
            module_name = module['data']['header']['label']
            module_page = self.getModulePage(module['async_data_path'])
            items = json.loads(module_page)['module_data']['items']
            product_items = []
            for item in items:
                # product_items.append({'name':item['name'],'price':item['pricing']['price']})
                product_items.append(item['name'])
            products.update({ module_name: product_items})
        return products

    def getStoreFrontPage(self, store_data):
        url = self.site["domain"] + self.site["paths"]["storefront"].replace(":retailer_slug", store_data['slug'])
        params = {}
        headers = self.getJSONHeaders()
        headers.update({'x-csrf-token': self.csrf_token})
        cookies = self.extractResponseCookies(self.prevCookies)
        r = requests.get( url = url, params = params, headers = headers, cookies = cookies)
        
        self.prevCookies = r.cookies
        return r.text

    def getModulePage(self, module_path):
        url = self.site["domain"] + module_path
        params = {}
        headers = self.getJSONHeaders()
        headers.update({'x-csrf-token': self.csrf_token})
        cookies = self.extractResponseCookies(self.prevCookies)
        r = requests.get( url = url, params = params, headers = headers, cookies = cookies)
        return r.text
    
    def extractResponseCookies(self, cookies):
        responseCookies = {}
        for cookie in cookies._cookies:
            for c in cookies._cookies[cookie]:
                for key in cookies._cookies[cookie][c]:
                    responseCookies.update({key: cookies[key]})
        return responseCookies

    def getJSONHeaders(self):
        headers = self.getCommonHeaders()
        headers.update({
            'accept': 'application/json',
            'content-type': 'application/json',
            'x-client-identifier': 'web',
            'x-requested-with': 'XMLHttpRequest',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors'
        })
        return headers

    def getHTMLHeaders(self):
        headers = self.getCommonHeaders()
        headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'upgrade-insecure-requests': '1'
        })
        return headers

    def getCommonHeaders(self):
        return {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'es-ES,es;q=0.9,en;q=0.8,it;q=0.7',
            'cache-control': 'no-cache',
            'dnt': '1',
            'pragma': 'no-cache',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
        }

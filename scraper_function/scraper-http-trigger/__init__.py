import logging
import json
import pymongo

import urllib
from urllib.request import Request, urlopen

import azure.functions as func

from bs4 import BeautifulSoup

save = False
uri = "mongodb://scrapi-db-client:04eVytMwKXPIwQLBEu2w0NxtRZn3IJVentyJiNcacHwtSmucfufY7mnqfnGf9lRbFjbhtzKIQSBOCtstLcHkxA==@scrapi-db-client.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@scrapi-db-client@&retrywrites=false"

def Soup(url):
	# Mozilla/5.0
	# Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11
	# Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36
	# Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'}
    req = Request(url, headers = hdr)
    page = "<div></div>"
    try:
        page = urlopen(req)
        print(page.getcode())
    except urllib.error.URLError as err:
        print(err, url)
    return BeautifulSoup(page, 'html.parser')

def get_callback(callback):
    if callback == "get_text":
        return get_text
    elif callback == "get_content":
        return get_attr("content")
    elif callback == "get_href":
        return get_attr("href")

def get_text(q : BeautifulSoup):
	if len(q) > 1:
		ret = []
		for i in q:
			ret.append(i.get_text())
		return ret
	return q[0].get_text()

def get_attr(attr):
	def decorator(q : BeautifulSoup):
		if len(q) > 1:
			ret = []
			for i in q:
				ret.append(i[attr])
			return ret
		return q[0][attr]
	return decorator

class Profile:
	def __init__(self, **args):
		self.hooks = args

	def addHook(self, hookname : str, selector : str, hookcallback):
		self.hooks.update({
			hookname : {
				"select" : selector,
				"callback" : hookcallback
			}
		})

	def digest(self, soup : BeautifulSoup):
		ret = {}
		for hookName, rule in self.hooks.items():
			try:
				callback = rule["callback"]
				val = callback(soup.select(rule["selector"]))
				ret.update({hookName : val})
				setattr(self, hookName, val)
			except IndexError:
				val = "Not found: " + rule["selector"]
				ret.update({hookName : val})
				setattr(self, hookName, val)
				print("-", Exception(rule['selector']))
		return ret

	def json(self):
		ret = {}
		for hookName in self.hooks.keys():
			value = getattr(self, hookName)
			ret.update({hookName : value if not issubclass(Profile, self.__class__) else value.json()})
		return ret

def scrape(name, url, hooks):
    # convert strings to callbacks
    logging.info("pre-hooks: " + str(hooks))

    if isinstance(hooks, list):
        h = {}
        for name, hook in hooks:
            h[name] = {
                'selector': hook['callback'],
                'callback': get_callback(hook['callback'])
            }
            logging.info("h: " + name + "," + str(hook))
        hooks = h
    else:
        for name, rule in hooks.items():
            hooks[name]['callback'] = get_callback(rule['callback'])
            logging.info("h: " + name + "," + str(rule))

    logging.info("hooks: " + str(hooks))
    
    item = {
        "name": name,
        "data": Profile(**hooks).digest(Soup(url))
        }

    if save:
        pymongo.MongoClient(uri).scrapi.data.insert(item)

    return item

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ScrAPI HTTP trigger function processed a request.')

    try:
        req_body = str(req.get_body().decode("utf-8"))

        logging.info("body: " + req_body)

        req_json = json.loads(req_body)

        name = req_json['name']# req.params.get('name')
        url = req_json['url']# req.params.get('url')
        hooks = req_json['hooks']# req.params.get('hooks')

        # if req_json['save']:
        #     save = True

        logging.info("pre-scrape: " + str(req_json))
        response = scrape(name, url, hooks)

        return func.HttpResponse(str(response), status_code=200)
    except ValueError:
        return func.HttpResponse("error")

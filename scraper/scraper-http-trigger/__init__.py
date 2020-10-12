
import logging
import json

import urllib
from urllib.request import Request, urlopen

import azure.functions as func

from bs4 import BeautifulSoup

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
        logging.info(page.getcode());
    except urllib.error.URLError as err:
        logging.info(err + ": " + url);
    return BeautifulSoup(page, 'html.parser')

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

def get_callback(callback):
    if callback == "get_text":
        return get_text
    elif callback == "get_content":
        return get_attr("content")
    elif callback == "get_href":
        return get_attr("href")
    elif callback == "get_src":
        return get_attr("src")

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
				val = callback(soup.select(rule["selector"])) # .replace(r"\n", "").replace(r"\x", " ")
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
        logging.info("is_list");
        for hook in hooks:
            logging.info("h: " + hook["name"] + "," + str(hook["hook"]))
            h[hook["name"]] = {
                'selector': hook["hook"]['selector'],
                'callback': get_callback(hook["hook"]['callback'])
            }
        hooks = h
    else:
        logging.info("is_dict")
        for n, rule in hooks.items():
            logging.info("h: " + n + "," + str(rule))
            hooks[n]['callback'] = get_callback(rule['callback'])

    logging.info("hooks: " + str(hooks))
    
    return {
        "name": name,
        "data": Profile(**hooks).digest(Soup(url))
        }

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ScrAPI HTTP trigger function processed a request.')

    try:
        req_body = str(req.get_body().decode("utf-8"))

        logging.info("body: " + req_body)

        req_json = json.loads(req_body)

        logging.info("pre-scrape: " + str(req_json))
        result = scrape(req_json['name'], req_json['url'], req_json['hooks'])

        return func.HttpResponse(str(result), status_code=200)
    except Exception as e:
        return func.HttpResponse("error:" + str(dict(e)))

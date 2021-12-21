#VERSION: 1.00
#AUTHORS: Gaein nidb (mail@gaein.cn)

# Open source under GPL v3

from json import encoder
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
import sgmllib
# some other imports if necessary
import requests
import json

class tjuptorg(object):
    
    """
    `url`, `name`, `supported_categories` should be static variables of the engine_name class,
     otherwise qbt won't install the plugin.

    `url`: The URL of the search engine.
    `name`: The name of the search engine, spaces and special characters are allowed here.
    `supported_categories`: What categories are supported by the search engine and their corresponding id,
    possible categories are ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books').
    """
    url = 'https://github.com/nidbCN/tjupt_search_plugin'
    name = 'Search plugin for tjupt'
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4', 'music': '1', 'games': '2', 'anime': '7', 'software': '3'}

    base_url = "https://tjupt.org/"

    def __init__(self):
        self.__username = ""
        self.__password = ""
        self.__cookie = ""
        """
        some initialization
        """

    def __get_cookie(self) -> str:
        FILENAME = "tjupt.json"
        with open(FILENAME) as config_file:
            config_json = json.load(config_file)
            if "cookie" in config_file:
                __cookie = config_file["cookie"]
            else:
                login_resp = requests.post(self.base_url + "takelogin.php", data = {
                    "username": self.__username,
                    "password": self.__password,
                    "logout": "90days"
                })
                
                self.__cookie = login_resp.headers["set-cookie"].split(';')[0]

        return self.__cookie

    def __set_cookie(self, cookie: str) -> None:
        FILENAME = "tjupt.json"
        with open(FILENAME, encoding="utf8") as config_file:
            json.dump({"cookie": cookie}, config_file, ensure_ascii=False)
            config_file.close()


    def download_torrent(self, info):
        """
        Providing this function is optional.
        It can however be interesting to provide your own torrent download
        implementation in case the search engine in question does not allow
        traditional downloads (for example, cookie-based download).
        """
        print download_file(info)

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        """
        Here you can do what you want to get the result from the search engine website.
        Everytime you parse a result line, store it in a dictionary
        and call the prettyPrint(your_dict) function.

        `what` is a string with the search tokens, already escaped (e.g. "Ubuntu+Linux")
        `cat` is the name of a search category in ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')
        """
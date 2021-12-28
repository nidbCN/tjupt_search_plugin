# VERSION: 1.00
# AUTHORS: Gaein nidb (mail@gaein.cn)

# Open source under GPL v3

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
# import sgmllib
# some other imports if necessary

import os
import json
from urllib import request
from urllib import parse


class NoRedirHandler(request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return fp
    http_error_301 = http_error_302


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
    supported_categories = {"movies": True,
                            "tv": True,
                            "music": True,
                            "games": True,
                            "anime": True,
                            "software": True, }

    base_url = "https://tjupt.org/"
    user_agent = "TJUPT_search_plugin/0.1 (use Python-urllib, for qBitorrnt search)"

    def __init__(self):
        self.__username = ""
        self.__password = ""
        self.__cookie = ""
        """
        some initialization
        """

    def __get_cookie(self) -> str:
        FILENAME = "tjupt.json"
        if os.path.exists(FILENAME):
            with open(FILENAME, mode="r", encoding="utf8") as config_file:
                config_json = json.load(config_file)
                if "cookie" in config_json:
                    self.__cookie = config_json["cookie"]
        else:
            payload = {
                "username": self.__username,
                "password": self.__password,
                "logout": "360days"
            }

            req_opener = request.build_opener(NoRedirHandler)
            req_opener.addheaders = [
                ("User-Agent", self.user_agent)]
            login_resp = req_opener.open(
                self.base_url + "takelogin.php", data=parse.urlencode(payload).encode("utf-8"))
            cookies = login_resp.getheader("Set-Cookie")
            if cookies is not None:
                cookie_list = cookies.split(';')
                self.__set_cookie(cookie_list[0])

        return self.__cookie

    def __set_cookie(self, cookie: str) -> None:
        FILENAME = "tjupt.json"
        with open(FILENAME, mode="w+", encoding="utf8") as config_file:
            json.dump({"cookie": cookie}, config_file, ensure_ascii=False)
            self.__cookie = cookie

    def download_torrent(self, info):
        """
        Providing this function is optional.
        It can however be interesting to provide your own torrent download
        implementation in case the search engine in question does not allow
        traditional downloads (for example, cookie-based download).
        """
        print(download_file(info))

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

        tjupt_cat = {
            "movies": "cat401",
            "tv": "cat402",
            "music": "cat406",
            "games": "cat409",
            "anime": "cat405",
            "software": "cat408",
        }

        param_dcit = {
            "search": what
        }

        if cat in tjupt_cat:
            param_dcit[tjupt_cat[cat]] = 1

        search_req = request.Request(
            self.base_url + "torrents.php?" + parse.urlencode(param_dcit),
            headers={
                "Cookie": self.__get_cookie(),
                "User-Agent": self.user_agent
            })

        search_resp = request.urlopen(search_req)
        if search_resp.code == 200:
            print(search_resp.read().decode('utf-8'))
            prettyPrinter()

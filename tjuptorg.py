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
from html.parser import HTMLParser

BASE_URL = "https://tjupt.org/"


class TjuptHtmlParser(HTMLParser):
    """Parse tjupt result page

    This class is a holy shit, do not try to understand it
    I cannot use bs in plugin
    """
    info_dict_list: dict

    in_list_table: bool
    in_title_table: bool
    in_list_tr: bool
    in_title_td: bool
    in_seeder_td: bool
    in_downloaders_td: bool
    in_size_td: bool
    in_disabled: bool

    td_others_count: int
    td_title_count: int

    has_next_page: bool

    def __init__(self, dict_list: list) -> None:
        HTMLParser.__init__(self)
        self.in_list_table = False
        self.in_title_table = False
        self.in_list_tr = False
        self.in_title_td = False
        self.in_seeder_td = False
        self.in_size_td = False
        self.in_downloaders_td = False
        self.in_disabled = False
        self.td_others_count = 0
        self.td_title_count = 0
        self.info_dict_list = dict_list

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            if ("class", "torrents") in attrs:
                self.in_list_table = True
            elif ("class", "torrentname") in attrs:
                self.in_title_table = True
        elif tag == "tr":
            if self.in_list_table and not self.in_title_table:
                self.in_list_tr = True
        elif tag == "td":
            if self.in_title_table and ("class", "embedded") in attrs:
                if self.td_title_count == 1:
                    # td element which contains title and link
                    self.in_title_td = True
                self.td_title_count = self.td_title_count + 1
            elif self.in_list_table and ("class", "rowfollow") in attrs:
                if self.td_others_count == 3:
                    # td element which contains file size
                    self.in_size_td = True
                elif self.td_others_count == 4:
                    # td element which contains seeders
                    self.in_seeder_td = True
                elif self.td_others_count == 5:
                    # td element which contains downloaders
                    self.in_downloaders_td = True
                self.td_others_count = self.td_others_count + 1
        elif tag == "a" and self.in_title_td:
            url = BASE_URL + attrs[1][1]
            title = attrs[0][1]
            self.info_dict_list.append({
                "link": url,
                "name": title,
                "size": "Unknow",
                "seeds": "Unknow",
                "leech": "Unknow",
                "engine_url": BASE_URL
            })
        elif tag == "font":
            if ("class", "gray") in attrs:
                self.in_disabled = True
        elif tag == "b":
            if ("title", "Alt+Pagedown") in attrs and not self.in_disabled:
                self.has_next_page = True

    def handle_endtag(self, tag):
        if tag == "table":
            if self.in_title_table:
                self.in_title_table = False
                self.td_title_count = 0
        elif tag == "tr":
            if self.in_list_tr:
                if self.in_list_table and not self.in_title_table:
                    # go next table
                    self.in_list_tr = False
                    self.td_others_count = 0
        elif tag == "td":
            if self.in_title_td:
                self.in_title_td = False
            elif self.in_size_td:
                self.in_size_td = False
            elif self.in_seeder_td:
                self.in_seeder_td = False
            elif self.in_downloaders_td:
                self.in_downloaders_td = False
        elif tag == "font":
            if self.in_disabled:
                self.in_disabled = False

    def handle_data(self, data):
        if self.in_size_td:
            self.info_dict_list[-1]["size"] = str(data).replace("<br>", " ")
        elif self.in_seeder_td:
            self.info_dict_list[-1]["seeds"] = str(data)
        elif self.in_downloaders_td:
            self.info_dict_list[-1]["leech"] = str(data)

    def parse_search(self, html_str: str) -> bool:
        self.feed(html_str)
        self.close()


class NoRedirHandler(request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return fp
    http_error_301 = http_error_302


class tjuptorg(object):
    url = 'https://github.com/nidbCN/tjupt_search_plugin'
    name = 'Search plugin for tjupt'
    supported_categories = {"movies": True,
                            "tv": True,
                            "music": True,
                            "games": True,
                            "anime": True,
                            "software": True, }

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
                BASE_URL + "takelogin.php", data=parse.urlencode(payload).encode("utf-8"))
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

        has_next_page = True
        page_number = 0

        while has_next_page:
            param_dcit["page"] = page_number
            search_req = request.Request(
                BASE_URL + "torrents.php?" + parse.urlencode(param_dcit),
                headers={
                    "Cookie": self.__get_cookie(),
                    "User-Agent": self.user_agent
                })

            search_resp = request.urlopen(search_req)
            if search_resp.code == 200:
                search_result_html = search_resp.read().decode('utf-8')
                result_dict_list = []
                search_parser = TjuptHtmlParser(result_dict_list)
                has_next_page = search_parser.parse_search(search_result_html)
                for info_dict in result_dict_list:
                    prettyPrinter(info_dict)
            else:
                has_next_page = False

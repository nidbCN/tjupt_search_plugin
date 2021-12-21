# tjupt search plugin

WAIT FOR CODE...

POST takelogin.php

Form Data:
username: NAME
password: PASSWD
logout: 90days

RESP set-cookie: access_token=xxxxx.xxxx.xxxx; expires=Wed, 16-Mar-2022 11:44:00 GMT; Max-Age=7776000; path=/; domain=.tjupt.org

https://tjupt.org/torrents.php?incldead=0&spstate=0&picktype=0&inclbookmarked=0&keepseed=0&search=Magical+Mirai&search_area=0&search_mode=0

列表：#torrents.tbody

标题：tr[0]td[1].a.title
下载：td[2].a.href

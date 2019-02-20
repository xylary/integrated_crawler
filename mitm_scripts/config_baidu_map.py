# -*- coding: utf-8 -*-

import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
from mitmproxy import ctx
import json


def response(flow):
    """修改应答数据"""
    if '?newmap=1' in flow.request.url and 'da_src=searchBox.button&wd=' in flow.request.url and '&auth=' in flow.request.url:
        with open('data/baidu_map_result.txt', 'a+', encoding='UTF-8', newline='') as file:
            file.write(flow.response.text+'\n')

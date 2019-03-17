# -*- coding: utf-8 -*-

import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
from mitmproxy import ctx


def request(flow):
    if flow.request.method == 'GET':
        print(flow.request)


def response(flow):
    print(flow.response)
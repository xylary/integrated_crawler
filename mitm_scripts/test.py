# -*- coding: utf-8 -*-

import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
from PIL import Image
from io import BytesIO, StringIO





def response(flow):
    """修改应答数据"""
    if '.png' in flow.request.url:
        # 屏蔽selenium检测
        print(flow.request.url)
        print('Good')
        print(mitmproxy.http.HTTPResponse.wrap(flow.response).headers)

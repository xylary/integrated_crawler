# -*- coding: utf-8 -*-

from mitmproxy import ctx


def request(flow):
    if flow.request.method == "GET":
        # If the decision is done by domain, one could also modify the server address here.
        # We do it after CONNECT here to have the request data available as well.
        client_ip = flow.client_conn.address[0]
        print(client_ip)
        print('OK')
    '''    
        if 'ip.cn' in flow.request.url:
                ctx.log.info(flow.request.url)
                proxy = ("localhost", 8080)
        else:
                proxy = ("localhost", 3800)
    # 这里配置二级代理的ip地址和端口
    if flow.live:
        flow.live.change_upstream_proxy_server(proxy)
    '''
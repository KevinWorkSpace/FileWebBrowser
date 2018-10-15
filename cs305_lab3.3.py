import asyncio
import os, sys
from parse_header import HTTPHeader
import mimetypes
import requests

async def dispatch(reader, writer):
    header = HTTPHeader()
    while True:
        data = await reader.readline()
        message = data.decode()
        header.parse_header(message)
        if data == b'\r\n':
            break
    path = './' + header.get('path')
    if header.get('method') == 'GET' or header.get('method') == 'HEAD':
        # path += header.get('path')
        if not os.path.exists(path):
            # 如果不存在, 404
            writer.writelines([
                b'HTTP/1.0 404 OK\r\n',
                b'Content-Type:text/html; charset=utf-8\r\n',
                b'Connection: close\r\n',
                b'\r\n',
                b'<html><body>404 Not Found<body></html>\r\n',
                b'\r\n'
            ])
        elif os.path.isdir(path):
            # 如果是目录. 则列出里面的所有文件和目录
            dirs = os.listdir(path)
            strs = ('<html><head><title>Index of .//</title></head>'
                   '<body bgcolor="white">'
                   '<h1>Index of .//</h1><hr>'
                   '<pre>')
            for dir in dirs:
                if os.path.isdir(path + '/' + dir):
                    strs += '\n<a href="' + dir + '">' + dir + '/</a><br>\n'
                else:
                    strs += '\n<a href="' + dir + '">' + dir + '</a><br>\n'
            strs += '</pre>\n' + '<hr>\n' + '</body></html>' + '\r\n'
            writer.writelines([
                b'HTTP/1.0 200 OK\r\n',
                b'Content-Type:text/html; charset=utf-8\r\n',
                b'Connection: close\r\n',
                b'\r\n',
                strs.encode(),
                b'\r\n'
            ])
        else:
            filetype = (mimetypes.guess_type(path))[0]
            filesize = os.path.getsize(path)
            if filetype is None:
                filetype = 'application/octet-stream'
            try:
                str = open(path, 'rb').read()
                # writer.writelines([
                #     b'HTTP/1.0 200 OK\r\n',
                #     b'Content-Type:' + filetype.encode() + b'; charset=utf-8\r\n',
                #     b'Connection: close\r\n',
                #     b'\r\n',
                #     str,
                #     b'\r\n'
                # ])
                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type:' + filetype.encode() + b'; charset=utf-8\r\n',
                    # b'Content-Length: ' + bytes(filesize) + b'\r\n',
                    b'Connection: close\r\n',
                    b'\r\n',
                    str,
                    b'\r\n'
                ])
            except FileNotFoundError:
                writer.writelines([
                    b'HTTP/1.0 404 OK\r\n',
                    b'Content-Type:text/html; charset=utf-8\r\n',
                    b'Connection: close\r\n',
                    b'\r\n',
                    b'<html><body>404 Not Found<body></html>\r\n',
                    b'\r\n'
                ])
    else:
        writer.writelines([
            b'HTTP/1.0 405 OK\r\n',
            b'Content-Type:text/html; charset=utf-8\r\n',
            b'Connection: close\r\n',
            b'\r\n',
            b'<html><body>405 Method Not Allowed<body></html>\r\n',
            b'\r\n'
        ])
    await writer.drain()
    writer.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 8080, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

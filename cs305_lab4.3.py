import asyncio
import os
from parse_header import HTTPHeader
import mimetypes

path = '.'
async def dispatch(reader, writer):
    header = HTTPHeader()
    while True:
        data = await reader.readline()
        message = data.decode()
        header.parse_header(message)
        if data == b'\r\n':
            break

    if header.get('method') == 'GET' or header.get('method') == 'HEAD':
        global path
        if header.get('cookie') is None:
            path += header.get('path')
        else:
            path = header.get('cookie').split('=')[1] + header.get('path')
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
            if (header.get('path') == '/') & (header.get('cookie') == 'sessionID=./'):
                dirs = os.listdir('./')
                strs = ('<html><head><title>Index of .//</title></head>'
                        '<body bgcolor="white">'
                        '<h1>Index of .//</h1><hr>'
                        '<pre>')
                strs += '\n<a href="' + './' + '">' + './' + '/</a><br>\n'
                for dir in dirs:
                    if os.path.isdir(path + '/' + dir):
                        strs += '\n<a href="' + dir + '">' + dir + '/</a><br>\n'
                    else:
                        strs += '\n<a href="' + dir + '">' + dir + '</a><br>\n'
                strs += '</pre>\n' + '<hr>\n' + '</body></html>' + '\r\n'
                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type:text/html; charset=utf-8\r\n',
                    b'Set-Cookie: sessionID=./\r\n',
                    b'Connection: close\r\n',
                    b'\r\n',
                    strs.encode(),
                    b'\r\n'
                ])
            elif header.get('path') == '/':
                dirs = os.listdir('./')
                strs = ('<html><head><title>Index of .//</title></head>'
                        '<body bgcolor="white">'
                        '<h1>Index of .//</h1><hr>'
                        '<pre>')
                strs += '\n<a href="' + './' + '">' + './' + '/</a><br>\n'
                for dir in dirs:
                    if os.path.isdir(path + '/' + dir):
                        strs += '\n<a href="' + dir + '">' + dir + '/</a><br>\n'
                    else:
                        strs += '\n<a href="' + dir + '">' + dir + '</a><br>\n'
                strs += '</pre>\n' + '<hr>\n' + '</body></html>' + '\r\n'
                writer.writelines([
                    b'HTTP/1.0 302 Found\r\n',
                    b'Content-Type:text/html; charset=utf-8\r\n',
                    b'Location: ./\r\n',
                    b'Set-Cookie: sessionID=./\r\n',
                    b'Connection: close\r\n',
                    b'\r\n',
                    strs.encode(),
                    b'\r\n'
                ])
            else:
                dirs = os.listdir(path)
                strs = ('<html><head><title>Index of .//</title></head>'
                        '<body bgcolor="white">'
                        '<h1>Index of .//</h1><hr>'
                        '<pre>')
                strs += '\n<a href="' + './' + '">' + './' + '/</a><br>\n'
                for dir in dirs:
                    if os.path.isdir(path + '/' + dir):
                        strs += '\n<a href="' + dir + '">' + dir + '/</a><br>\n'
                    else:
                        strs += '\n<a href="' + dir + '">' + dir + '</a><br>\n'
                strs += '</pre>\n' + '<hr>\n' + '</body></html>' + '\r\n'
                if header.get('cookie') is None:
                    writer.writelines([
                        b'HTTP/1.0 200 OK\r\n',
                        b'Content-Type:text/html; charset=utf-8\r\n',
                        b'Set-Cookie: sessionID=' + path.encode() + b'\r\n',
                        b'Connection: close\r\n',
                        b'\r\n',
                        strs.encode(),
                        b'\r\n'
                    ])
                else:
                    oldC = header.get('cookie')
                    list = oldC.split('=')
                    oldCookie = list[1]
                    writer.writelines([
                        b'HTTP/1.0 200 OK\r\n',
                        b'Content-Type:text/html; charset=utf-8\r\n',
                        b'Set-Cookie: sessionID=' + oldCookie.encode() + header.get('path').encode() + b'\r\n',
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
                fileBits = open(path, 'rb').read()
                if(header.get('range') is None):
                    # if(filetype == 'video/mpeg4'):
                    #     filetype = 'video/mp4'
                    writer.writelines([
                        b'HTTP/1.0 200 OK\r\n',
                        b'Content-Type:' + filetype.encode() + b'; charset=utf-8\r\n',
                        # b'Content-Type: ' + filetype.encode() + b';\r\n',
                        b'Content-Length: %d' % (filesize) + b'\r\n',
                        b'Connection: close\r\n',
                        b'\r\n',
                        fileBits,
                        b'\r\n'
                    ])
                else:
                    requestHeader = header.get('range')
                    print(requestHeader)
                    l1 = requestHeader.split('=')
                    print(l1[1])

                    # if (filetype == 'video/mpeg4'):
                    #     filetype = 'video/mp4'
                    print(filetype)
                    l2 = l1[1].split('-')
                    if l2[1] == '':
                        writer.writelines([
                            b'HTTP/1.1 206 Partial Content\r\n',
                            b'Content-Range: bytes ' + l2[0].encode() + b'-%d/%d\r\n' % (filesize - 1, filesize),
                            b'Content-Length: %d' % (filesize - int(l2[0])) + b'\r\n',
                            b'Content-Type: ' + filetype.encode() + b'; charset=utf-8\r\n',
                            # b'Content-Type: ' + filetype.encode() + b';\r\n',
                            b'Connection: close\r\n',
                            b'\r\n',
                            fileBits,
                            b'\r\n'
                        ])
                    else:
                        writer.writelines([
                            b'HTTP/1.1 206 Partial Content\r\n',
                            b'Content-Range: bytes %s\r\n' % (l1[1]),
                            b'Content-Length: %d' % (int(l2[1]) - int(l2[0]) + 1) + b'\r\n',
                            b'Content-Type: ' + filetype.encode() + b'; charset=utf-8\r\n',
                            b'Connection: close\r\n',
                            b'\r\n',
                            fileBits,
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

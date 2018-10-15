
keys = ('method', 'path', 'range', 'cookie')

class HTTPHeader:
    def __init__(self):
        self.headers = {key: None for key in keys}

    def parse_header(self, line):
        fileds = line.split(' ')
        # print(fileds)

        if fileds[0] == 'GET' or fileds[0] == 'POST' or fileds[0] == 'HEAD':
            self.headers['method'] = fileds[0]
            self.headers['path'] = fileds[1]

        if fileds[0] == 'Range:':
            self.headers['range'] = fileds[1].replace("\r\n", "")

        if fileds[0] == 'Cookie:':
            self.headers['cookie'] = fileds[1].replace("\r\n", "")
    
    def get(self, key):
        return self.headers.get(key)
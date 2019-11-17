import abc


class Provider(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def convert(cls, url):
        raise NotImplementedError('Implement in class')

    @staticmethod
    @abc.abstractmethod
    def check_url(url):
        raise NotImplementedError('Implement in class')


class Release:

    def __init__(self, tag, body, url):
        self.tag = tag
        self.body = body
        self.url = url

    def get_rst(self):
        if self.body:
            body = '\n'.join([self.parse_line(line) for line in self.body.splitlines()])
        else:
            body = '\n'
        rst = f"""
{self.tag}
===========

{body}

`Release <{self.url}>`_

"""
        return rst

    @staticmethod
    def parse_line(line):
        # Assume markdown here
        if line.startswith('- '):
            line = '*'+line[1:]
        if line.startswith('##'):
            line = line[3:]+'\n'+'-'*(len(line)-1)
        if line.startswith('###'):
            line = line[3:]+'\n'+'~'*(len(line)-1)
        return line

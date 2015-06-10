__author__ = 'Alex Haslehurst'

from abc import ABCMeta, abstractmethod
import gzip
import urllib
import time


class ScraperBase(metaclass=ABCMeta):

    def __init__(self, source):
        self.source = source

    @abstractmethod
    def __iter__(self):
        pass

    def get_iterator(self):
        return self.__iter__()

    @staticmethod
    def _try_open_stream(request):
        while True:
            try:
                response = urllib.request.urlopen(request)
                buf = response.read()
                if response.info().get('Content-Encoding') == 'gzip':
                    return gzip.decompress(buf).decode()
                else:
                    return buf.decode()
            except ConnectionResetError:
                print("Connection reset")
                time.sleep(10)
                print("Retrying")

    @staticmethod
    def _save_file(request, file_name):
        response = urllib.request.urlopen(request)
        f = open(file_name, 'wb')
        meta = dict(response.info())
        file_size = int(meta.get("Content-Length"))
        print("Downloading: %s Bytes: %s" % (file_name, file_size))
        buffer = response.read()
        f.write(buffer)
        f.close()
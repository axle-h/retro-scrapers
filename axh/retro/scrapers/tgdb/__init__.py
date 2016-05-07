import urllib.parse
import urllib.request

__author__ = 'Alex Haslehurst'


class TgDbRequest(urllib.request.Request):
    Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    AcceptEncoding = "gzip"
    AcceptLanguage = "en-GB,en;q=0.8"
    CacheControl = "no-cache"
    Connection = "keep-alive"
    Pragma = "no-cache"
    UserAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"

    TgDbScheme = "http"
    TgDbNetloc = "thegamesdb.net"
    TgDbHeaders = {'Accept': Accept, 'Accept-Encoding': AcceptEncoding, 'Accept-Language': AcceptLanguage,
                   'Cache-Control': CacheControl, 'Connection': Connection, 'Pragma': Pragma, 'User-Agent': UserAgent}

    def __init__(self, url_path, params=None):
        url = TgDbRequest._get_url(url_path, params)
        super().__init__(url, headers=self.TgDbHeaders)

    @staticmethod
    def _get_url(url_path, params):
        parsed = urllib.parse.urlparse(url_path)

        if params is None:
            return "{0}://{1}{2}".format(TgDbRequest.TgDbScheme, TgDbRequest.TgDbNetloc, parsed.path)
        else:
            return "{0}://{1}{2}?{3}".format(TgDbRequest.TgDbScheme, TgDbRequest.TgDbNetloc, parsed.path,
                                             urllib.parse.urlencode(params))
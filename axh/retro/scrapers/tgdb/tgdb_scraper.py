from axh.retro.scrapers.models import Rom, RetroImage
from axh.retro.scrapers.scraper import ScraperBase
from axh.retro.scrapers.tgdb import TgDbRequest
from xml.etree import ElementTree
import re
import os
import urllib.parse

__author__ = 'Alex Haslehurst'


class _TgDbGetPlatformRequest(TgDbRequest):
    GetPlatformUrl = "/api/GetPlatform.php"

    def __init__(self, platform_id):
        super().__init__(self.GetPlatformUrl, {"id": platform_id})
        self.platform_id = platform_id


class _TgDbGetGameRequest(TgDbRequest):
    GetPlatformUrl = "/api/GetGame.php"

    def __init__(self, platform, name, is_exact=False):
        super().__init__(self.GetPlatformUrl, {"platform": platform, "exactname" if is_exact else "name": name})
        self.platform = platform
        self.name = name


class _TgDbGetImageRequest(TgDbRequest):
    GetImageUrl = "/banners/"

    def __init__(self, url):
        super().__init__(self.GetImageUrl + url)


class TgDbApiClient(ScraperBase):
    def __init__(self, system):
        super().__init__("TheGamesDb")
        self.platform = TgDbApiClient._get_platform(system.platform)
        self.roms = [rom for rom in
                     [self._try_scrape(file_name) for file_name in os.listdir(system.path) if
                      any(file_name.endswith(ext) for ext in system.extensions)] if rom is not None]

    def save_images(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

        for rom in self.roms:
            if rom.boxart_back is not None:
                rom.image = os.path.join(path, os.path.splitext(rom.file_name)[0] + "-back" +
                                                os.path.splitext(rom.boxart_back.url)[1])
                ScraperBase._save_file(_TgDbGetImageRequest(rom.boxart_back.url), rom.image)


            if rom.boxart_front is not None:
                rom.image = os.path.join(path, os.path.splitext(rom.file_name)[0] + "-back" +
                                                os.path.splitext(rom.boxart_back.url)[1])
                ScraperBase._save_file(_TgDbGetImageRequest(rom.boxart_front.url), rom.image)

    def _try_scrape(self, file_name):
        print("[%s]" % file_name, end=" ")

        rom_name = file_name.split("(")[0].strip()
        the_index = rom_name.find(", The")
        if the_index > 0:
            rom_name = "The " + rom_name[:the_index] + rom_name[the_index + 5:]

        if rom_name.endswith(", The"):
            rom_name = "The " + rom_name[0:-5]

        exact_rom = self._try_get_exact_game(rom_name, file_name)
        if exact_rom is not None:
            print("exact: " + rom_name)
            return exact_rom

        roms = self._get_games(rom_name, file_name)
        if len(roms) == 0:
            print("failed")
            return None

        if len(roms) == 1:
            print("single: " + rom_name)
            return roms[0]

        alpha_numeric_pattern = re.compile('[\W_]+')
        key = alpha_numeric_pattern.sub('', rom_name).lower()
        for rom in roms:
            if key == alpha_numeric_pattern.sub('', rom.title).lower():
                print("auto: " + rom_name)
                return rom

        print("")
        for i, rom in enumerate(roms):
            print("[%s] %s" % (i, rom.title))

        index = input("Select a result (or press Enter to skip): ")
        try:
            return roms[int(index)]
        except (ValueError, IndexError):
            return None

    def _try_get_exact_game(self, exact_name, file_name):
        request = _TgDbGetGameRequest(self.platform, exact_name, is_exact=True)
        response = ScraperBase._try_open_stream(request)

        if not response:
            print("failed")
            return None

        game_data = ElementTree.fromstring(response)

        game = game_data.find("Game")

        return None if not game else self._get_rom(self.source, file_name, game)

    def _get_games(self, name, file_name):
        request = _TgDbGetGameRequest(self.platform, name)
        response = ScraperBase._try_open_stream(request)

        if not response:
            return []

        game_data = ElementTree.fromstring(response)

        return [self._get_rom(self.source, file_name, game) for game in game_data.findall("Game")]

    @staticmethod
    def _get_rom(source, file_name, game):
        return Rom(source, file_name, TgDbApiClient._try_find(game, "GameTitle"),
                   TgDbApiClient._try_find(game, "Overview"),
                   TgDbApiClient._get_boxart(game, "front"), TgDbApiClient._get_boxart(game, "back"),
                   TgDbApiClient._try_find(game, "ReleaseDate"), TgDbApiClient._try_find(game, "Publisher"),
                   TgDbApiClient._try_find(game, "Developer"), TgDbApiClient._try_find(game, "Genres/genre"),
                   TgDbApiClient._try_find(game, "Rating"), TgDbApiClient._try_find(game, "Players"))

    @staticmethod
    def _try_find(element, selector):
        node = element.find(selector)
        return "" if node is None else re.sub(r"\n", " ", node.text)

    @staticmethod
    def _get_boxart(element, side):
        node = element.find("Images/boxart[@side='%s']" % side)
        banners_url = "/banners"
        return None if node is None else RetroImage("Boxart[%s]" % side, urllib.parse.urljoin(banners_url, node.text),
                                                    node.attrib["width"], node.attrib["height"],
                                                    urllib.parse.urljoin(banners_url, node.attrib["thumb"]))

    @staticmethod
    def _get_platform(platform_id):
        request = _TgDbGetPlatformRequest(platform_id)
        response = ScraperBase._try_open_stream(request)

        if not response:
            return None

        platform_data = ElementTree.fromstring(response)
        return platform_data.find('Platform/Platform').text

    def __iter__(self):
        return iter(self.roms)
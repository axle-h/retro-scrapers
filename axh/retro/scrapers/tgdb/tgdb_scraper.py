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
    def __init__(self, system, ignore_list, images_path):
        super().__init__("TheGamesDb")
        self.platform = TgDbApiClient._get_platform(system.platform)
        self.roms = [rom for rom in
                     [self._save_image(self._try_scrape(os.path.splitext(file_name)[0].split("(")[0].strip(), file_name)
                                       or self._try_scrape_alternative_name(file_name, system.path),
                                       images_path)
                      for file_name in os.listdir(system.path) if
                      any(file_name.endswith(ext) for ext in system.extensions) and not any(
                          file_name == ignore_file for ignore_file in ignore_list)] if rom is not None]

    def _try_scrape_alternative_name(self, file_name, path):
        while True:
            alternative_name = input("Try a new name for %s (or press Enter to skip): " % file_name)
            if alternative_name is None or alternative_name == "":
                rom_file = os.path.join(path, file_name)
                if input("Delete %s? (Y/n) " % rom_file).strip().lower() != "n":
                    os.remove(rom_file)
                    print("Deleted")
                return None

            rom = self._try_scrape(alternative_name, file_name)
            if rom is not None and input("Ok? (Y/n) ").strip().lower() != "n":
                return rom

    def _try_scrape(self, rom_name, file_name):
        print("[%s]" % file_name, end=" ")

        the_index = rom_name.find(", The")
        if the_index > 0:
            rom_name = "The " + rom_name[:the_index] + rom_name[the_index + 5:]

        exact_rom = self._try_get_exact_game(rom_name, file_name)
        if exact_rom is not None:
            print("exact: " + exact_rom.title)
            return exact_rom

        roms = self._get_games(rom_name, file_name)
        if len(roms) == 0:
            print("failed")
            return None

        alpha_numeric_pattern = re.compile('[\W_]+')
        key = alpha_numeric_pattern.sub('', rom_name).lower()
        for rom in roms:
            if key == alpha_numeric_pattern.sub('', rom.title).lower():
                print("auto: " + rom.title)
                return rom

        if len(roms) == 1:
            if input("single: %s, Ok? (Y/n) " % roms[0].title).strip().lower() != "n":
                return roms[0]
            else:
                return None

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
    def _save_image(rom, path):
        if rom is None:
            return None

        base_name = os.path.join(path, os.path.splitext(rom.file_name)[0])
        image = rom.boxart_front or rom.boxart_back
        rom.image = TgDbApiClient._download_image(image, base_name)
        return rom

    @staticmethod
    def _download_image(image, base_name):
        if image is None or image.url is None:
            return None

        image_file = base_name + "-" + image.description + os.path.splitext(image.url)[1]
        ScraperBase._save_file(_TgDbGetImageRequest(image.url), image_file)

        return image_file

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
        return None if node is None else RetroImage("boxart-%s" % side, urllib.parse.urljoin(banners_url, node.text),
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
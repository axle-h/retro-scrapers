import datetime
import os
from axh.retro.scrapers.models import RetroSystem
from axh.retro.scrapers.tgdb.models import RetroPlatform
from axh.retro.scrapers.tgdb.tgdb_scraper import TgDbApiClient
from xml.etree import ElementTree

__author__ = 'Alex Haslehurst'

_platform_mapping = {
    'amiga': RetroPlatform.Amiga,
    'atari2600': RetroPlatform.Atari2600,
    'atari5200': RetroPlatform.Atari5200,
    'atari7800': RetroPlatform.Atari7800,
    'atarijaguar': RetroPlatform.AtariJaguar,
    'atarijaguarcd': RetroPlatform.AtariJaguarCD,
    'colecovision': RetroPlatform.Colecovision,
    'c64': RetroPlatform.Commodore64,
    'intellivision': RetroPlatform.Intellivision,
    'n64': RetroPlatform.Nintendo64,
    'nes': RetroPlatform.NintendoEntertainmentSystem,
    'gb': RetroPlatform.NintendoGameBoy,
    'gba': RetroPlatform.NintendoGameBoyAdvance,
    'gbc': RetroPlatform.NintendoGameBoyColor,
    'sega32x': RetroPlatform.Sega32X,
    'segacd': RetroPlatform.SegaCD,
    'gamegear': RetroPlatform.SegaGameGear,
    'genesis': RetroPlatform.SegaGenesis,
    'mastersystem': RetroPlatform.SegaMasterSystem,
    'megadrive': RetroPlatform.SegaMegaDrive,
    'saturn': RetroPlatform.SegaSaturn,
    'psx': RetroPlatform.SonyPlaystation,
    'ps2': RetroPlatform.SonyPlaystation2,
    'psp': RetroPlatform.SonyPSP,
    'snes': RetroPlatform.SuperNintendo,
    'pcengine': RetroPlatform.TurboGrafx16}


def scrape_es(path):
    es_systems_cfg = os.path.join(path, "es_systems.cfg")
    images_path = os.path.join(path, "images")

    systems = [RetroSystem(system_node.find("platform").text, _platform_mapping[system_node.find("platform").text],
                           system_node.find("path").text, system_node.find("extension").text.split(" "))
               for system_node in ElementTree.parse(es_systems_cfg).getroot().findall("system")]

    gamelists_path = os.path.join(path, "gamelists")
    if not os.path.exists(gamelists_path):
        os.makedirs(gamelists_path)

    for system in systems:
        system_gamelists_path = os.path.join(gamelists_path, system.platform_name)
        if not os.path.exists(system_gamelists_path):
            os.makedirs(system_gamelists_path)
        gamelists_xml_path = os.path.join(system_gamelists_path, "gameslist.xml")

        if os.path.isfile(gamelists_xml_path):
            game_list_root = ElementTree.parse(gamelists_xml_path).getroot()
            ignore_list = [os.path.basename(game.find("path").text) for game in game_list_root.findall("game")]
        else:
            game_list_root = ElementTree.Element("gameList")
            ignore_list = []

        scraper = TgDbApiClient(system, ignore_list)
        scraper.save_images(os.path.join(images_path, system.platform_name))

        for rom in scraper:
            try:
                release_date = datetime.datetime.strptime(rom.release_date, "%m/%d/%Y")
            except ValueError:
                release_date = datetime.datetime.strptime(rom.release_date, "%Y")

            game = dict_to_elem({"name": rom.title, "desc": rom.description, "image": rom.image, "rating": rom.rating,
                                 "releasedate": release_date.strftime("%Y%m%dT000000"), "developer": rom.developer,
                                 "publisher": rom.publisher, "genre": rom.genre, "players": rom.players,
                                 "path": os.path.join(system.path, rom.file_name)})
            game_list_root.append(game)

        with open(gamelists_xml_path, 'w', encoding='utf-8') as file:
            ElementTree.ElementTree(game_list_root).write(file, encoding='unicode')


def dict_to_elem(dictionary):
    item = ElementTree.Element("game")
    for key in dictionary:
        field = ElementTree.Element(key)
        field.text = dictionary[key]
        item.append(field)
    return item






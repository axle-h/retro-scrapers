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
    'atarilynx': RetroPlatform.AtariLynx,
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
    'pcengine': RetroPlatform.TurboGrafx16,
    'ngpc': RetroPlatform.NeoGeoPocketColor,
    'wonderswancolor': RetroPlatform.WonderSwanColor,
    'pc': RetroPlatform.Pc}

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
        gamelists_xml_path = os.path.join(system_gamelists_path, "gamelist.xml")

        if os.path.isfile(gamelists_xml_path):
            game_list_root = ElementTree.parse(gamelists_xml_path).getroot()
            ignore_list = [os.path.basename(game.find("path").text) for game in game_list_root.findall("game")]
        else:
            game_list_root = ElementTree.Element("gameList")
            ignore_list = []

        system_images_path = os.path.join(images_path, system.platform_name)
        if not os.path.exists(system_images_path):
            os.makedirs(system_images_path)
        scraper = TgDbApiClient(system, ignore_list, system_images_path)

        for rom in scraper:
            try:
                release_date = datetime.datetime.strptime(rom.release_date, "%m/%d/%Y").strftime("%Y%m%dT000000")
            except ValueError:
                try:
                    release_date = datetime.datetime.strptime(rom.release_date, "%m/%d/%Y").strftime("%Y%m%dT000000")
                except ValueError:
                    release_date = ""

            game = _dict_to_elem({"name": rom.title, "desc": rom.description, "image": rom.image, "rating": rom.rating,
                                 "releasedate": release_date, "developer": rom.developer,
                                 "publisher": rom.publisher, "genre": rom.genre, "players": rom.players,
                                 "path": os.path.join(system.path, rom.file_name)})
            game_list_root.append(game)

        game_dict = dict()
        for game in game_list_root.findall("game"):
            game_name = game.find("name").text
            if game_name not in game_dict:
                game_dict[game_name] = game
                continue
            dup_game = game_dict[game_name]
            dup_game_path = dup_game.find("path").text
            game_path = game.find("path").text
            print("[%s] Duplicate" % game_name)
            print("[0] %s" % dup_game_path)
            print("[1] %s" % game_path)
            index = input("Select one to keep (or press Enter to skip): ")
            try:
                index = int(index)
                if index == 0:
                    game_list_root.remove(game)
                    if os.path.isfile(game_path):
                        os.remove(game_path)
                elif index == 1:
                    game_list_root.remove(dup_game)
                    if os.path.isfile(dup_game_path):
                        os.remove(dup_game_path)
            except (ValueError, IndexError):
                pass

        with open(gamelists_xml_path, 'w', encoding='utf-8') as file:
            ElementTree.ElementTree(game_list_root).write(file, encoding='unicode')


def rm_dups_es(path):
    es_systems_cfg = os.path.join(path, "es_systems.cfg")
    images_path = os.path.join(path, "images")




def _dict_to_elem(dictionary):
    item = ElementTree.Element("game")
    for key in dictionary:
        field = ElementTree.Element(key)
        field.text = dictionary[key]
        item.append(field)
    return item






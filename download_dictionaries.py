"""Script de téléchargement et de compilation des dictionnaires Anglais-Français complets.

Auteur  : ValMG
Version : 2.0.0
"""

__author__ = "ValMG"
__version__ = "2.0.0"

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict

WIKTIONARY_URL = "https://raw.githubusercontent.com/pquentin/wiktionary-translations/master/frwiktionary-20140612-euradicfmt.csv"
FREEDICT_URL = "https://raw.githubusercontent.com/freedict/fd-dictionaries/master/eng-fra/eng-fra.tei"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DICTS_DIR = os.path.join(SCRIPT_DIR, "dictionaries")


def download_file(url: str, dest_path: str) -> None:
    """Télécharge un fichier depuis une URL vers un chemin local."""
    print(f"Téléchargement depuis : {url} ...")
    urllib.request.urlretrieve(url, dest_path)
    print(f"Enregistré dans : {dest_path}")


def parse_wiktionary_csv(csv_path: str) -> Dict[str, str]:
    """Extrait les paires Anglais -> Français du dump CSV du Wiktionnaire."""
    translations = {}
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split(";")
            if len(parts) >= 4 and parts[2] == "TR-FR-EN":
                fr_word = parts[0].strip()
                en_word = parts[3].strip()
                if en_word and fr_word:
                    en_lower = en_word.lower()
                    if en_lower not in translations:
                        translations[en_lower] = fr_word
    return translations


def parse_freedict_tei(tei_path: str) -> Dict[str, str]:
    """Extrait les paires Anglais -> Français du fichier TEI XML FreeDict."""
    translations = {}
    try:
        tree = ET.parse(tei_path)
        root = tree.getroot()
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}
        entries = root.findall(".//tei:entry", ns)
        for entry in entries:
            orth = entry.find(".//tei:orth", ns)
            quote = entry.find(".//tei:quote", ns)
            if orth is not None and quote is not None and orth.text and quote.text:
                en_word = orth.text.strip().lower()
                fr_word = quote.text.strip()
                if en_word not in translations:
                    translations[en_word] = fr_word
    except Exception as e:
        print(f"Avertissement lors de la lecture de FreeDict : {e}")
    return translations


def build_full_dictionary():
    """Télécharge les dictionnaires et génère les fichiers compilés."""
    os.makedirs(DICTS_DIR, exist_ok=True)

    wiktionary_raw = os.path.join(DICTS_DIR, "wiktionary_raw.csv")
    freedict_raw = os.path.join(DICTS_DIR, "freedict_raw.tei")

    # 1. Téléchargements
    if not os.path.exists(wiktionary_raw):
        download_file(WIKTIONARY_URL, wiktionary_raw)
    else:
        print(f"Fichier existant : {wiktionary_raw}")

    if not os.path.exists(freedict_raw):
        download_file(FREEDICT_URL, freedict_raw)
    else:
        print(f"Fichier existant : {freedict_raw}")

    # 2. Extraction
    print("Compilation du Wiktionnaire...")
    wikt_dict = parse_wiktionary_csv(wiktionary_raw)
    print(f"-> {len(wikt_dict)} mots extraits du Wiktionnaire.")

    print("Compilation de FreeDict...")
    free_dict = parse_freedict_tei(freedict_raw)
    print(f"-> {len(free_dict)} mots extraits de FreeDict.")

    # 3. Fusion (FreeDict puis Wiktionnaire pour la complétude)
    combined = {**free_dict, **wikt_dict}
    print(f"Total combiné : {len(combined)} mots anglais traduits en français.")

    # 4. Sauvegarde du grand dictionnaire complet
    full_dict_path = os.path.join(DICTS_DIR, "en_fr_full.json")
    with open(full_dict_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Grand dictionnaire sauvegardé dans : {full_dict_path}")

    # 5. Préservation du glossaire prioritaire de jeu
    game_glossary_path = os.path.join(SCRIPT_DIR, "dictionary.json")
    if os.path.exists(game_glossary_path):
        with open(game_glossary_path, "r", encoding="utf-8") as f:
            glossary = json.load(f)
        # On s'assure que les termes spécifiques au jeu restent prioritaires
        merged = {**combined, **glossary}
    else:
        merged = combined

    merged_path = os.path.join(SCRIPT_DIR, "dictionary.json")
    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Dictionnaire principal mis à jour avec {len(merged)} mots : {merged_path}")


if __name__ == "__main__":
    build_full_dictionary()

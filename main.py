"""Point d'entrée du traducteur YAML autonome (V2).

Auteur  : ValMG
Version : 2.0.0
"""

__author__ = "ValMG"
__version__ = "2.0.0"

import argparse
import os
import sys
import time
from translator import OfflineTranslator
from yaml_processor import YamlProcessor


def parse_arguments() -> argparse.Namespace:
    """Analyse les arguments passés en ligne de commande."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description=f"Traducteur YAML autonome v{__version__} par {__author__} (100% hors-ligne, sans API Google)."
    )
    parser.add_argument(
        "-i", "--input",
        default=os.path.join(script_dir, "en.yml"),
        help="Chemin du fichier YAML source (défaut: en.yml)"
    )
    parser.add_argument(
        "-o", "--output",
        default=os.path.join(script_dir, "fr.yml"),
        help="Chemin du fichier YAML de sortie (défaut: fr.yml)"
    )
    parser.add_argument(
        "-d", "--dict",
        default=os.path.join(script_dir, "dictionary.json"),
        help="Chemin du glossaire JSON prioritaire (défaut: dictionary.json)"
    )
    parser.add_argument(
        "--dict-dir",
        default=os.path.join(script_dir, "dictionaries"),
        help="Dossier contenant tous les dictionnaires à charger (.json, .csv, .tsv, .txt, .tei)"
    )
    parser.add_argument(
        "--from-lang",
        default="en",
        help="Code langue source (défaut: en)"
    )
    parser.add_argument(
        "--to-lang",
        default="fr",
        help="Code langue cible (défaut: fr)"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if not os.path.exists(args.input):
        print(f"[Erreur] Le fichier d'entrée '{args.input}' est introuvable.")
        sys.exit(1)

    print("=" * 60)
    print(f"Traducteur YAML v{__version__} - par {__author__}")
    print("Mode : 100% Hors-ligne / Multi-dictionnaires + IA locale")
    print(f"Fichier source : {args.input}")
    print(f"Fichier cible  : {args.output}")
    print(f"Dossier dicos  : {args.dict_dir}")
    print(f"Dico priorité  : {args.dict}")
    print("=" * 60)

    # 1. Initialisation du traducteur
    start_time = time.time()
    translator = OfflineTranslator(
        dictionary_path=args.dict,
        dictionaries_dir=args.dict_dir,
        from_lang=args.from_lang,
        to_lang=args.to_lang
    )

    # 2. Gestion du fichier YAML
    processor = YamlProcessor(translate_fn=translator.translate)

    last_pct = -1

    def progress(current: int, total: int):
        nonlocal last_pct
        pct = int((current / total) * 100) if total > 0 else 100
        if pct != last_pct and pct % 5 == 0:
            last_pct = pct
            print(f"Progression : {pct}% ({current}/{total} entrées)")

    print("\nDébut du traitement...")
    processor.process_file(args.input, args.output, on_progress=progress)

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"Traduction terminée avec succès en {elapsed:.1f} secondes !")
    print(f"Fichier enregistré sous : {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()

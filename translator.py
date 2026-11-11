"""Module de traduction locale hors-ligne avec gestion multi-dictionnaires et protection des balises.

Auteur  : ValMG
Version : 2.0.0
"""

__author__ = "ValMG"
__version__ = "2.0.0"

import json
import os
import re
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET
import argostranslate.package
import argostranslate.translate


class OfflineTranslator:
    """Traducteur autonome utilisant tous les dictionnaires du dossier 'dictionaries/' et Argos Translate."""

    def __init__(
        self,
        dictionary_path: str | None = "dictionary.json",
        dictionaries_dir: str | None = "dictionaries",
        from_lang: str = "en",
        to_lang: str = "fr"
    ):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.dictionary: Dict[str, str] = {}
        self.cache: Dict[str, str] = {}

        # 1. Chargement de tous les dictionnaires
        self.load_all_dictionaries(dictionaries_dir, dictionary_path)

        # 2. Vérification du modèle local
        self._ensure_model_installed()

        # Regex pour protéger les balises Minecraft, variables, codes couleur et commandes
        self.placeholder_regex = re.compile(
            r"(hover:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
            r"|NOPREFIX\|"
            r"|%[^%\r\n]+%"
            r"|\{\$[^}\r\n]+\}"
            r"|&[0-9a-fk-orA-FK-OR]"
            r"|@?https?://[^\s'\"\}\)]+"
            r"|(?<=\s)/[a-zA-Z0-9_\-]+|^/[a-zA-Z0-9_\-]+)",
            re.IGNORECASE
        )

        # Mots / identifiants techniques à ne pas traduire (constantes, sons, items en majuscules)
        self.identifier_regex = re.compile(r"^[A-Z0-9_]{3,}$")

        # Mots grammaticaux et prépositions à ne jamais remplacer en tant que termes isolés dans les phrases
        self.stop_phrases = {
            "the", "a", "an", "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "to the", "of the", "in the", "for the", "on the", "at the", "from the",
            "with the", "into the", "and the", "as the", "is the", "are the", "was the",
            "it", "its", "this", "that", "these", "those", "you", "your", "my", "his", "her",
            "there", "their", "they", "we", "our", "us", "he", "she", "him", "them",
            "and", "or", "but", "so", "if", "as", "is", "are", "was", "were", "be", "been",
            "do", "does", "did", "have", "has", "had"
        }

    def _parse_dictionary_file(self, filepath: str) -> Dict[str, str]:
        """Lit et extrait les paires (anglais -> français) selon l'extension du fichier."""
        ext = os.path.splitext(filepath)[1].lower()
        entries: Dict[str, str] = {}

        if ext == ".json":
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return {str(k).strip().lower(): str(v).strip() for k, v in data.items() if k and v}
            except Exception as e:
                print(f"[Avertissement] Erreur de lecture JSON '{filepath}': {e}")

        elif ext in [".csv", ".tsv"]:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        sep = "\t" if "\t" in line else (";" if ";" in line else ",")
                        parts = [p.strip() for p in line.split(sep)]
                        # Format Wiktionnaire EurADiC: FR;type;TR-FR-EN;EN;type
                        if len(parts) >= 4 and parts[2] == "TR-FR-EN":
                            fr, en = parts[0], parts[3]
                            if en and fr:
                                entries[en.lower()] = fr
                        elif len(parts) >= 2:
                            en, fr = parts[0], parts[1]
                            if en and fr:
                                entries[en.lower()] = fr
            except Exception as e:
                print(f"[Avertissement] Erreur de lecture CSV '{filepath}': {e}")

        elif ext in [".tei", ".xml"]:
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                ns = {"tei": "http://www.tei-c.org/ns/1.0"}
                for entry in root.findall(".//tei:entry", ns):
                    orth = entry.find(".//tei:orth", ns)
                    quote = entry.find(".//tei:quote", ns)
                    if orth is not None and quote is not None and orth.text and quote.text:
                        entries[orth.text.strip().lower()] = quote.text.strip()
            except Exception as e:
                print(f"[Avertissement] Erreur de lecture TEI/XML '{filepath}': {e}")

        elif ext in [".txt"]:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        for sep in ["->", "=>", "=", ":"]:
                            if sep in line:
                                parts = line.split(sep, 1)
                                en, fr = parts[0].strip().lower(), parts[1].strip()
                                if en and fr:
                                    entries[en] = fr
                                break
            except Exception as e:
                print(f"[Avertissement] Erreur de lecture TXT '{filepath}': {e}")

        return entries

    def load_all_dictionaries(self, dictionaries_dir: str | None, root_dict_path: str | None) -> None:
        """Parcourt le dossier 'dictionaries/' et charge tous les fichiers trouvés."""
        loaded_files = 0

        # 1. Parcours de tous les fichiers du dossier dictionaries/
        if dictionaries_dir and os.path.isdir(dictionaries_dir):
            file_names = sorted(os.listdir(dictionaries_dir))
            for filename in file_names:
                full_path = os.path.join(dictionaries_dir, filename)
                if os.path.isfile(full_path):
                    file_entries = self._parse_dictionary_file(full_path)
                    if file_entries:
                        self.dictionary.update(file_entries)
                        loaded_files += 1

        # 2. Chargement du dictionnaire racine (prioritaire)
        if root_dict_path and os.path.exists(root_dict_path):
            root_entries = self._parse_dictionary_file(root_dict_path)
            if root_entries:
                self.dictionary.update(root_entries)
                loaded_files += 1

        print(f"[Dictionnaires] {len(self.dictionary):,} mots chargés depuis {loaded_files} fichier(s).")

    def _ensure_model_installed(self) -> None:
        """Vérifie la présence du modèle linguistique local, sinon le télécharge."""
        installed = argostranslate.translate.get_installed_languages()
        has_pair = any(
            lang.code == self.from_lang and any(t.to_lang.code == self.to_lang for t in lang.translations_from)
            for lang in installed
        )
        if not has_pair:
            print(f"[Traducteur] Téléchargement initial du modèle local {self.from_lang} -> {self.to_lang}...")
            argostranslate.package.update_package_index()
            available = argostranslate.package.get_available_packages()
            pkg = next((p for p in available if p.from_code == self.from_lang and p.to_code == self.to_lang), None)
            if pkg:
                pkg_path = pkg.download()
                argostranslate.package.install_from_path(pkg_path)
                print("[Traducteur] Modèle installé avec succès.")
            else:
                raise RuntimeError(f"Modèle introuvable pour {self.from_lang} -> {self.to_lang}")

    def _match_casing(self, original: str, translated: str) -> str:
        """Applique la casse de la source au mot traduit (majuscule initiale ou tout en minuscules)."""
        if original.isupper() and len(original) > 1:
            return translated.upper()
        if original[0].isupper() and not original.islower():
            return translated[0].upper() + translated[1:]
        return translated

    def _has_translatable_words(self, text: str) -> bool:
        """Vérifie si le texte contient au moins un mot alphabétique à traduire."""
        stripped = self.placeholder_regex.sub(" ", text)
        words = re.findall(r"\b[A-Za-z]{2,}\b", stripped)
        return len(words) > 0

    def _clean_french_grammar(self, text: str) -> str:
        """Nettoie les erreurs de contraction et d'élision françaises fréquentes."""
        # Contractions grammaticales obligatoires
        text = re.sub(r"\bà\s+le\b", "au", text, flags=re.IGNORECASE)
        text = re.sub(r"\bà\s+les\b", "aux", text, flags=re.IGNORECASE)
        text = re.sub(r"\bde\s+le\b", "du", text, flags=re.IGNORECASE)
        text = re.sub(r"\bde\s+les\b", "des", text, flags=re.IGNORECASE)
        # Correction des doubles apostrophes ou espaces d'élision
        text = re.sub(r"l''\s*", "l'", text)
        text = re.sub(r"d''\s*", "d'", text)
        # Corrige "à l' [consonne]" en "au [consonne]" (ex: "à l' royaume" -> "au royaume")
        text = re.sub(r"\bà\s+l'([bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ][a-zA-Z]+)", r"au \1", text)
        text = re.sub(r"\bà\s+l'\s+([bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ][a-zA-Z]+)", r"au \1", text)
        return text

    def _find_matching_phrases(self, text: str) -> List[str]:
        """Détecte rapidement les expressions multi-mots du dictionnaire présentes dans le texte via n-grammes."""
        words = re.findall(r"\b[A-Za-z0-9_\-]+\b", text)
        matched = set()
        for n in range(min(5, len(words)), 1, -1):
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i:i + n]).lower()
                if ngram in self.dictionary and ngram not in self.stop_phrases:
                    matched.add(ngram)
        return sorted(matched, key=len, reverse=True)

    def translate(self, text: str) -> str:
        """Traduit un texte en protégeant les balises et en consultant le glossaire."""
        if not text or not isinstance(text, str):
            return text

        if text in self.cache:
            return self.cache[text]

        clean = text.strip()
        if self.identifier_regex.match(clean):
            self.cache[text] = text
            return text

        lower_clean = clean.lower()
        if lower_clean in self.dictionary:
            dict_translation = self.dictionary[lower_clean]
            result = text.replace(clean, self._match_casing(clean, dict_translation))
            self.cache[text] = result
            return result

        if not self._has_translatable_words(text):
            self.cache[text] = text
            return text

        # 1. Masquage des balises et variables
        tags: List[str] = []

        def mask_tag(match: re.Match) -> str:
            tags.append(match.group(0))
            return f"<t{len(tags) - 1}/>"

        masked_text = self.placeholder_regex.sub(mask_tag, text)

        # 2. Masquage des expressions du dictionnaire détectées dans la phrase (via n-grammes)
        glossary_replacements: List[Tuple[str, str]] = []
        matching_phrases = self._find_matching_phrases(masked_text)

        for term in matching_phrases:
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            if pattern.search(masked_text):
                replacement_tag = f"<g{len(glossary_replacements)}/>"
                glossary_val = self.dictionary[term]

                def replace_term(m: re.Match) -> str:
                    glossary_replacements.append((replacement_tag, self._match_casing(m.group(0), glossary_val)))
                    return replacement_tag

                masked_text = pattern.sub(replace_term, masked_text)

        # 3. Traduction neuronale locale
        try:
            translated = argostranslate.translate.translate(masked_text, self.from_lang, self.to_lang)
        except Exception:
            translated = masked_text

        # 4. Restauration des termes du dictionnaire
        for tag, replacement in glossary_replacements:
            pattern = re.compile(rf"{re.escape(tag)}", re.IGNORECASE)
            translated = pattern.sub(lambda _: replacement, translated)

        # 5. Restauration des balises protégées
        for i, tag in enumerate(tags):
            pattern = re.compile(rf"<t{i}\s*/>", re.IGNORECASE)
            translated = pattern.sub(lambda _: tag, translated)

        # 6. Nettoyage grammatical français
        if self.to_lang == "fr":
            translated = self._clean_french_grammar(translated)

        self.cache[text] = translated
        return translated

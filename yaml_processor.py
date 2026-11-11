"""Module de traitement et de parcours récursif des fichiers YAML.

Auteur  : ValMG
Version : 2.0.0
"""

__author__ = "ValMG"
__version__ = "2.0.0"

from typing import Any, Callable
import ruamel.yaml
from ruamel.yaml.scalarstring import (
    DoubleQuotedScalarString,
    FoldedScalarString,
    LiteralScalarString,
    SingleQuotedScalarString,
)


class YamlProcessor:
    """Charge, traduit récursivement et sauvegarde un fichier YAML tout en préservant commentaires et structure."""

    def __init__(self, translate_fn: Callable[[str], str]):
        self.translate_fn = translate_fn
        self.yaml = ruamel.yaml.YAML(typ="rt")
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.width = 4096  # Évite les retours à la ligne intempestifs sur les longues phrases

    def _preserve_scalar_style(self, original: Any, new_text: str) -> Any:
        """Conserve le style de guillemets ou de bloc multiligne d'origine."""
        if isinstance(original, LiteralScalarString):
            return LiteralScalarString(new_text)
        if isinstance(original, FoldedScalarString):
            return FoldedScalarString(new_text)
        if isinstance(original, DoubleQuotedScalarString):
            return DoubleQuotedScalarString(new_text)
        if isinstance(original, SingleQuotedScalarString):
            return SingleQuotedScalarString(new_text)

        style = getattr(original, "style", None)
        if style == "'":
            return SingleQuotedScalarString(new_text)
        if style == '"':
            return DoubleQuotedScalarString(new_text)
        return new_text

    def _process_node(self, node: Any, progress_callback: Callable[[], None] | None = None) -> Any:
        """Parcourt récursivement l'arbre YAML pour traduire uniquement les chaînes de texte."""
        if isinstance(node, dict):
            for key in list(node.keys()):
                val = node[key]
                if isinstance(val, (dict, list)):
                    self._process_node(val, progress_callback)
                elif isinstance(val, str) and val.strip():
                    translated = self.translate_fn(val)
                    node[key] = self._preserve_scalar_style(val, translated)
                    if progress_callback:
                        progress_callback()
        elif isinstance(node, list):
            for i in range(len(node)):
                item = node[i]
                if isinstance(item, (dict, list)):
                    self._process_node(item, progress_callback)
                elif isinstance(item, str) and item.strip():
                    translated = self.translate_fn(item)
                    node[i] = self._preserve_scalar_style(item, translated)
                    if progress_callback:
                        progress_callback()
        return node

    def count_translatable_strings(self, node: Any) -> int:
        """Compte le nombre de valeurs textuelles à traduire pour la barre de progression."""
        count = 0
        if isinstance(node, dict):
            for val in node.values():
                if isinstance(val, (dict, list)):
                    count += self.count_translatable_strings(val)
                elif isinstance(val, str) and val.strip():
                    count += 1
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, (dict, list)):
                    count += self.count_translatable_strings(item)
                elif isinstance(item, str) and item.strip():
                    count += 1
        return count

    def process_file(self, input_path: str, output_path: str, on_progress: Callable[[int, int], None] | None = None) -> None:
        """Lit le fichier d'entrée, traduit les valeurs et écrit le résultat."""
        with open(input_path, "r", encoding="utf-8") as f_in:
            data = self.yaml.load(f_in)

        total_strings = self.count_translatable_strings(data)
        completed = 0

        def step():
            nonlocal completed
            completed += 1
            if on_progress:
                on_progress(completed, total_strings)

        self._process_node(data, progress_callback=step)

        with open(output_path, "w", encoding="utf-8") as f_out:
            self.yaml.dump(data, f_out)

"""Owned presentation messages for the Critic. Wire values are never translated."""
from __future__ import annotations

import argparse
import json
import os
import string
import sys
from contextvars import ContextVar
from pathlib import Path

CATALOG_DIRECTORY = Path(__file__).resolve().parent / "locales"
LANGUAGES = ("es", "en")
_language: ContextVar[str | None] = ContextVar("critic_language", default=None)


def set_language(language: str) -> str:
    """Select presentation language; invalid preferences visibly fall back to Spanish."""
    if language not in LANGUAGES:
        print(f"CRITIC_LANG: unsupported language {language!r}; using es / idioma no admitido; se usa es", file=sys.stderr)
        language = "es"
    _language.set(language)
    return language


def get_language() -> str:
    selected = _language.get()
    return selected if selected is not None else set_language(os.environ.get("CRITIC_LANG", "es"))


def load_catalog(language: str) -> dict[str, str]:
    if language not in LANGUAGES:
        raise ValueError(f"Unsupported catalogue: {language}")
    data = json.loads((CATALOG_DIRECTORY / f"{language}.json").read_text(encoding="utf-8"))
    if not isinstance(data, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in data.items()):
        raise ValueError(f"Invalid catalogue: {language}")
    return data


def translate(key: str, **parameters: object) -> str:
    """Fail on missing translations rather than disguising incomplete localization."""
    return load_catalog(get_language())[key].format(**parameters)


def validate_catalogs() -> int:
    catalogs = {language: load_catalog(language) for language in LANGUAGES}
    if catalogs["en"].keys() != catalogs["es"].keys():
        raise ValueError("Catalogue keys differ")
    formatter = string.Formatter()
    for key in catalogs["en"]:
        placeholders = [sorted((field, spec, conversion) for _, field, spec, conversion in formatter.parse(catalogs[language][key]) if field is not None) for language in LANGUAGES]
        if placeholders[0] != placeholders[1]:
            raise ValueError(f"Catalogue placeholders differ: {key}")
    return len(catalogs["en"])


def configure_arguments(arguments: list[str] | None = None) -> list[str]:
    """Extract --lang anywhere, leaving the product's original argument contract intact."""
    pending = list(sys.argv[1:] if arguments is None else arguments)
    remaining: list[str] = []
    selected = os.environ.get("CRITIC_LANG", "es")
    index = 0
    while index < len(pending):
        item = pending[index]
        if item == "--lang":
            if index + 1 == len(pending) or pending[index + 1].startswith("--"):
                print("--lang requires en|es / --lang requiere en|es", file=sys.stderr)
                raise SystemExit(2)
            index += 1
            selected = pending[index]
        elif item.startswith("--lang="):
            selected = item.partition("=")[2]
        else:
            remaining.append(item)
        index += 1
    set_language(selected)
    return remaining


class LocalizedArgumentParser(argparse.ArgumentParser):
    """Localize parser headings without rewriting user input or dependency errors."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("add_help", False)
        super().__init__(*args, **kwargs)
        self._positionals.title = translate("parser.positionals")
        self._optionals.title = translate("parser.options")
        self.add_argument("-h", "--help", action="help", help=translate("parser.help"))
        self.add_argument("--lang", metavar="en|es", help=translate("parser.language"))

    def format_usage(self):
        return self._localized_usage(super().format_usage())

    def format_help(self):
        return self._localized_usage(super().format_help())

    @staticmethod
    def _localized_usage(value):
        return translate("parser.usage") + value[len("usage: "):] if value.startswith("usage: ") else value

    def error(self, message):
        # argparse's original diagnostic is preserved, including quoted user input.
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: {translate('parser.error')}: {message}\n")

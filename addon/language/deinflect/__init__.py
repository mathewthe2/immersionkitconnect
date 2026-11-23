# -*- coding: utf-8 -*-
import re

from . import ja, en, yomitan_js

# ── All supported languages ────────────────────────────────────────────────
# fmt: (code, display_label, script_family)
ALL_LANGS = [
    ("ja", "Japanese (日本語)",            "cjk"),
    ("en", "English",                     "latin"),
]
ALL_LANG_CODES = {c for c, *_ in ALL_LANGS}
INFLECTED_LANGS = {
    "ja", "en"
}

# Latin-script langs (share same character set, auto-detect can't distinguish)
LATIN_LANGS = {
    "en"
}

# candidates(lang, surface) -> list[str]
def candidates(lang: str, surface: str):
    if not surface:
        return []
    base = None
    if lang == "ja":
        base = ja.candidates(surface)
    elif lang == "en":
        base = en.candidates(surface)
    else:
        base = [surface]
    if lang == "en":
        return base
    return yomitan_js.enrich(lang, surface, base)

# keep_char(lang, ch) -> bool
def keep_char(lang: str, ch: str) -> bool:
    if lang == "ja":
        return ja.keep_char(ch)
    if lang in LATIN_LANGS:
        return ch.isalpha() and (ch.isascii() or ord(ch) < 0x0300)
    # zh default: CJK BMP + Extensions
    cp = ord(ch)
    return (
        (0x3400 <= cp <= 0x9FFF) or
        (0x20000 <= cp <= 0x2EBEF) or
        (0x30000 <= cp <= 0x3134F)
    )

def pick_seed(lang: str, text: str) -> str:
    text = text or ""
    if lang == "en" or lang in LATIN_LANGS:
        return en.pick_word(text)
    seed = "".join(c for c in text if keep_char(lang, c))
    if not seed and lang == "ja":
        seed = "".join(c for c in text if keep_char("zh", c))
    return seed
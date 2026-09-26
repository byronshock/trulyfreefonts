"""Family ids and name helpers. Frozen contract.

- ``match_key`` and ``search_key`` come from ``keys`` (re-exported here).
- ``mint_id`` makes the stable family id, once, at first sighting; the id never
  changes afterwards, even when the family is renamed (methodology §2).
- ``gf_dir_slug`` is the google/fonts folder name of a family.
- ``strip_style`` drops trailing style words from a font or PostScript name.
- ``NERD_SUFFIX`` finds a Nerd Fonts build suffix at the end of a name.

Nothing here guesses: every function is a fixed text rule, and matching stays
exact (design-m1: "matching never guesses").
"""

import re
import unicodedata

from tff_catalog.keys import match_key, search_key

__all__ = [
    "ID_PATTERN",
    "NERD_SUFFIX",
    "STYLE_WORDS",
    "gf_dir_slug",
    "match_key",
    "mint_id",
    "search_key",
    "slugify",
    "strip_style",
]

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Latin letters that have no decomposition to a base letter.
_TRANSLIT = str.maketrans(
    {
        "ß": "ss",
        "ẞ": "SS",
        "ł": "l",
        "Ł": "L",
        "ø": "o",
        "Ø": "O",
        "æ": "ae",
        "Æ": "AE",
        "œ": "oe",
        "Œ": "OE",
        "đ": "d",
        "Đ": "D",
        "ð": "d",
        "Ð": "D",
        "þ": "th",
        "Þ": "TH",
        "ħ": "h",
        "Ħ": "H",
        "\u0131": "i",  # dotless i
        "ŀ": "l",
        "Ŀ": "L",
    }
)


def _ascii_fold(name: str) -> str:
    text = unicodedata.normalize("NFKC", name).translate(_TRANSLIT)
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def slugify(name: str) -> str:
    """Lower-case ASCII words joined by hyphens: ``"Łódź Sans 3" -> "lodz-sans-3"``.

    Non-Latin letters are dropped; an all-dropped name gives ``""``.
    """
    return re.sub(r"[^a-z0-9]+", "-", _ascii_fold(name)).strip("-")


def mint_id(name: str, taken: set[str] | frozenset[str]) -> str:
    """Mint a new family id from ``name`` that is not in ``taken``.

    The id is ``slugify(name)`` (``"family"`` if that is empty), with ``-2``,
    ``-3`` ... appended on a clash. ``taken`` is not modified: the caller records
    the new id in ``state/ids.json``. Ids match ``ID_PATTERN``.
    """
    base = slugify(name) or "family"
    if base not in taken:
        return base
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    return f"{base}-{n}"


def gf_dir_slug(name: str) -> str:
    """Return the google/fonts folder slug: ASCII-folded, lower case, letters and digits only.

    ``"Noto Sans JP" -> "notosansjp"``, ``"Caacupé One" -> "caacupeone"``.
    """
    return re.sub(r"[^a-z0-9]+", "", _ascii_fold(name))


STYLE_WORDS = frozenset(
    {
        "thin",
        "hairline",
        "extralight",
        "ultralight",
        "light",
        "book",
        "regular",
        "normal",
        "roman",
        "medium",
        "semibold",
        "demibold",
        "bold",
        "extrabold",
        "ultrabold",
        "black",
        "heavy",
        "extrablack",
        "ultrablack",
        "italic",
        "oblique",
    }
)
# Only stripped together with a style word after them ("Extra Light").
_MODIFIERS = frozenset({"extra", "ultra", "semi", "demi"})
_CAMEL = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")


# PostScript style parts may be abbreviated ("SourceSansPro-BoldIt").
_PS_ABBREVIATIONS = frozenset({"it"})


def _is_style(token: str, *, postscript: bool = False) -> bool:
    words = STYLE_WORDS | _PS_ABBREVIATIONS if postscript else STYLE_WORDS
    if token.lower().replace("-", "").replace("_", "") in words:
        return True
    parts = [p.lower() for p in _CAMEL.findall(token)]
    return (
        bool(parts)
        and all(p in words or p in _MODIFIERS for p in parts)
        and any(p in words for p in parts)
    )


def strip_style(name: str) -> str:
    """Drop trailing style words, keeping at least one word.

    ``"Inter Bold Italic" -> "Inter"``, ``"Fira Sans Extra Light" -> "Fira Sans"``,
    ``"JetBrainsMono-BoldItalic" -> "JetBrainsMono"`` (PostScript form).
    Width words (Condensed, Narrow) are kept: they name separate families.
    Callers try the exact name first, since ``"Archivo Black"`` is a family.
    """
    text = " ".join(name.split())
    if " " not in text and "-" in text:
        family, _, style = text.rpartition("-")
        if family and _is_style(style, postscript=True):
            return family
        return text
    tokens = text.split(" ")
    stripped_style = False
    while len(tokens) > 1:
        last = tokens[-1]
        if _is_style(last):
            tokens.pop()
            stripped_style = True
        elif stripped_style and last.lower() in _MODIFIERS:
            tokens.pop()
        else:
            break
    return " ".join(tokens)


# "JetBrainsMono Nerd Font Mono", "Hack NF", "FiraCode NFM", "IosevkaTermNerdFontPropo".
# Group "build" is the suffix as written; callers map it to an alias detail
# (nerd, nf, nfm, nfp, propo) and keep the base name before match.start().
# "NF" counts only after a separator, a lower-case letter or a digit, so "CONF"
# is not a Nerd build. The suffix must end the name: strip "CN" (CJK) first.
NERD_SUFFIX: re.Pattern[str] = re.compile(
    r"[\s_-]*(?P<build>(?i:nerd[\s_-]*font(?:[\s_-]*(?:mono|propo))?)|(?<=[\s_a-z0-9-])NF[MP]?)\Z"
)

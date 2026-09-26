"""Stage "specimens": SVG previews of each font (Milestone 2 step 5, design-m2 §3). Owner: agent A5.

It runs inside ``tff-catalog refresh`` between "export" and "export-site"
(design-m1 gap G9): for each ``preview_ok`` font it fetches ``font_file.url``
into ``~/.cache/tff/fonts/<sha256>``, checks the sha256, renders
``build/specimens/<id>.svg`` with HarfBuzz and records ``preview {path, sha256}``.
The SVGs are committed, because ``tff-site build`` makes no network requests.
"""

RENDERER_VERSION = 1  # bump when output bytes change on purpose
UNITS_PER_EM = 256  # integer coordinate grid
NAME_SIZE_EM = 1.0  # line 1: the family name
SAMPLE_SIZE_EM = 0.6  # line 2: the sample
SAMPLE = "Zażółć gęślą jaźń · Příliš žluťoučký kůň"  # M2 batch 2 (rec)
BASIC_SAMPLE = "Sphinx of black quartz, judge my vow"  # fallback for basic-Latin fonts
DEFAULT_WEIGHT = 400.0  # variable fonts: wght=400 if the axis allows it, else the default instance

# Budget (tff-catalog specimens --check).
SMALL_GZIP_BYTES = 5 * 1024  # at least half the files at or under this, gzip -9
MAX_FILE_BYTES = 30 * 1024  # larger files are re-rendered with the name only
MAX_TOTAL_BYTES = 10 * 1024 * 1024

FLAGS = ("specimen_failed", "specimen_name_only", "specimen_hash_mismatch")

"""Command line entry point for ``tff-site``.

Placeholder until the Milestone 2 contracts replace it with the frozen
subcommands (build, serve, check, pack, fetch-fonts, validate, linkcheck).
Contract kept from now on: ``main(argv) -> int``, where ``argv`` defaults to
``sys.argv[1:]`` and the return value is the exit code.
"""

import sys

from tff_catalog import __version__

USAGE = """\
usage: tff-site [-h] [--version] <command> [options]

Builds trulyfreefonts.com from the catalog.

No commands exist yet; they arrive with Milestone 2.

options:
  -h, --help  show this message and exit
  --version   print the version and exit
"""


def main(argv: list[str] | None = None) -> int:
    """Run tff-site with ``argv`` and return the process exit code."""
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] in ("-h", "--help"):
        print(USAGE, end="")
        return 0
    if args and args[0] == "--version":
        print(f"tff-site {__version__}")
        return 0
    if args:
        print(f"tff-site: unknown command {args[0]!r}", file=sys.stderr)
    print(USAGE, end="", file=sys.stderr)
    return 2

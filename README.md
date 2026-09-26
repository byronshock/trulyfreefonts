# trulyfreefonts

This project builds a ranked list of the most popular truly free Latin fonts and publishes it at [trulyfreefonts.com](https://trulyfreefonts.com). A font counts as truly free only if its license allows use in all personal and commercial projects, with no use restrictions. Display-only, personal-use-only, demo and non-commercial licenses don't qualify. The first release is the filterable list. A later release compares the list with the fonts a visitor already has and shows the ones they don't have.

## Status

Milestone 1, the catalog pipeline, is in progress. Until the first release, trulyfreefonts.com shows a placeholder page.

- Plan: [docs/roadmap.md](docs/roadmap.md) and the milestone checklists, starting with [docs/milestone-1.md](docs/milestone-1.md).
- How fonts are ranked: [docs/ranking-methodology.md](docs/ranking-methodology.md).
- Settled decisions: [AUTHORITY.md](AUTHORITY.md).

## Development

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.14 if you don't have it.

```sh
uv sync                     # create .venv with the locked dependencies
uv run pytest               # run the tests
uv run tff-catalog --help   # the catalog command line
uv run ruff check           # lint
uv run ruff format --check  # formatting
```

CI runs the lint, the tests and a secret scan (gitleaks) on every pull request. It skips tests marked `network`, `store` or `browser`, which need the network, the private snapshot store or a browser.

## Licenses

- **Code:** MIT. See [LICENSE](LICENSE).
- **Catalog data** (`build/*.json` and `data/`): CC BY-SA 4.0. This is **provisional** until the audit of each source's terms (Milestone 1, step 3). See [LICENSE-DATA](LICENSE-DATA).
- **Fonts** are not part of this project's licenses. Each font keeps its own.

## Source credits

The rankings are built from data that others publish. Thank you to all of them.

The license column shows what we know today. The step 3 audit will confirm each entry. "Terms under review" means we have found no license for the data yet, or its terms need a ruling.

**Candidate fonts and license facts**

| Source | What we use | License or terms |
|---|---|---|
| [Google Fonts](https://github.com/google/fonts) repository | family list, metadata, licenses | each family folder is under its font's license (OFL 1.1, Apache 2.0 or UFL) |
| [Fontsource](https://fontsource.org) registry ([repository](https://github.com/fontsource/fontsource)) | non-Google fonts, font facts | MIT |
| [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) `fonts.json` | the original fonts behind Nerd Font builds | MIT |
| [Homebrew casks](https://github.com/Homebrew/homebrew-cask) | fonts packaged for macOS | BSD-2-Clause |
| [Fontist formulas](https://github.com/fontist/formulas) | license facts only | terms under review (no license file) |
| [Debian copyright files](https://sources.debian.org) | license cross-checks, identifiers only | terms under review (each file belongs to its package) |
| [Google Fonts glyph sets](https://github.com/googlefonts/glyphsets) | the Latin coverage test | Apache 2.0 |
| Foundries: [The League of Moveable Type](https://www.theleagueofmoveabletype.com), [Velvetyne](https://velvetyne.fr), [Collletttivo](https://www.collletttivo.it), [Open Foundry](https://open-foundry.com) and others | extra candidate fonts | terms under review |

**Desktop installs**

| Source | What we use | License or terms |
|---|---|---|
| [Homebrew analytics](https://formulae.brew.sh/analytics/) | font cask installs on macOS, 365 days | terms under review (no data license stated) |
| [Arch Linux pkgstats](https://pkgstats.archlinux.de) | share of Arch systems with each font package | terms under review (no data license stated) |
| Package databases of [Arch Linux](https://archlinux.org/packages/), [CachyOS](https://cachyos.org) and [EndeavourOS](https://endeavouros.com) | which packages pull fonts in | terms under review |
| [Debian popularity contest](https://popcon.debian.org) | installs reported by Debian-based systems | MIT (Expat) or GPL-2.0-or-later, per [Debian's web license](https://www.debian.org/license) |
| [Debian package lists](https://deb.debian.org/debian/) | which packages pull fonts in | terms under review |
| GitHub release downloads, through the [GitHub API](https://docs.github.com/en/rest/releases) | downloads of fonts whose main channel is GitHub | terms under review ([GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service)) |
| [Nerd Fonts releases](https://github.com/ryanoasis/nerd-fonts/releases) | patched-build downloads, credited to the original font | terms under review (as for GitHub) |
| [Chocolatey](https://community.chocolatey.org) | download counts on Windows | terms under review: its terms forbid automated access, so it is not collected unless that changes |

**Fonts used in websites, code and apps**

| Source | What we use | License or terms |
|---|---|---|
| [Fonts Over Time](https://fontsovertime.com) | fonts on about 10,000 homepages | terms under review (no license file; its data page says the data is free to download and reuse, and asks for a link back) |
| [Web Almanac 2025](https://almanac.httparchive.org) | pages declaring each font | Apache 2.0 |
| [Google Fonts](https://fonts.google.com) | views over one year | terms under review ([Google Terms of Service](https://policies.google.com/terms)) |
| [npm](https://www.npmjs.com) downloads of `@fontsource`, `@fontsource-variable` and `@expo-google-fonts` packages | code and app use | terms under review (npm's terms say nothing specific about download counts) |
| [ecosyste.ms](https://packages.ecosyste.ms) | GitHub projects that depend on each package | CC BY-SA 4.0 |
| [jsDelivr](https://www.jsdelivr.com) hits, through [Fontsource](https://fontsource.org)'s stats | CDN use | terms under review (no data license stated) |
| Uses of [google_fonts for Flutter](https://pub.dev/packages/google_fonts) in public code | app use; not collected in the first build | terms under review |

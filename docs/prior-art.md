# Prior art: tools that show which popular free fonts you don't have

Survey date: 2026-09-25. Question: does anything already do what this project plans (see [AUTHORITY.md](../AUTHORITY.md))? That is: detect the fonts a user has installed, compare them with a popularity-ranked list of truly free Latin fonts, show the ones they're missing, and link to official downloads.

**Method.** Five research agents each covered one area: direct prior art, GUI font managers, CLI and package managers, browser-side detection, and catalogs and licenses. A verification workflow of 89 agents then:

- tried to disprove the claims about the closest tools, checking source code, live JavaScript bundles and changelogs rather than marketing copy;
- ran five new search angles: new web apps, GitHub scripts, non-English ecosystems, plugins and mobile, and 2025–26 font managers;
- ran a completeness critic;
- checked every new candidate that scored 2 or more.

I also queried the Fontsource, Google Fonts, Fontshare and Homebrew APIs directly, and read the ITF license text shipped with the fonts.

**Scoring.** Each tool scores one point for each of the four parts of the idea, so 0–4:

1. It detects installed fonts.
2. It ranks or sorts by popularity.
3. It has a view that shows only the fonts you don't have.
4. Its catalog is limited to, or can be filtered to, truly free licenses.

Scores below are the checkers' verified scores.

## Bottom line

1. **Nobody offers this as a web page.** FontVS and wordmark.it detect installed fonts in the browser, and some pickers load a popularity-sorted Google Fonts list next to local fonts. None of them ever compares the two lists.
2. **The desktop version does exist, in narrow form.** A few small native apps sort Google Fonts by popularity and hide the ones you have. The oldest is **fontfinder** (Linux; its Popular sort plus an unticked "Show Installed" box gives exactly that view). Newer ones are **font-file-installer** (macOS, July 2026) and the iOS app **Fonts: Install New Fonts**. All of them only recognise fonts *they installed themselves* or fonts in one user folder. Fonts installed any other way show up as missing.
3. **What's genuinely unclaimed:**
   - detecting fonts installed by any means, combined with a missing-only view;
   - matching names across renames and patched builds;
   - a ranking that isn't just Google's own popularity field;
   - a Latin-only ranking;
   - a license rule as strict as AUTHORITY Rule 1, plus a redistributable toggle;
   - links to official downloads.

   Every popularity sort found reuses Google's rank, and fonts outside Google Fonts are sorted last or alphabetically.
4. **Anyone could build this quickly.** Many of the closest tools are small, often AI-assisted projects from 2026 with 0–20 stars: OpenFont Manager (created 2026-09-12), font-file-installer, fontina, Fonts Over Time and others. The part that's hard to copy is the data: ranking, aliases and license vetting.

## Nearest neighbours

| Tool | Kind | Installed detection | Popularity | Missing-only | Truly free | Status (2026-09-25) | Score |
|---|---|---|---|---|---|---|---|
| [fontfinder](https://github.com/mmstick/fontfinder) (System76) | Linux GTK app | Own downloads only | Popular sort via Google's API (default is Trending) | **Yes**: untick "Show Installed" | Google Fonts only | Unmaintained since 2023-04; Flathub end-of-life 2026-01-28 | 3.5 |
| [font-file-installer](https://github.com/srihas115/font-file-installer) | macOS app | `~/Library/Fonts` + own record; misses `/Library` and `/System` | "Most Popular" option (default A–Z); frozen snapshot | **Yes**: installed families always hidden | Google + Fontsource | Dormant since 2026-07; 1 star | 3.5 |
| [OpenFont Manager](https://github.com/stoatworks-labs/openfont-manager) | Web + Tauri desktop | Desktop only, system-wide via font-kit; the web page detects nothing | **Default** "Most popular" (Google rank; Fontsource fonts last) | No, badge only | **License filter** + open-license allowlist | Created 2026-09-12; no desktop binaries published | 3 (desktop) / 2 (web) |
| [Fonts: Install New Fonts](https://apps.apple.com/us/app/fonts-install-new-fonts/id1509011708) | iOS app | Own installs only | No | **Yes**: All / Installed / Not Installed | Google Fonts only | Last update 2022-01 | 3 |
| [Font Manager](https://github.com/FontManager/font-manager) | Linux GTK app | Knows all installed fonts, but the Google catalog checks only its own downloads | Name / Newest / Most Popular / Trending | No; a PR attempt was closed unmerged | Google Fonts only; groups *installed* fonts by license | Dormant since 2025-09 | 2.5–3 |
| [chocolateimage/fontviewer](https://github.com/chocolateimage/fontviewer) | Linux GTK app | **System-wide via fontconfig** | Google's `defaultSort` (a popularity/trending/new blend), fixed | No, badge only | Google Fonts only | v1.3.0, 2026-06 | 2.5 |
| [Fontastic](https://apps.apple.com/us/app/fontastic-install-fonts/id1537294729) | iOS app | Own installs only | Popularity / Trending sort | No; filter shows installed only | Open-source catalog | Active (4.1.2, 2026-09-11) | 2.5 |
| [FontVS](https://fontvs.com/) | Web app | Local Font Access (Chromium desktop); other browsers get a hard-coded OS list | No; A–Z only | No; never compares its lists | Google source view only | Live, closed source, "work in progress" | 1.5–2 |
| [wordmark.it](https://wordmark.it/) | Web app | Local Font Access + Chromium extension | No; A–Z / random | No; the Google catalog view is separate (Pro) | Google catalog | Active, paid tiers | 2 |
| [FontGet](https://github.com/Graphixa/FontGet) | CLI (Go) | Two font folders per OS; misses `/usr/share/fonts` on Linux | **Default** popularity score (a search heuristic, not usage data) in `browse` | No | Mixed; includes Fontshare, shows licenses | Very active (v2.7.0, 2026-09-24) | 2 |
| [Fontist](https://www.fontist.org/) | CLI + web registry | Hard-coded search paths; `list` marks "installed" only for its own directory | No | Not usable | Web registry has **License and Redistributable filters** | Maintained | 2 |
| [Fonts.Free](https://fonts.free/) | Web catalog | None | Default "Popular" (Google order; 196 non-Google fonts last) | n/a | License filter pages, but submissions accept personal-use licenses | Launched July 2026 | 2 |
| [Lipi](https://github.com/shonebinu/Lipi) | Linux GTK4 app | **System-wide via Pango** ("System" badge) | No; alphabetical | No | Google, license shown per font | Active | 2 |

Other tools that score 3 but are prototypes or niche:

- [FontBox](https://github.com/Kaidorespy/fontbox): Windows; one untested, AI-generated commit.
- [YMM4-FontManager](https://github.com/routersys/YMM4-FontManager): a Japanese video-editor plugin, archived 2026-09-19.
- [font-mcp-server](https://github.com/miruna23-08/font-mcp-server): an MCP server. It has a system-font scan and a popularity-sorted Google search, and leaves the comparison to the LLM.

Three Chinese SkyFonts-style clients read system fonts and sort their catalogs by popularity, with "free commercial" and Latin filters: [字由 HelloFont](https://www.hellofont.cn/), [字加](https://www.zijia.com.cn/zijia.html) and [iFonts](https://ifonts.com/client). The detection and the catalog are separate views, and "free commercial" is the vendor's label, not a license type.

## What no existing tool does

These are the project's openings, each checked against the tools above.

1. **Detection of fonts installed any way, feeding a missing-only view.** Tools with a missing-only view track only their own installs. Tools that detect system-wide (fontconfig, Pango, font-kit, `queryLocalFonts`) never hide installed fonts from a ranked catalog. Font Manager knows every installed font *and* has a popularity-sorted catalog, but never compares the two.
2. **Name matching.** Every tool matches exact, prefix or substring names. None handles renames (Source Sans Pro → Source Sans 3), Nerd Font builds (Sauce Code Pro), or false prefix matches (Fontz treats RobotoMono files as Roboto).
3. **A web page.** Only the Local Font Access API can list fonts, on Chromium desktop only. Nobody offers a fallback such as pasting the output of `fc-list`.
4. **An independent, Latin-only ranking.** Every popularity sort is Google's rank or Google's API order. Top-20 lists include Noto Sans JP/KR/SC and Material Icons. Non-Google free fonts are unranked.
5. **A strict license rule.** Catalogs call fonts "free" by where they come from, not by their license text. Fonts Over Time and FontGet count Fontshare's ITF license as free, and Fonts.Free accepts personal-use submissions. None separates "usable for everything" from "redistributable" the way AUTHORITY Rules 1 and 3 do. Fontist's web registry comes closest, with a Redistributable filter.
6. **Official download links.** Most tools install straight from `fonts.gstatic.com`, and Fonts Over Time has no download links at all.

## Building blocks worth reusing

**Catalog and license data** (the first three checked directly on 2026-09-25):

- **Google Fonts metadata**, `https://fonts.google.com/metadata/fonts`: 1,946 families. Has `popularity`, `trending`, `defaultSort`, `subsets`, `primaryScript` and `isOpenSource`. Every family is OFL, Apache-2.0 or UFL.
- **Fontsource API**, `https://api.fontsource.org/v1/fonts`: 2,100 fonts, each with a `license` field. Counts: OFL-1.1 2,056, Apache-2.0 36, UFL-1.0 5, and one each of CC0, MIT and Unlicense, so all qualify. 120 are not from Google Fonts.
- **Fontshare API**, `https://api.fontshare.com/v2/fonts`: 100 fonts. 64 are under the ITF license, now excluded by AUTHORITY Rule 4, and 36 are under the SIL OFL. Has `views` counts.
- **Fontist registry**, `https://www.fontist.org/formulas/formulas-data.json`: 4,283 formulas with license type and category, and a Redistributable facet on its website.
- **Nerd Fonts `fonts.json`**: an SPDX license per patched family. Useful for mapping a Nerd Font build back to its original font.

**Popularity signals beyond Google's rank:**

- **Homebrew cask analytics**, `https://formulae.brew.sh/api/analytics/cask-install/365d.json`: 2,640 `font-*` casks with one-year install counts. Skews toward developers and Nerd Fonts.
- **Fontsource / jsDelivr stats**: npm and CDN download counts, which reflect web-developer use.
- **[Fonts Over Time](https://fontsovertime.com/)**: a weekly crawl of about 10,000 homepages, ranking body and heading fonts by share. Its data is "free to download and reuse". It launched as a Show HN on 2026-09-24.
- **Debian popcon**, `https://popcon.debian.org/main/fonts/by_inst`: 771 packages from about 290k reporting systems. Dominated by fonts that other packages pull in automatically, and it leaves out UFL fonts. Demand for using it exists: [fnt issue #37](https://github.com/alexmyczko/fnt/issues/37), open since 2024, asks for exactly this sort.
- HTTP Archive Web Almanac, fonts chapter.

**Detection:**

- Browser: Local Font Access `queryLocalFonts()` (Chromium desktop, behind a permission prompt).
- Chrome extensions: `chrome.fontSettings.getFontList()`, which returns names only.
- Native: fontconfig or Pango (Linux), font-kit (Rust, cross-platform), CoreText (macOS), DirectWrite or the registry (Windows).

**UX precedents:**

- **[Noonnu](https://noonnu.cc/en/index)** (Korea) sorts by popularity by default and has permitted-use checkboxes: Print, Website, Packaging, Video, Embedding, BI/CI and OFL. It's a good model for Rule 3's redistributable toggle.
- **FontDrop!** and **Wakamai Fondue** process dropped files entirely in the browser, which sets the precedent for "nothing is uploaded".

## Corrections to the first-round findings

The verification pass overturned or sharpened several first-round claims:

- **Snapfont** is gone. It was a Manifest V2 extension, so Chrome has disabled it since July 2025, and it was removed from the Chrome Web Store in 2026.
- **SkyFonts** is discontinued. The claimed 2026 release was a mirror-site date. Its Google Fonts sync ended around early 2021.
- **getnf** has no proprietary fonts. All 72 Nerd Fonts families are under free licenses.
- **FontGet** *does* sort by popularity (on by default, in `browse` and `search`). It only scans two font folders per OS.
- **Fontist**'s `list` marks fonts "installed" only by exact filename in its own directory. Its web registry, however, has License and Redistributable filters.
- **wordmark.it** does have a Google Fonts catalog (Pro), but never compares it with installed fonts.
- **Font Manager** does mark installed state and sort by popularity, but only for its own downloads. It has been dormant since September 2025.
- **Font Downloader** is GTK3, not GTK4. Its catalog is a frozen 2021 snapshot and the project is abandoned.
- **winget** has installed fonts generally since v1.12 (October 2025). Its font catalog holds only two packages, and `winget font list` is still experimental.
- **FontVS**'s filters are source, category, italic, variable and a paid language filter. Its "System" list outside Chromium is hard-coded, not detected.

## Coverage gaps

The second-round critic ran out of search budget before covering these angles, so treat them as open:

- Reddit, dev.to, Medium and social-media "I built" posts. The first-round agent searched Reddit, Hacker News and Product Hunt and found nothing.
- The full Product Hunt archive.
- Defunct pre-2020 tools, such as GoFont for Mac.
- Microsoft 365 cloud fonts, and KDE Discover, Pamac and UniGetUI as package front-ends.
- GitLab, Codeberg and SourceHut code search.
- Arch `pkgstats`.
- Vietnamese, Turkish, Indonesian, Persian, Thai, Polish, Italian and Hindi communities.
- Enterprise font-compliance scanners.

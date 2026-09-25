# AUTHORITY — truly_free_fonts

This file holds the project's settled decisions. Everything else in the repo follows it. Only decisions the owner has made go here. Research and drafts live elsewhere and are linked below.

## Purpose

Compare the fonts a user already has installed with a ranked list of the most popular free Latin fonts, and show the ones they don't have. The preferred delivery is a web page.

## Rules

1. **Licenses.** A font qualifies only if its license allows use in **all personal and commercial projects**. A truly free font has **no use restrictions**. Display-only licenses are excluded, and so are personal-use-only, demo/trial and non-commercial licenses. *(2026-09-25)*
2. **Script.** Latin fonts only.
3. **Redistribution.** Rule 1 is about use, so a license that places no restrictions on use but forbids redistributing the font files still qualifies. Each font records whether it may be redistributed. The web page has an option labelled **"Redistributable fonts only"** (or similar wording) that hides the rest; when it is off, those fonts are listed too. *(2026-09-25)*
4. **Excluded licenses.**
   - **ITF Free Font License v2.0 (17 Aug 2026)**, used by 64 of Fontshare's 100 fonts. It has use restrictions: it forbids modification, including subsetting and format conversion, and it forbids offering the font to third parties through a website, app, SaaS, design tool or template editor. Fontshare fonts under the SIL OFL are unaffected. *(2026-09-25)*

## Infrastructure

*(2026-09-25; setup checklist and runbook in [ops/SERVER.md](ops/SERVER.md))*

- **Domains.** trulyfreefonts.com, .org and .net, registered and hosted on Cloudflare. The canonical URL is `https://trulyfreefonts.com`; `www.*`, `.org` and `.net` 301-redirect to it, keeping the path.
- **Hosting.** A Contabo VPS running Debian 13, served by Caddy, with the site root at `/srv/trulyfreefonts/public`.
- **Cloudflare.** Proxied (orange cloud), SSL mode Full (strict), with a Cloudflare Origin CA certificate on the server.
- **Access.** One admin user `byron`, key-only SSH, passwordless sudo, root login off. Local alias `ssh tff`. Claude manages the server over SSH and Cloudflare through an API token; its ssh/scp/rsync commands to `tff` are auto-allowed in this project.
- **Secrets.** Kept out of the project: the Cloudflare token lives in `~/.config/trulyfreefonts/cloudflare.env`, and the root password (VNC emergency access only) lives in the owner's password manager.

## Repository and workflow

*(2026-09-25)*

- **Repository.** Public, at [github.com/byronshock/trulyfreefonts](https://github.com/byronshock/trulyfreefonts), default branch `main`. The methodology and rankings are open.
- **Kept out of git.**
  - `PLAN.md`: private planning notes.
  - `ops/SERVER.local.md`: origin IPs, VNC console and zone IDs; publishing the origin IP would let anyone bypass Cloudflare.
  - `.claude/settings.local.json`.
- **Tracked docs.** `docs/ranking-methodology.md` and `docs/milestone-1.md` are versioned.
- **Monthly data refresh.** A scheduled GitHub Actions workflow runs the pipeline and opens a pull request with the new catalog and anything flagged for review. The owner reviews and merges it.

## Funding

- A donation button on the site, and nothing more: no donation strategy or fundraising work. By the owner's reckoning the site costs nothing except their time. *(2026-09-25)*

## Current step

1. Survey the tools that already exist for this, or for parts of it. *(done 2026-09-25; findings in [docs/prior-art.md](docs/prior-art.md))*
2. Milestone 1: the ranking methodology proposal and checklist are being drafted. *(2026-09-25)*

## Background

- The earlier top-100 library is at `~/Documents/code/fonts`; its `MANIFEST.md` explains the ranking method. Its 8 Fontshare families (Satoshi, General Sans, Clash Display, Cabinet Grotesk, Switzer, Ranade, Gambetta, Chillax) are under the ITF license and do not qualify.

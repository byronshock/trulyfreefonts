# Roadmap

Status as of 2026-09-25. Settled decisions are in [AUTHORITY.md](../AUTHORITY.md); each checklist has the detail.

## Milestone 1: catalog script and catalog.json
- **Goal:** one script builds a ranked, license-checked catalog of about 500 truly free Latin font families.
- **Status:** Step 0 in review in [pull request #1](https://github.com/byronshock/trulyfreefonts/pull/1). D8 is decided; D1, D3, D4, D7, D10, D12, D13, D14, D15 and D17 are open.
- **Checklist:** [milestone-1.md](milestone-1.md)
- **Depends on:** nothing.

## Milestone 2: the filterable list goes live (intermediate release)
- **Goal:** the ranked, filterable list replaces the stub, with methodology, privacy and about pages and a tip link; usability testing starts. No owned-font comparison.
- **Status:** draft checklist awaiting its Step 0. Done early: the server log policy (M2-D9), Cloudflare's error logging off, and the live tip link ([ops/DONATIONS.md](../ops/DONATIONS.md) steps 1–10).
- **Checklist:** [milestone-2.md](milestone-2.md)
- **Depends on:** Milestone 1. Its step 20 freezes `catalog-site.json` v1 after this milestone's step 2 approves the fields; the soft launch waits for that freeze.

## Milestone 3: owned-font tools
- **Goal:** visitors paste a one-line command's output (Linux, macOS, Windows) or, in desktop Chromium, press "Check my fonts". Matching stays in the browser. Built and tested on a hidden page beside the live list.
- **Status:** draft checklist awaiting its Step 0.
- **Checklist:** [milestone-3.md](milestone-3.md)
- **Depends on:** Milestone 1's alias table and name export; Milestone 2's live site, deploy path, headers and usability process.

## Milestone 4: full release, then monthly refreshes
- **Goal:** switch the comparison on for everyone, announce the site, and run the monthly refresh. Two months after launch, a review decides between new features and maintenance only.
- **Status:** draft checklist awaiting its Step 0.
- **Checklist:** [milestone-4.md](milestone-4.md)
- **Depends on:** Milestone 3 done; the tip link live; Milestone 1's monthly workflow.

# Server: trulyfreefonts

How the Contabo VPS and the three Cloudflare zones are set up. The settled decisions are in [AUTHORITY.md](../AUTHORITY.md#infrastructure); this file is the checklist and runbook.

## Facts

| | |
|---|---|
| Host | Contabo Cloud VPS 4 (2026), Seattle, Debian 13 (Trixie) |
| IPv4 / IPv6 | in `ops/SERVER.local.md` (not in git) |
| SSH | `ssh tff` (user `byron`, key `~/.ssh/id_ed25519`, passwordless sudo) |
| Site root | `/srv/trulyfreefonts/public` |
| Web server config | [ops/Caddyfile](Caddyfile) → `/etc/caddy/Caddyfile` |
| Origin cert | `/etc/caddy/certs/` (Cloudflare Origin CA, 15 years) |
| Cloudflare zone IDs | in `ops/SERVER.local.md`, or `ops/cf.sh GET /zones` |
| Cloudflare token | `~/.config/trulyfreefonts/cloudflare.env` on the laptop (mode 600, never committed) |
| Emergency access | Contabo panel → VNC console (address in `ops/SERVER.local.md`), root password in password manager |
| Snapshots | 1 slot on this plan (2 on the next tier up), each deleted after 30 days. Use one as an undo point before risky changes, not as a backup. To rebuild, use `ops/` + `public/` + this checklist. |

**Deploy the site** (from the project root): `rsync -av --delete public/ tff:/srv/trulyfreefonts/public/`

**Change the web server config:** edit [ops/Caddyfile](Caddyfile), then run the deploy line at the top of that file.

**Cloudflare API:** `ops/cf.sh METHOD /path [json]`, e.g. `ops/cf.sh GET /zones`. It reads the token from the env file and never prints it.

**Cloudflare IP ranges:** `ssh tff sudo cloudflare-ips-sync` refreshes the firewall and Caddy by hand; a weekly timer does it automatically.

## Setup checklist

### A. By hand (Byron)
- [x] 1. Get the IPv4 (and IPv6) from Contabo. Change the emailed root password and store it in the password manager.
- [x] 2. `ssh-copy-id -i ~/.ssh/id_ed25519.pub root@<IPv4>` from your own terminal.
- [x] 3. Create the Cloudflare API token "trulyfreefonts-mgmt" (Zone·Zone·Read, Zone·DNS·Edit, Zone·Zone Settings·Edit, Zone·SSL and Certificates·Edit; the 3 zones). Put `CF_API_TOKEN=<token>` in `~/.config/trulyfreefonts/cloudflare.env`.

### B. Server baseline (Claude, over SSH)
- [x] 4. `Host tff` in `~/.ssh/config`; allow rules for ssh/scp/rsync to `tff` in `.claude/settings.local.json`.
- [x] 5. `apt full-upgrade`; hostname `trulyfreefonts`; timezone UTC; install `sudo ufw fail2ban unattended-upgrades`; automatic security updates on.
- [x] 6. User `byron` with the key and NOPASSWD sudo (`/etc/sudoers.d/byron`).
- [x] 6b. Remove cloud-init's default `debian` user (locked, but has NOPASSWD sudo) and `/etc/sudoers.d/90-cloud-init-users`.
- [x] 7. `/etc/ssh/sshd_config.d/00-hardening.conf`: no root login, no password or keyboard-interactive auth, `AllowUsers byron`.
- [x] 8. `ufw`: deny incoming; allow 22, 80, 443. (80/443 later limited to Cloudflare in step 14.) fail2ban sshd jail (`backend = systemd`, home IP ignored). LLMNR/mDNS off in systemd-resolved.
- [x] 9. Reboot and confirm it comes back.

### C. Cloudflare (Claude, over the API)
- [x] 10. Proxied `A`/`AAAA` records for `@` and `www` in all 3 zones.
- [x] 11. SSL Full (strict), Always Use HTTPS, minimum TLS 1.2 on all 3 zones.
- [x] 12. Origin CA cert for `trulyfreefonts.{com,org,net}` and `*.trulyfreefonts.{com,org,net}`, key generated on the server.

### D. Web server (Claude)
- [x] 13. Caddy from the official repo; `.com` serves the site; `www.*`, `.org` and `.net` 301 to `https://trulyfreefonts.com{uri}`; placeholder page.

### E. Optional
- [x] 14. Ports 80/443 open only to Cloudflare's IP ranges; Caddy trusts `CF-Connecting-IP` from them. Kept current weekly by `cloudflare-ips-sync.timer` ([ops/cloudflare-ips-sync](cloudflare-ips-sync)).
- [x] 15. Cloudflare Email Routing `admin@trulyfreefonts.com` → Gmail; "no mail" SPF/DMARC on .org and .net. (Email Routing records: MX route1–3.mx.cloudflare.net, SPF, DKIM `cf2024-1`.)
- [x] 16. Contabo snapshot (taken 2026-09-25; auto-deleted after 30 days, around 2026-10-25).

## Verification
- `ssh tff sudo -n true` works; `ssh root@<IP>` and `ssh -o PubkeyAuthentication=no tff` are refused.
- `ssh tff 'sudo ufw status verbose; systemctl is-active caddy fail2ban unattended-upgrades'` is all active.
- `dig +short trulyfreefonts.com` returns Cloudflare IPs.
- `curl -sI https://trulyfreefonts.com` → 200, `server: cloudflare`. `www.`, `.org` and `.net` URLs → 301 to the same path on `https://trulyfreefonts.com`.
- SSL mode is `strict` on all 3 zones.

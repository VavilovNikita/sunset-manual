# Deploying the manual on the VPS

Commands are shown with `sudo`; when logged in as root (as on the hotel VPS), leave it out.

The manual is served at `https://sunsetsamui.com/manual/` by the nginx that already runs on the host. Anyone signed in to the admin as staff can open it; anyone else is sent to the staff sign-in page and back.
The check is the web app's `GET /api/session/staff-check` (sunset-beach), so that has to be deployed first.
Nothing else on the server changes.

## One time

```
cd ~
git clone git@github.com:VavilovNikita/sunset-manual.git   # or https, same as the other repos
cd ~/sunset-manual
./deploy/publish.sh                                         # copies site/ to /var/www/sunset-manual
```

Then edit `/etc/nginx/sites-available/sunsetsamui` (keep a dated copy first): put the `proxy_cache_path` line from `deploy/nginx-manual.conf` at the top, outside the server blocks, and the `location` blocks inside the `server { listen 443 ... }` block.

```
sudo nginx -t && sudo systemctl reload nginx
```

Check it works:

- `curl -sI https://sunsetsamui.com/manual/` answers `302` to `/login?callbackUrl=/manual/`.
- In a browser: sign in at `/login` and open `/manual/`, the manual opens. Sign out and reload, you are back on the sign-in page.
- `curl -sI https://sunsetsamui.com/` and `https://sunsetsamui.com/api/actuator/health` are unchanged.

## Every update

```
cd ~/sunset-manual && git pull && ./deploy/publish.sh
```

## From the shared password (October 2026) to the staff login

The first version used nginx basic auth. Replace its two `location` blocks with the ones above, and add the `proxy_cache_path` line. After the reload, `/etc/nginx/sunset-manual.htpasswd` is no longer read and can be deleted.

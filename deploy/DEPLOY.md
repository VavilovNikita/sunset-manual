# Deploying the manual on the VPS

Commands are shown with `sudo`; when logged in as root (as on the hotel VPS), leave it out.

The manual is served at `https://sunsetsamui.com/manual/` by the nginx that already runs on the host, behind one shared staff password.
Nothing else on the server changes.

## One time

```
cd ~
git clone git@github.com:vavilovnikita/sunset-manual.git   # or https, same as the other repos
cd ~/sunset-manual
./deploy/publish.sh                                         # copies site/ to /var/www/sunset-manual
sudo apt install -y rsync apache2-utils                     # if rsync or htpasswd is missing
sudo htpasswd -c /etc/nginx/sunset-manual.htpasswd staff    # type the password at the prompt
```

Next, copy the two `location` blocks from `deploy/nginx-manual.conf` into the `server { listen 443 ... }` block of `/etc/nginx/sites-available/sunsetsamui`, and reload nginx:

```
sudo cp /etc/nginx/sites-available/sunsetsamui /etc/nginx/sites-available/sunsetsamui.bak-$(date +%F)
sudo nano /etc/nginx/sites-available/sunsetsamui
sudo nginx -t && sudo systemctl reload nginx
```

Check it works:

- `curl -sI https://sunsetsamui.com/manual/` should answer `401`.
- `curl -sI -u staff https://sunsetsamui.com/manual/en/` should answer `200` (curl asks for the password).
- `curl -sI https://sunsetsamui.com/` and `https://sunsetsamui.com/api/actuator/health` should be unchanged.

## Every update

```
cd ~/sunset-manual && git pull && ./deploy/publish.sh
```

## Changing the password

Run `sudo htpasswd /etc/nginx/sunset-manual.htpasswd staff` (without `-c`, which would replace the file).
There is no need to reload nginx.

#!/bin/sh
# Copy the manual from this clone to the folder nginx serves. Run on the VPS after `git pull`.
set -eu
here=$(cd "$(dirname "$0")/.." && pwd)
target=/var/www/sunset-manual
sudo mkdir -p "$target"
sudo rsync -a --delete "$here/site/" "$target/"
sudo chown -R root:root "$target"
sudo chmod -R u=rwX,go=rX "$target"
echo "Published $(git -C "$here" rev-parse --short HEAD) to $target"

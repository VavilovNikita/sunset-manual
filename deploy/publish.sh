#!/bin/sh
# Copy the manual from this clone to the folder nginx serves. Run on the VPS after `git pull`.
# Works as root (no sudo needed) or as a user with sudo. Needs rsync (apt install rsync).
set -eu
here=$(cd "$(dirname "$0")/.." && pwd)
target=/var/www/sunset-manual
if [ "$(id -u)" -eq 0 ]; then as_root=""; else as_root="sudo"; fi
$as_root mkdir -p "$target"
$as_root rsync -a --delete "$here/site/" "$target/"
$as_root chown -R root:root "$target"
$as_root chmod -R u=rwX,go=rX "$target"
echo "Published $(git -C "$here" rev-parse --short HEAD) to $target"

#!/bin/sh
set -eu

if [ "${1#-}" != "$1" ]; then
	set -- python3 build.py "$@"
fi

exec "$@"

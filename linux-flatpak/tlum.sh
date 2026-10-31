#!/bin/sh

export KIVY_HOME="${XDG_CONFIG_HOME}/kivy"
export TLUM_DATA_DIR="${XDG_DATA_HOME}"
export KIVY_AUDIO=sdl2

exec python3 /app/share/tlum/main.py "$@"

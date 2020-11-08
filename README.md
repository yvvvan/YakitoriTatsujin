![Mahjong bot](https://github.com/MahjongRepository/tenhou-python-bot/workflows/Mahjong%20bot/badge.svg)

Bot was tested with Python 3.6+ and PyPy3, we are not supporting Python 2.

# What do we have here?

![Example of bot game](https://cloud.githubusercontent.com/assets/475367/25059936/31b33ac2-21c3-11e7-8cb2-de33d7ba96cb.gif)

## Mahjong hands calculation

You can find it here: https://github.com/MahjongRepository/mahjong

## Mahjong bot

For research purposes we built a simple bot to play riichi mahjong on tenhou.net server.

Here you can read about bot played games statistic: [versions history](doc/versions.md)

# For developers

## How to run it?

1. `pip install -r requirements/lint.txt`
1. Run `cd project && python main.py` it will connect to the tenhou.net and will play a game.

## How to run bot battle with pypy

To make it easier run bot vs bot battles we prepared PyPy3 Docker container.

It wasn't tested for regular game on tenhou.net, but theoretically should work here without any issues.

How to run the game locally:

1. [Install Docker](https://docs.docker.com/get-docker/) 
1. Run `make build_docker`
1. Run `make GAMES=1 run_battle` it will play one game locally. Logs and replays will be stored in `bots_battle` folder

## Configuration instructions

1. Put your own settings to the `project/settings/settings_local.py` file. 
They will override settings from default `settings/base.py` file.
1. Also, you can override some default settings with command arguments. 
Use `python main.py -h` to check all available commands.

## Game reproducer

It can be useful to debug bot errors or strange discards: [game reproducer](doc/reproducer.md)

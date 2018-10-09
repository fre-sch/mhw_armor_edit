# MHW Editor Suite

Edit MHW game data.

Note that this requires extracting the game chunk data using
[worldchunktool](https://www.nexusmods.com/monsterhunterworld/mods/6).

## Using the Editor

Download the [latest release](https://github.com/fre-sch/mhw_armor_edit/releases),
extract and run ``MHW-Editor-Suite.exe``.

* Extract ``<GAMEDIR>\chunk\chunk0.bin`` using [worldchunktool](https://www.nexusmods.com/monsterhunterworld/mods/6).
* Run ``MHW-Editor-Suite.exe`` and open extracted chunk directory using File menu

Currently supported file formats:

* `*.am_dat` - modify only
* `*.eq_crt` - modify only
* `*.gmd` - read only
* `*.itm` - modify only
* `*.shl_tbl` - modify only
* `*.wp_dat_g` - modify only

## Setup for Development

The following is only relevant if having this repository checked out for
development.

### Requirements

* Python 3.6
* Tests require extracted game files in ``test/data``

### Setup

1. Create virtual python env
2. Run ``pip install requirements.txt``
3. Activate virtual env
4. Run ``src/mhw_armor_edit/suite.py``

### Build

1. Create virtual python env
2. Run ``pip install requirements.txt``
3. Activate virtual env
4. Run ``pyinstaller suite.spec``
5. Result is application in ``dist/MHW-Editor-Suite``

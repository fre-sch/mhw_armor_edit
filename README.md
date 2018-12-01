# MHW Editor Suite

Edit MHW game data.

Note that this requires extracting the game chunk data using
[worldchunktool](https://www.nexusmods.com/monsterhunterworld/mods/6).

## Using the Editor

Download the [latest release](https://github.com/fre-sch/mhw_armor_edit/releases),
extract and run ``MHW-Editor-Suite.exe``.

* Extract all ``<GAMEDIR>\chunk\chunk*.bin`` using [worldchunktool](https://www.nexusmods.com/monsterhunterworld/mods/6).
* Using Windows File Explorer, merge all extracted chunk directories into one:
  * Create a new directory ``merged``
  * Navigate into chunk directory ``chunk0``, select all and copy.
  * Navigate into ``merged`` directory, and paste. Wait for completion.
  * Navigate to next chunk directory ``chunk1``, select all and copy.
  * Navigate to ``merged`` directory, and paste. In the popup 
    "Confirm Folder Replace" choose "Yes". In the popup "Replace or Skip Files"
    choose "Replace the file in the destination". Make sure to replace all files. Wait for completion.
  * Repeat for all remaining chunk directories in ascending order, eg. 
    ``chunk2``, ``chunk3``, ``chunk4``, ``chunk5``.
* Using windows File Explorer, create a directory ``my-first-mod``.
* Run ``MHW-Editor-Suite.exe`` and open directory ``merged`` using the menu File -> "Open chunk directory ...".
* Open the directory ``my-first-mod`` using the menu File -> "Open mod directory ...".
* Open files from the chunk directory browser, edit them and save them to add or update them to the mod directory
* Open files from the mod directory browser, edit and save them in mod directory.

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

# MHW Armor Editor

Tests require an extracted armor.am_dat, which is not distributed to due possible
licensing issues.

## Using the Editor

Download the [latest release](https://github.com/fre-sch/mhw_armor_edit/releases), extract and run ``MHW-Armor-Editor.exe``.

## Setup for Development

The following is only relevant if having this repository checked out for
development.

### Requirements

* Python 3.6

### Setup

1. Create virtual python env
2. Run ``pip install requirements.txt``
3. Activate virtual env
4. Run ``src/mhw_armor_edit/armor_editor.py``

### Build

1. Create virtual python env
2. Run ``pip install requirements.txt``
3. Activate virtual env
4. Run ``pyinstaller armor_editor.spec``
5. Result is application in ``dist/MHW-Armor-Editor``

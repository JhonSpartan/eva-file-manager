# EVA File Manager

Desktop application for batch processing DXF files.

## Features

- Rename DXF files
- Replace characters in filenames
- Update "nadpis" layer
- Remove Defpoints layer
- Progress bar
- Multithreaded processing (QThread)
- Error logging

## Installation

```bash
git clone ...
cd file_manager

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt
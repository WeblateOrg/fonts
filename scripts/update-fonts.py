#!/usr/bin/env python3

# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: OFL-1.1

import tomllib
from io import BytesIO
from pathlib import Path, PurePath
from urllib.parse import quote
from zipfile import ZipFile

import requests

with open("scripts/fonts.toml", "rb") as handle:
    FONTS = tomllib.load(handle)

for name, font in FONTS.items():
    print(f"Processing {name}...")
    version_underscore = font["version"].replace("/", "_").replace("-vf", "vf")
    url = font["url"].format(
        version_quoted=quote(font["version"], safe=""),
        version_underscore=version_underscore,
        version_shortened=version_underscore.rsplit("_", 1)[0],
        **font,
    )
    destination = Path(font["destination"])
    destination.mkdir(parents=True, exist_ok=True)
    print(f"Download {url}...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    with ZipFile(BytesIO(response.content)) as zipfile:
        for filename in zipfile.namelist():
            for match in font["extract"]:
                if filename.endswith(match):
                    output = destination / PurePath(match).name
                    print(f"Writing out {output}...")
                    output.write_bytes(zipfile.read(filename))

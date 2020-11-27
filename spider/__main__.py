# Vaccine image scraper
# Copyright (C) 2020  Nguyễn Gia Phong
#
# This file is part of Spider Venom.
#
# Spider Venom is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Spider Venom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Spider Venom.  If not, see <https://www.gnu.org/licenses/>.

from sys import argv

from httpx import AsyncClient
from trio import Path, open_nursery, run

from .tuoitre import tuoitre
from .vnexpress import vnexpress


async def main(dest):
    """Download vaccine images."""
    async with AsyncClient() as client, open_nursery() as nursery:
        nursery.start_soon(tuoitre, Path(dest), client, nursery)
        nursery.start_soon(vnexpress, Path(dest), client, nursery)


if __name__ == '__main__':
    run(main, argv[1] if len(argv) > 1 else '.')

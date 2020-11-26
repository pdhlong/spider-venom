# VnExpress vaccine image scraper
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

from functools import partial
from os.path import basename, splitext
from urllib.parse import urldefrag, urlparse

from html5lib import parse
from httpx import ConnectTimeout
from trio import open_file

INDEX = 'https://vnexpress.net/suc-khoe/vaccine'

parse_html5 = partial(parse, namespaceHTMLElements=False)


def articles(links):
    """Return URLs to vaccine articles from the given links."""
    for a in links:
        url, fragment = urldefrag(a.get('href'))
        # Would this miss a few articles?  Yes.  Do I care?  No.
        if url.endswith('.html') and 'vaccine' in url: yield url


async def download(img, dest, client):
    """Save the given image with caption if it's about vaccine."""
    caption, url = img.get('alt'), img.get('data-src')
    if 'vaccine' not in caption.lower(): return
    name, ext = splitext(basename(urlparse(url).path))
    directory = dest / name
    await directory.mkdir(parents=True, exist_ok=True)

    try:
        fi = await client.get(url)
    except ConnectTimeout:
        return
    async with await open_file(directory/f'image{ext}', 'wb') as fo:
        async for chunk in fi.aiter_bytes(): await fo.write(chunk)
    await (directory/'caption').write_text(caption, encoding='utf-8')
    print(caption)


async def scrape_images(url, dest, client, nursery):
    """Download vaccine images from the given VnExpress article."""
    article = await client.get(url)
    for img in parse_html5(article.text).iterfind('.//img'):
        if img.get('itemprop') == 'contentUrl':
            nursery.start_soon(download, img, dest, client)


async def vnexpress(dest, client, nursery):
    """Download vaccine images from VnExpress."""
    index = await client.get(INDEX)
    for url in set(articles(parse_html5(index.text).iterfind('.//a'))):
        nursery.start_soon(scrape_images, url, dest/'vnexpress',
                           client, nursery)

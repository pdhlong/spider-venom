Scraping vaccine images from VnExpress
======================================

Site analysis
-------------

In order to scrape images from VnExpress, we first need to analyze the site.
The news site is kind enough to provide a portal solely for vaccine-related
news::

   https://vnexpress.net/suc-khoe/vaccine

Taking a peak into the page's source, it is easy to notice that articles
are pointed to via a HTML tag of the following format.

.. code-block:: html

   <a href="https://vnexpress.net/{normalized title}.html"
      class="thumb thumb-5x3"
      title="{title}">

Looking into the article's source, we can see the content image tags like so:

.. code-block:: html

   <img itemprop="contentUrl"
        intrinsicsize="{intrinsic size}"
        alt="{caption}"
        class="lazy"
        src="{encoded source}"
        data-src="{image URL}">

Now we have all needed infomation, let's cook up a scraper!

Scraper construction
--------------------

Since the task is I/O intensive and we are using Python, it is natural
to employ an asynchronous input/output framework.  We pick Trio_ for its
ease-of-use, and thus use HTTPX_ as the HTTP client.  The client
and Trio nursery are prepared as follows:

.. code-block:: python

   from httpx import AsyncClient
   from trio import open_nursery

   async with AsyncClient() as client, open_nursery() as nursery:
       ...

The vaccine portal page

.. code-block:: python

   INDEX = 'https://vnexpress.net/suc-khoe/vaccine'

is then fetched as simply as

.. code-block:: python

   index = await client.get(INDEX)

Next, we need to parse the page and use html5lib_ for it.
For convenience purposes, we define a wrapper with ``namespaceHTMLElements``
disabled by default:

.. code-block:: python

   from functools import partial
   from html5lib import parse

   parse_html5 = partial(parse, namespaceHTMLElements=False)

All the ``a`` tags at the appropriate levels can then be found using

.. code-block:: python

   parse_html5(index.text).iterfind('.//a')

Now we need to extract the only URLs to articles about vaccine.
As discussed earlier, these end with ``.html`` and probably contain ``vaccine``:

.. code-block:: python

   from urllib.parse import urldefrag

   def articles(links):
       """Return URLs to vaccine articles from the given links."""
       for a in links:
           url, fragment = urldefrag(a.get('href'))
           if url.endswith('.html') and 'vaccine' in url: yield url

We then use ``nursery`` to fetch each of these articles in a concurrent task

.. code-block:: python

   nursery.start_soon(scrape_images, url, dest, client, nursery)

and look for the content images

.. code-block:: python

   async def scrape_images(url, dest, client, nursery):
       """Download vaccine images from the given VnExpress article."""
       article = await client.get(url)
       for img in parse_html5(article.text).iterfind('.//img'):
           if img.get('itemprop') == 'contentUrl':
               nursery.start_soon(download, img, dest, client)

The ``async`` function ``download`` takes care of the rest of the work,
namely fetching and putting the images and caption in the specified location:

.. code-block:: python

   from os.path import basename, splitext
   from urllib.parse import urlparse
   from trio import open_file

   async def download(img, dest, client):
       """Save the given image with caption if it's about vaccine."""
       caption, url = img.get('alt'), img.get('data-src')
       if 'vaccine' not in caption.lower(): return
       name, ext = splitext(basename(urlparse(url).path))
       directory = dest / name
       await directory.mkdir(parents=True, exist_ok=True)

       async with await open_file(directory/f'image{ext}', 'wb') as fo:
           async for chunk in fi.aiter_bytes(): await fo.write(chunk)
       await (directory/'caption').write_text(caption)

.. _Trio: https://trio.readthedocs.io
.. _HTTPX: https://www.python-httpx.org
.. _html5lib: https://html5lib.readthedocs.io

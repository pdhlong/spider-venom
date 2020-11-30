Scraping vaccine images from tuoitre
====================================

Site analysis
-------------

The site that we are going to work with to get the articles about vaccine from tuoitre.vn is::

   https://tuoitre.vn/vaccine.html

Different form VnExpress, the href provided in ``<a>`` can't directly link to the articles, moreover, some ``<a>`` 
have no href attribute. For example:

.. code-block:: html
		
   <a href="/vac-xin-covid-19-cua-astrazeneca-bi-che-bai-do-gia-mem-20201127105727613.htm" 
      title="V&#7855;c xin COVID-19 c&#7911;a AstraZeneca b&#7883; chê bai do... giá m&#7873;m?" 
      class="img212x132 pos-rlt" data-displayinslide="0">	
	   
   <a id="refresh-captcha">Lấy mã mới</a>

For the images and their captions in the articles, we will try to get the ``src`` ---image source and 
``alt`` ---image caption of the ``<img>`` tag. 

Scraping explanation
--------------------

The site that will be worked with is defined as:

.. code-block:: python

   INDEX = 'https://tuoitre.vn/vaccine.html'
	
Then it is fetched and parsed in order to find all the available ``<a>`` tag.

The scraper then focuses on 3 main functions articles(), scrape_image() and download().

articles()
^^^^^^^^^^

.. code-block:: python
	
   def articles(links):
       """Search for URLs contains 'vacxin' in the given link."""
       for a in links:
           href = a.get('href')
           if href is None: continue
           url = 'http://tuoitre.vn' + href
           if url.endswith('.htm') and 'vac' in url: yield url
		
From the ``<a>`` tags from we try to get the href attribute of each ``<a>``. Since some ``<a>`` have no href attribute, 
we will skip if the href returns None. To make the href become a recognized url, we add ``http://tuoitre.vn`` 
before the href. Finally, in order to get the appropriate articles related to vaccine, we only get the url end 
with ``.htm`` and contains ``vac``.

scrape_image()
^^^^^^^^^^^^^^

.. code-block:: python

   async def scrape_images(url, dest, client, nursery):
       """Search for img in the articles in order to download the images."""
       article = await client.get(url)
       for img in parse_html5(article.text).iterfind('.//img'):
           if img.get('type') == 'photo':
	       nursery.start_soon(download, img, dest, client)
				
The appropriate urls are then fetched and parsed in order to find all the ``<img>`` tags available.
We notice that the main images of the articles all have ``type="photo"`` so we only have get the 
``<img>`` satisfied the condition without having to check the captions' contents.

download()
^^^^^^^^^^

.. code-block:: python

   async def download(img, dest, client):
       """Save the images with theirs captions of the searched articles."""
           caption, url = img.get('alt'), img.get('src')
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
	
Last one is the download() function. It will do all the work remaining. It will download the 
image from ``src`` and the caption from ``alt``. Each image and its caption is then put in the same
folder and named "image", "caption" respectively.

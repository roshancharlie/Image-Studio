import logging
import shutil
import sys
from pathlib import Path

from tqdm import tqdm

from .api import ImageSearchAPI


def image_downloader(query, limit=100, output_dir='dataset', adult_filter_off=True,
                     force_replace=False, timeout=60, filter_string="", verbose=True, badsites=None, name='Image'):
    """
    Download images using the Bing image scraper.

    Parameters:
    query (str): The search query.
    limit (int): The maximum number of images to download.
    output_dir (str): The directory to save the images in.
    adult_filter_off (bool): Whether to turn off the adult filter.
    force_replace (bool): Whether to replace existing files.
    timeout (int): The timeout for the image download.
    filter (str): The filter to apply to the search results.
    verbose (bool): Whether to print detailed output.
    badsites (list): List of bad sites to be excluded.
    name (str): The name of the images.
    """

    if badsites is None:
        badsites = []
    if adult_filter_off:
        adult = 'off'
    else:
        adult = 'on'

    image_dir = Path(output_dir).joinpath(query).absolute()

    if force_replace and Path.is_dir(image_dir):
        shutil.rmtree(image_dir)

    # check directory and create if necessary
    try:
        if not Path.is_dir(image_dir):
            Path.mkdir(image_dir, parents=True)
    except Exception as e:
        logging.error('Failed to create directory. %s', e)
        sys.exit(1)

    logging.info("Downloading Images to %s", str(image_dir.absolute()))

    # Initialize tqdm progress bar

    with tqdm(total=limit, unit='MB', ncols=100, colour="green",
              bar_format='{l_bar}{bar} {total_fmt} MB| Speed {rate_fmt} | Estimated Time:  {remaining}') as pbar:
        def update_progress_bar(download_count):
            pbar.update(download_count - pbar.n)

        bing = ImageSearchAPI(query, limit, image_dir, adult, timeout, filter_string, verbose, badsites, name)
        bing.download_callback = update_progress_bar
        bing.run()



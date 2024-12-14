import imghdr
import logging
import posixpath
import re
import urllib
import urllib.error
import urllib.parse
import urllib.request


class ImageSearchAPI:
    """_summary_
    A class to download images from Bing.

    _description_
    This class is used to download images from Bing. It uses the Bing Image Search API to get the links of the images
    and then downloads the images from the links. The class can be used to download images based on a query, with a
    limit on the number of images to be downloaded. The images can be filtered based on the type of image
    (photo, clipart, line drawing, animated gif, transparent) and the adult content can be filtered as well.
    The images are saved in the specified output directory. The class also has the option to be verbose,
    which will print the progress of the download.

    _parameters_

    query : str
        The query to be used to search for images.
    limit : int
        The number of images to be downloaded.
    output_dir : str
        The directory where the images are to be saved.
    adult : str
        The adult content filter. Can be "off" or "on".
    timeout : int
        The time in seconds to wait for the request to Bing to be completed.
    filter : str
        The type of image to be filtered. Can be "line", "photo", "clipart", "gif", "transparent".
    verbose : bool
        Whether to print the progress of the download.

    _methods_

    get_filter(shorthand)
        Returns the filter string based on the shorthand.
        ============
        shorthand : str
            The shorthand for the filter. Can be "line", "photo", "clipart", "gif", "transparent".
        ============
        return : str
            The filter string based on the shorthand.

    save_image(link, file_path)
        Saves the image from the link to the file path.
        ============
        link : str
            The link of the image to be saved.
        file_path : str
            The file path where the image is to be saved.
        ============
        return : None

    download_image(link)
        Downloads the image from the link.
        ============
        link : str
            The link of the image to be downloaded.
        ============
        return : None
    run()
        Runs the download of the images.
        ============
        return : None

    """

    def __init__(self, query, limit, output_dir, adult, timeout, filter_str='', verbose=True, badsites=None,
                 name='Image'):
        self.sources = None
        if badsites is None:
            badsites = []
        self.download_count = 0
        self.query = query
        self.output_dir = output_dir
        self.adult = adult
        self.filter = filter_str
        self.verbose = verbose
        self.seen = set()
        self.urls = []
        self.badsites = badsites
        self.image_name = name
        self.download_callback = None

        if self.badsites:
            logging.info("Download links will not include: %s", ', '.join(self.badsites))

        assert isinstance(limit, int), "limit must be integer"
        self.limit = limit
        assert isinstance(timeout, int), "timeout must be integer"
        self.timeout = timeout

        self.page_counter = 0
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                                      'AppleWebKit/537.11 (KHTML, like Gecko) '
                                      'Chrome/23.0.1271.64 Safari/537.11',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                        'Accept-Encoding': 'none',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Connection': 'keep-alive'}

    @staticmethod
    def get_filter(shorthand):
        if shorthand == "line" or shorthand == "linedrawing":
            return "+filterui:photo-linedrawing"
        elif shorthand == "photo":
            return "+filterui:photo-photo"
        elif shorthand == "clipart":
            return "+filterui:photo-clipart"
        elif shorthand == "gif" or shorthand == "animatedgif":
            return "+filterui:photo-animatedgif"
        elif shorthand == "transparent":
            return "+filterui:photo-transparent"
        else:
            return ""

    def save_image(self, link, file_path) -> None:
        try:
            request = urllib.request.Request(link, None, self.headers)
            image = urllib.request.urlopen(request, timeout=self.timeout).read()
            if not imghdr.what(None, image):
                logging.error('Invalid image, not saving %s', link)
                raise ValueError('Invalid image, not saving %s' % link)
            with open(str(file_path), 'wb') as f:
                f.write(image)

        except urllib.error.HTTPError as e:
            self.sources -= 1
            logging.error('HTTPError while saving image %s: %s', link, e)

        except urllib.error.URLError as e:
            self.sources -= 1
            logging.error('URLError while saving image %s: %s', link, e)

    def download_image(self, link):
        self.download_count += 1
        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split('?')[0]
            file_type = filename.split(".")[-1]
            if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
                file_type = "jpg"

            if self.verbose:
                print("[%] Downloading Image #{} from {}".format(self.download_count, link))

            self.save_image(link, self.output_dir.joinpath("{}_{}.{}".format(
                self.image_name, str(self.download_count), file_type)))
            if self.verbose:
                print("[%] File Downloaded !\n")

            # Update progress bar
            if self.download_callback:
                self.download_callback(self.download_count)

        except Exception as e:
            self.download_count -= 1
            logging.error('Issue getting: %s\nError: %s', link, e)

    def run(self):
        while self.download_count < self.limit:
            if self.verbose:
                logging.info('\n\n[!]Indexing page: %d\n', self.page_counter + 1)

            # Build the request URL
            request_url = self.build_request_url()

            try:
                # Make the request and get the HTML response
                response = urllib.request.urlopen(urllib.request.Request(request_url, headers=self.headers))
                html = response.read().decode('utf8')

                if not html:
                    logging.info("[!] No more images are available.")
                    break

                # Extract image links
                links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
                if self.verbose:
                    logging.info("[%%] Indexed %d Images on Page %d.", len(links), self.page_counter + 1)
                    logging.info("\n===============================================\n")

                # Process each link
                self.process_links(links)

                self.page_counter += 1

            except urllib.error.URLError as e:
                logging.error('Error making request to Bing: %s', e)

        logging.info("\n\n[%%] Done. Downloaded %d images.", self.download_count)

    def build_request_url(self):
        """Helper function to build the request URL."""
        return (
            f'https://www.bing.com/images/async?q={urllib.parse.quote_plus(self.query)}'
            f'&first={self.page_counter}&count={self.limit}&adlt={self.adult}'
            f'&qft={self.get_filter(self.filter) if self.filter else ""}'
        )

    def process_links(self, links):
        """Process and download images from the links."""
        for link in links:
            if any(badsite in link for badsite in self.badsites):
                if self.verbose:
                    logging.info("[!] Link included in badsites %s", link)
                continue

            if self.download_count < self.limit and link not in self.seen:
                self.seen.add(link)
                self.download_image(link)

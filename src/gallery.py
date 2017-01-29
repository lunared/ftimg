"""
Classes and methods for dealing with managing image galleries
and their files.

New galleries will be cached into mongo, old galleries can
be fetched from mongo instead of having to hit the hard drive
every time.
"""

import base64
import yaml
import os
import math

from PIL import ExifTags, Image
from .app import mongo, app

class Gallery(object):
    """
    Object representation of an image Gallery
    """

    """
    Metadata file we expect in folders for additional information, \
    such as artist information and tags.
    """
    INFO_FILE = 'gallery.yml'

    @staticmethod
    def _format_path(path):
        """
        Properly formats a path for an image gallery in the app
        """
        filepath = "{0}".format(app.config['ROOT_DIRECTORY'])
        if path:
            filepath = "{0}{1}".format(app.config['ROOT_DIRECTORY'], path)
        return filepath

    @staticmethod
    def generate_thumbnail(img):
        from io import BytesIO
        buffered = BytesIO()
        img.thumbnail((400, 400))
        img = img.convert(mode="RGB")
        img.save(buffered, format="JPEG")
        return "data:image/jpg;base64,{}".format(
            base64.b64encode(buffered.getvalue()).decode('utf-8').replace('\n', '')
        )

    @staticmethod
    def _read_exif(file):
        """
        Reads all existing exif tags from the image
        In particular we'll be looking for thumbnail exif images

        @return: dict of the exif tags on the image
        """
        img = Image.open(file)
        try:
            exif = {
                ExifTags.TAGS[k]: v
                for k, v in img._getexif().items()
                if k in ExifTags.TAGS
            }
            if 'thumbnail' not in exif:
                exif['thumbnail'] = Gallery.generate_thumbnail(img)
            return exif
        except Exception:
            return {
                'thumbnail': Gallery.generate_thumbnail(img)
            }

    @staticmethod
    def _read_info(directory):
        """
        add metadata reading from gallery.yml, which includes additional base information
        not typically found in exif data

        @param directory: File path of the image gallery
        @return dict: metadata from the gallery.yml.  If no gallery.yml exists we default to
                    returning a dict with the title of the gallery being the filepath
        """
        def read_from_file(directory):
            try:
                meta = yaml.load(open(os.path.join(directory, Gallery.INFO_FILE), 'r'))['gallery']
                return meta
            except Exception as e:
                return {
                    'title': os.path.basename(directory.rstrip(os.path.sep)),
                }

        if app.config['USE_MONGO']:
            try:
                return mongo.db.galleries.find({'path': directory})
            except Exception:
                return read_from_file(directory)
        else:
            return read_from_file(directory)


    def __init__(self, path):
        self.path = os.path.join(app.config['ROOT_DIRECTORY'], path)
        self.meta = Gallery._read_info(self.path)

    @property
    def files(self):
        if app.config['USE_MONGO']:
            return mongo.db.galleries.find({'path': self.path}, {'files.thumbnail': 1, 'files.path': 1})
        else:
            files = [f for f in os.listdir(self.path) if app.config['FORMAT_MATCH'].search(f)]
            files.sort()
            return files

    def render(self, url, page=1, page_size=10):
        """
        Get a context renderable version of this Gallery.
        Supports paginating the image gallery

        @return: a dictionary used for view context related to the pagination of the gallery
        """
        
        images = [
            {
                'path': url + "{}{}".format(self.path, f)[len(app.config['ROOT_DIRECTORY']):],
                'thumbnail': Gallery._read_exif(os.path.join(self.path, f))['thumbnail']
            }
            for f in self.files
        ]
        pages = math.ceil(len(images) / page_size)

        return {
            'total': len(images),
            'images': images[(page-1)*page_size:page*page_size],
            'meta': self.meta
        }, pages


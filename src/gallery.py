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
import pymongo

from PIL import ExifTags, Image
from .app import app, mongo

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
    def generate_thumbnail(file):
        """
        Uses PIL to generate a thumbnail for an image file

        @param file: image file of a page in the gallery
        """
        from io import BytesIO
        img = Image.open(file)
        buffered = BytesIO()
        img.thumbnail((400, 400))
        img = img.convert(mode="RGB")
        img.save(buffered, format="JPEG")
        return "data:image/jpg;base64,{}".format(
            base64.b64encode(buffered.getvalue()).decode('utf-8').replace('\n', '')
        )

    @staticmethod
    def _read_info(directory):
        """
        add metadata reading from gallery.yml, which includes additional base information
        not typically found in exif data

        @param directory: File path of the image gallery
        @return dict: metadata from the gallery.yml.  If no gallery.yml exists we default to
                    returning a dict with the title of the gallery being the filepath
        """

    def __init__(self, path):
        self.path = path

    @property
    def filepath(self):
        return os.path.join(app.config['ROOT_DIRECTORY'], self.path)

    @property
    def meta(self):
        if app.config['USE_MONGO']:
            return mongo.db.galleries.find_one({'_id': self.path})
        else:
            try:
                meta = {}
                with open(os.path.join(self.filepath, Gallery.INFO_FILE), 'r') as gyml:
                    meta = yaml.load(gyml)['gallery']
                return meta
            except Exception as e:
                return {
                    'title': os.path.basename(self.filepath),
                }

    @property
    def files(self):
        """
        Discovers all files for the Gallery
        """
        if app.config['USE_MONGO']:
            files = mongo.db.pages.find(
                {'gallery': self.path},
                {'thumbnail': 1, '_id': 1}
            ).sort([('_id', pymongo.ASCENDING)])
            return files, files.count()
        else:
            files = [f for f in os.listdir(self.filepath) if app.config['FORMAT_MATCH'].search(f)]
            files.sort()
            return [
                {
                    '_id': "{}{}".format(self.path, f)[len(app.config['ROOT_DIRECTORY']):],
                    'thumbnail': Gallery.generate_thumbnail(os.path.join(self.filepath, f))
                }
                for f in files
            ], len(files)

    def render(self, page=1, page_size=10):
        """
        Get a context renderable version of this Gallery.
        Supports paginating the image gallery

        @return: a dictionary used for view context related to the pagination of the gallery
        """

        images, count = self.files
        pages = math.ceil(count / page_size)

        if app.config['USE_MONGO']:
            images = images.skip(0 if page <= 1 else ((page-1)*page_size)).limit(page_size)
        else:
            images = images[(page-1)*page_size:page*page_size]

        return {
            'total': count,
            'images': list(images),
            'meta': self.meta
        }, pages


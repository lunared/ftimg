#! /bin/python3.5

from flask import Flask, render_template, request, send_from_directory, abort, send_file
import decimal
import glob
import os
import re
import io
import base64
import fnmatch
import yaml
import math
from urllib.parse import urlencode

# for thumbnail importing
from PIL import ExifTags, Image

# for dir updating
from watchdog.observers import Observer as FileObserver
from watchdog.events import FileSystemEventHandler
import time

app = Flask(__name__,)

"""
Root directory that we scan for image galleries from.\n
Do not change this unless you're not using the docker-compose.  \
It is preferred you use just change the volume mapping on the docker-compose.yml
"""
ROOT_DIRECTORY = "./gallery/"

"""
Tells flask to serve the image files.\n
Typically you'd want nginx to do this instead, as this is an \
easy way to cause concurrent response issues with flask
"""
SERVE_FILES = True

"""
acceptable standard html5 compatible formats
"""
FORMATS = ['*.jpg', '*.png', '*.jpeg']
FORMAT_MATCH = re.compile(r'.(jpg|jpeg|png)$')

"""
Metadata file we expect in folders for additional information, \
such as artist information and tags.
"""
INFO_FILE = 'gallery.yml'

def get_dir_tree():
    """
    Crawls the root directory recursively for any image galleries

    @return: a list of all the image gallery directory paths
    """
    tree = set()
    for filename in glob.iglob(os.path.join(ROOT_DIRECTORY, '**', '*.jpg')):
        tree.add(os.path.dirname(filename)[len(ROOT_DIRECTORY):]+"/")
    return tree
"""
Directory tree of all valid image galleries stemming from the ROOT_DIRECTORY.

When starting up the app, we make sure we cache the directory tree of all folders \
that may be traversed by ftmp3.  
This allows us to have a nice navigation menu of the file system.
"""
DIR_TREE = get_dir_tree()


def read_info(directory):
    """
    add metadata reading from gallery.yml, which includes additional base information
    not typically found in exif data

    @param directory: File path of the image gallery
    @return dict: metadata from the gallery.yml.  If no gallery.yml exists we default to
                  returning a dict with the title of the gallery being the filepath
    """
    try:
        return yaml.load(open(os.path.join(directory, INFO_FILE), 'r'))['gallery']
    except Exception as e:
        return {
            'title': directory
        }

def generate_thumbnail(img):
    from io import BytesIO
    buffered = BytesIO()
    img.thumbnail((400, 400))
    img = img.convert(mode="RGB")
    img.save(buffered, format="JPEG")
    return "data:image/jpg;base64,{}".format(
        base64.b64encode(buffered.getvalue()).decode('utf-8').replace('\n', '')
    )

def read_exif(file):
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
            exif['thumbnail'] = generate_thumbnail(img)
        return exif
    except Exception:
        return {
            'thumbnail': generate_thumbnail(img)
        }

def format_path(path):
    """
    Properly formats a path for an image gallery in the app
    """
    filepath = "{0}".format(ROOT_DIRECTORY)
    if path:
        filepath = "{0}{1}".format(ROOT_DIRECTORY, path)
    return filepath

def get_images(path):
    """
    @param path: filepath of the image gallery
    @return: the list of image file paths for a gallery
    """
    files = [f for f in os.listdir(path) if FORMAT_MATCH.search(f)]
    files.sort()

    images = [
        {
            'path': request.url_root + "{0}{1}".format(path, f)[len(ROOT_DIRECTORY):],
            'thumbnail': read_exif(os.path.join(path, f))['thumbnail']
        }
        for f in files
    ]
    import json

    return images

def paginate(images, page=1, page_size=10):
    """
    Paginates the image gallery

    @return: a dictionary used for view context related to the pagination of the gallery
    """
    pages = math.ceil(len(images) / page_size)
    return {
        'total': len(images),
        'pages': pages,
        'page': page,
        'pagesize': page_size,
        'nextpage': min(page + 1, pages),
        'prevpage': max(page - 1, 1),
        'images': images[(page-1)*page_size:page*page_size]
    }

@app.route('/')
@app.route('/<path:path>')
def home(path=None):
    if path and not os.path.exists(os.path.join(ROOT_DIRECTORY, path)):
        return abort(404)
    if SERVE_FILES and path and FORMAT_MATCH.search(path):
        return send_from_directory(ROOT_DIRECTORY, path)
    path = format_path(path)
    return render_template("body.html", **{
        'path': request.base_url,
        'meta': read_info(path),
        'view': paginate(get_images(path),
                         int(request.args.get('page', 1)),
                         int(request.args.get('pagesize', 10))),
        'tree': DIR_TREE,
    }), 200


class RefreshDirTree(FileSystemEventHandler):
    """
    File System watcher that will refresh the cached
    DIR_TREE whenever there is a change in the filesystem path
    """

    def on_any_event(self, event):
        global DIR_TREE
        DIR_TREE = get_dir_tree()

if __name__ == '__main__':
    app.jinja_env.globals.update(min=min)
    app.jinja_env.globals.update(max=max)
    app.jinja_env.globals.update(is_array=lambda x: isinstance(x, list))
    app.jinja_env.globals.update(is_dict=lambda x: isinstance(x, dict))
    app.jinja_env.globals.update(urlencode=urlencode)
    app.run(debug=True, host='0.0.0.0', port=5000)

    # watch for changes in the file system to update paths
    file_dir_observer = FileObserver()
    file_dir_observer.schedule(RefreshDirTree(), ROOT_DIRECTORY, recursive=True)
    file_dir_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        file_dir_observer.stop()
    file_dir_observer.join()
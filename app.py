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

app = Flask(__name__,)

# Root directory that we scan for music from
# Do not change this unless you're not using the docker-compose
# It is preferred you use just change the volume mapping on the docker-compose.yml
ROOT_DIRECTORY = "./gallery/"
# Tells flask to serve the image files
# Typically you'd want nginx to do this instead, as this is an
# easy way to cause concurrent response issues with flask
SERVE_FILES = True
# acceptable standard html5 compatible formats
FORMAT_MATCH = re.compile(r"\.(jpg|jpeg|png)$")

# Metadata file we expect in folders for additional information
# such as artist information and tags.  If not provided
# the title of the gallery is assumed to be the folder name
INFO_FILE = 'gallery.yml'

# when starting up the app, we make sure we cache the directory tree of all folders
# that may be traversed by ftmp3.  This allows us to have a nice navigation menu
# of the file system.
def get_dir_tree():
    tree = []
    for path, dirs, files in os.walk(ROOT_DIRECTORY):
        if len(fnmatch.filter(files, INFO_FILE)) > 0:
            if not path.endswith('/'):
                path += '/'
            tree.append(path[len(ROOT_DIRECTORY):])
    return tree
DIR_TREE = get_dir_tree()

# add cover image reading
def read_info(directory):
    try:
        return yaml.load(open(os.path.join(directory, INFO_FILE), 'r'))['gallery']
    except Exception as e:
        return {
            'title': directory
        }
    
def get_images(path, page=1, page_size=10):
    filepath = "{0}".format(ROOT_DIRECTORY)
    if path:
        filepath = "{0}{1}".format(ROOT_DIRECTORY, path)
    meta = read_info(filepath)
    files = [f for f in os.listdir(filepath) if FORMAT_MATCH.search(f)]
    images = [request.url_root + "{0}{1}".format(filepath, f)[len(ROOT_DIRECTORY):] for f in files]
    images.sort()

    pages = math.ceil(len(images) / page_size)
    return {
        'path': request.base_url,
        'meta': meta,
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
    context = get_images(path, int(request.args.get('page', 1)), int(request.args.get('pagesize', 10)))
    return render_template("body.html", **{
        **context,
        'tree': DIR_TREE,
    }), 200


if __name__ == '__main__':
    print(DIR_TREE)
    app.jinja_env.globals.update(min=min)
    app.jinja_env.globals.update(max=max)
    app.jinja_env.globals.update(is_array=lambda x: isinstance(x, list))
    app.jinja_env.globals.update(is_dict=lambda x: isinstance(x, dict))
    app.jinja_env.globals.update(urlencode=urlencode)
    app.run(debug=True, host='0.0.0.0', port=5000)

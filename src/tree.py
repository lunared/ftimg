import glob
import os
import math

from .app import app, mongo


DIR_TREE = None

def get_dir_tree(page, page_size):
    """
    Crawls the root directory recursively for any image galleries

    @return: a list of all the image gallery directory paths
    """
    global DIR_TREE

    if app.config['USE_MONGO']:
        collection = mongo.db.galleries.find(None, {'path':1, 'title':1})
        return collection.skip(page_size * (page-1)).limit(page_size), math.ceil(collection / page_size)
    else:
        if not DIR_TREE:
            tree = set()
            for filename in glob.iglob(os.path.join(app.config['ROOT_DIRECTORY'], '**', '*.jpg')):
                tree.add(os.path.dirname(filename)[len(app.config['ROOT_DIRECTORY']):]+"/")
            DIR_TREE = [
                {
                    'path': f,
                    'title': f
                }
                for f in tree
            ]
        start = page_size * (page-1)
        end = start + page_size
        return DIR_TREE[start:end], math.ceil(len(DIR_TREE) / page_size)

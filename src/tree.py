import glob
import os

from .app import app, mongo


DIR_TREE = None

def get_dir_tree(page, page_size, search):
    """
    Crawls the root directory recursively for any image galleries

    @return: a list of all the image galleries and the number of how many there are
    """
    global DIR_TREE

    if app.config['USE_MONGO']:
        search = {'$text': {'$search': search}} if search else {}

        collection = mongo.db.galleries.find(
            search,
            {'path':1, 'title':1}
        )

        return collection.skip(page_size * (page-1)).limit(page_size), collection.count()
    else:
        if not DIR_TREE:
            files = list(glob.iglob(os.path.join(settings.ROOT_DIRECTORY, '**', '*.jpg')))
            files.extend(list(glob.iglob(os.path.join(settings.ROOT_DIRECTORY, '**', '*.png'))))
            tree = set()
            for filename in files:
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
        return DIR_TREE[start:end], len(DIR_TREE)

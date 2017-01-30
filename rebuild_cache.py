"""
Script for generating/updating the directory listing
of the mongo database.

Depending on the size of your gallery listing, this might
take a few minutes to set up the first time.
"""

import os
import glob
import datetime
import yaml

from pymongo import MongoClient
from src.gallery import Gallery
from src import settings


def build_cache(database, now):
    """
    Rebuilds the mongo cache of ftimg
    """

    tree = dict()

    # look for all our valid gallery files
    files = list(glob.iglob(os.path.join(settings.ROOT_DIRECTORY, '**', '*.jpg')))
    files.extend(list(glob.iglob(os.path.join(settings.ROOT_DIRECTORY, '**', '*.png'))))
    files.extend(list(glob.iglob(os.path.join(settings.ROOT_DIRECTORY, '**', 'gallery.yml'))))

    for filename in files:
        mod_date = os.path.getmtime(filename)
        path = filename[len(settings.ROOT_DIRECTORY):]
        gallery = os.path.dirname(filename)[len(settings.ROOT_DIRECTORY):]

        # establish or update gallery metadata
        if filename.endswith('gallery.yml'):
            result = database.galleries.find_one_and_update({
                '_id': gallery
            }, {
                '$set': {'lastChecked': now}
            })
            if result is None or \
               (result and result.get('modified', None) is None) or \
               (result and result['modified'] < mod_date):

                with open(filename, 'r') as gyml:
                    meta = yaml.load(gyml)['gallery']
                    database.galleries.update_one(
                        {
                            '_id': gallery,
                        },
                        {
                            '$setOnInsert': {
                                '_id': gallery,
                                'files': [],
                                'lastChecked': now,
                            },
                            '$set': {
                                'modified': mod_date,
                                **meta
                            }
                        },
                        upsert=True
                    )
        # update or add pages into our database
        else:
            result = database.pages.find_one_and_update({
                '_id': path
            }, {
                '$set': {'lastChecked': now}
            })
            if result is None or \
               (result and result.get('modified', None) is None) or \
               (result and result['modified'] < mod_date):
                result = database.pages.update_one(
                    {
                        '_id': path
                    },
                    {
                        '$setOnInsert': {
                            '_id': path,
                            'gallery': gallery,
                            'lastChecked': now,
                        },
                        '$set': {
                            'modified': mod_date,
                            'thumbnail': Gallery.generate_thumbnail(filename)
                        },
                    },
                    upsert=True
                )

                # update the gallery this page belongs to to be aware of the file
                if result.upserted_id:
                    database.galleries.update_one(
                        {
                            '_id': gallery,
                        },
                        {
                            '$setOnInsert': {
                                'modified': None,
                                'title': os.path.basename(os.path.dirname(filename))
                            }
                        },
                        upsert=True
                    )


def clean_cache(database, now):
    """
    Remove files from gallery cache if they no longer exist.
    This is determined by if the file was checked when rebuilding the cache

    @param now: time at which the cache was updated.
    """
    database.pages.delete_many({
        'lastChecked': {'$lt': now}
    })


def run():
    """
    Execute the process of rebuilding and cleaning the mongo cache
    """
    # current time of checking
    now = datetime.datetime.now()

    client = MongoClient(settings.MONGO_HOST)
    database = client.ftimg

    build_cache(database, now)
    clean_cache(database, now)

if __name__ == '__main__':
    run()
    
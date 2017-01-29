"""
FileSystem watchers provided by watchdog.

Hook into mongodb datastore to cache galleries so that \
they may be searchable.
"""

import glob
import os

from watchdog.events import FileSystemEventHandler

from .app import mongo, app


class RefreshDirTree(FileSystemEventHandler):
    """
    File System watcher that will refresh the cached
    DIR_TREE whenever there is a change in the filesystem path
    """

    def __init__(self):
        super().__init__()

    def on_any_event(self, event):
        pass

#! /bin/python3.5

from src.app import app
from src.watcher import RefreshDirTree
from src import views

# for dir updating
from watchdog.observers import Observer as FileObserver
import time

from urllib.parse import urlencode

if __name__ == '__main__':
    app.jinja_env.globals.update(min=min)
    app.jinja_env.globals.update(max=max)
    app.jinja_env.globals.update(is_array=lambda x: isinstance(x, list))
    app.jinja_env.globals.update(is_dict=lambda x: isinstance(x, dict))
    app.jinja_env.globals.update(urlencode=urlencode)

    # watch for changes in the file system to update paths
    file_dir_observer = FileObserver()
    file_dir_observer.schedule(RefreshDirTree(), app.config['ROOT_DIRECTORY'], recursive=True)
    file_dir_observer.start()

    app.run(debug=True, host='0.0.0.0', port=5000)
    file_dir_observer.stop()
    file_dir_observer.join()

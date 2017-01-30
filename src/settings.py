"""
Application settings for ftimg
"""

import re
import os

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

### Region :: MongoDB settings ###
USE_MONGO = os.environ.get('USE_MONGO', False)
MONGO_HOST = os.environ.get('MONGO_URL', "localhost")
MONGO_PORT = 27017
MONGO_DBNAME = "ftimg"

"""
Main app references
"""

from flask import Flask, render_template, request, send_from_directory, abort, send_file
from flask_pymongo import PyMongo
from . import settings

app = Flask('ftimg',)
app.config.update(
    **vars(settings)
)
if settings.USE_MONGO:
    mongo = PyMongo(app, config_prefix='MONGO')
else:
    mongo = None

@app.before_first_request
def setup():
    from urllib.parse import urlencode
    import logging

    app.jinja_env.globals.update(min=min)
    app.jinja_env.globals.update(max=max)
    app.jinja_env.globals.update(is_array=lambda x: isinstance(x, list))
    app.jinja_env.globals.update(is_dict=lambda x: isinstance(x, dict))
    app.jinja_env.globals.update(urlencode=urlencode)

    if settings.USE_MONGO:
        # check connection
        mongo.cx.server_info()
        mongo.db.galleries.create_index([
            ('title', "text"),
            ('title.native', "text"),
            ('title.localized', "text"),
            ('tags', "text")
        ])

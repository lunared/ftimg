"""
Main app references
"""

from flask import Flask, render_template, request, send_from_directory, abort, send_file
from . import settings

app = Flask('ftimg',)
app.config = {
    **app.config,
    **vars(settings)
}

if settings.USE_MONGO:
    mongo = PyMongo(app, config_prefix='MONGO')
else:
    mongo = None
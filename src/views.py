"""
Flask Views
"""

from flask import Flask, render_template, request, send_from_directory, abort, send_file
import os
import math

from .app import app, mongo
from .gallery import Gallery
from .tree import get_dir_tree

@app.route('/<path:path>')
def gallery(path=None):
    """
    View for an image gallery
    """
    if path and not os.path.exists(os.path.join(app.config['ROOT_DIRECTORY'], path)):
        return abort(404)
    if app.config['SERVE_FILES'] and path and app.config['FORMAT_MATCH'].search(path):
        return send_from_directory(app.config['ROOT_DIRECTORY'], path)
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pagesize', 10))
    gallery, pages = Gallery(path).render(page, page_size)
    return render_template("body.html", **{
        'directory': path,
        'url': request.url_root,
        'path': request.base_url,
        'gallery': gallery,
        'page': page,
        'pagesize': page_size,
        'pages': pages,
        'nextpage': min(page+1, pages),
        'prevpage': max(page-1, 1)
    }), 200

@app.route('/')
def search():
    """
    View for the landing search screen
    """
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pagesize', 10))

    dir_tree, total_galleries = get_dir_tree(page, page_size, search)
    return render_template("search.html", **{
        'can_search': app.config['USE_MONGO'],
        'galleries': dir_tree,
        'search': search,
        'page': page,
        'page_size': page_size,
        'pages': math.ceil(total_galleries / page_size),
    })

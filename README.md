# ftimg

This project is inspired by/a fork of ftmp3, designed to provides an html5 super basic interface for looking at your image galleries
hosted on your webserver, whether they be comics, manga, or questionable images.

Designed to play along with html5 ftp clients, such as [Cute File Browser](https://github.com/martinaglv/cute-files).

## How to use
### Docker
Build and run the container
```
docker-compose build && docker-compose up -d
```

Be sure to configure the volume on the docker-compose file to be equal to the files that are exposed by your FTP.
By default the docker-container will render the site on port 80.  You'll probably want to change that, unless you're running this on a subdomain.

### Flask
Alternatively, since this is a really simple app, you can just run it directly on your host machine.
```
pip install -r requirements.txt
``` 
```
python app.py
```

You'll have to edit the app.py in this case to change the ftp directory.  It's also mapped to the default port 5000.

I recommended setting up Cute File Browser and ftimg with nginx in a smart way so you can hop between them quickly.  
eg. `http://0.0.0.0/share/my-image-folder` to `http://0.0.0.0/gallery/my-image-folder`

### Gallery Metadata

ftimg displays metadata from `gallery.yml` files found within the gallery folders.  These are lightweight files that
are non-standard at the moment, but shouldn't take much time to integrate into your collection if you want a information
rich display on the front-end.

## Links

* http://flask.pocoo.org/

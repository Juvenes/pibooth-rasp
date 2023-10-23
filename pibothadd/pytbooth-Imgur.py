
import os
from imgurpython import ImgurClient
import pibooth

__version__ = "0.0.2"

IMGUR_CLIENT_ID = os.environ.get('IMGUR_CLIENT_ID')
IMGUR_CLIENT_SECRET = os.environ.get('IMGUR_CLIENT_SECRET')

if not IMGUR_CLIENT_ID or not IMGUR_CLIENT_SECRET:
    raise ValueError("Imgur credentials not set in environment variables.")

@pibooth.hookimpl
def pibooth_startup(app):
    app.imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)

@pibooth.hookimpl
def state_print_enter(app):
    name = os.path.basename(app.previous_picture_file)

    with open(app.previous_picture_file, 'rb') as fp:
        uploaded_image = app.imgur_client.upload_from_file(fp, config=None, anon=True)
        app.previous_picture_url = uploaded_image['link']

@pibooth.hookimpl
def pibooth_cleanup(app):
    pass

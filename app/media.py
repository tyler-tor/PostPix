"""Public URLs for images (P37).

Every image the app shows lives in ONE S3 bucket and is served through
CloudFront under MEDIA_BASE_URL (e.g. https://postpix.tylertorrero.dev/media):

  uploads/<random>.webp      photos people upload (app/s3_helpers.py)
  seed/avatars/user-01.jpg   demo data images, listed in seeds/media_manifest.json
  seed/posts/post-01.jpg     (uploaded once by the infra repo, never by the app)

URL = MEDIA_BASE_URL + "/" + key.

Without MEDIA_BASE_URL (local development) seed images fall back to the
original hot-linked URLs in the manifest ("source"), so the demo data still
shows pictures with no AWS set up at all.
"""
import json
import os
from functools import lru_cache

from flask import current_app, has_app_context

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), 'seeds', 'media_manifest.json')


@lru_cache(maxsize=1)
def load_manifest():
    with open(MANIFEST_PATH, encoding='utf-8') as f:
        return json.load(f)


def media_base_url():
    """MEDIA_BASE_URL without a trailing slash, or '' when it is not set."""
    if has_app_context():
        base = current_app.config.get('MEDIA_BASE_URL') or ''
    else:
        base = os.environ.get('MEDIA_BASE_URL', '')
    return base.strip().rstrip('/')


def media_url(key):
    """Public URL of an object in the media bucket, or None without MEDIA_BASE_URL."""
    base = media_base_url()
    return f'{base}/{key.lstrip("/")}' if base else None


def _manifest_url(entry):
    return media_url(entry['key']) or entry['source']


def seed_avatar_url(number):
    """Profile picture of seed user #number (see seeds/users.py)."""
    return _manifest_url(load_manifest()['avatars'][str(number)])


def seed_post_url(number):
    """Image of seed post number `number` (see seeds/posts.py)."""
    return _manifest_url(load_manifest()['posts'][str(number)])


def default_avatar_url():
    """Profile picture for new users who did not upload one."""
    return _manifest_url(load_manifest()['default_avatar'])

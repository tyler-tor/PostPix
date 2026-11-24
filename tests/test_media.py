"""P37: uploads through the default AWS credential chain, MEDIA_BASE_URL, seed manifest."""
import io

import boto3
import pytest
from moto import mock_aws
from PIL import Image
from sqlalchemy import select

from app.media import load_manifest
from app.models import db, Post, User
from app.seeds import _seed

BASE = 'https://postpix.example.dev/media'


def _png():
    buffer = io.BytesIO()
    Image.new('RGB', (1600, 1200), (15, 118, 110)).save(buffer, 'PNG')
    buffer.seek(0)
    return buffer


def _login(client):
    user = User(username='tester', email='t@example.com', password='password',
                first_name='T', last_name='E')
    db.session.add(user)
    db.session.commit()
    assert client.post('/api/auth/login', json={'email': 't@example.com', 'password': 'password'}).status_code == 200
    return user


@pytest.fixture
def aws(monkeypatch):
    # Fake credentials so nothing can ever reach a real AWS account.
    for name, value in {'AWS_ACCESS_KEY_ID': 'testing', 'AWS_SECRET_ACCESS_KEY': 'testing',
                        'AWS_SESSION_TOKEN': 'testing'}.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv('AWS_PROFILE', raising=False)
    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-2')
        s3.create_bucket(Bucket='postpix-media-test',
                         CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
        yield s3


def test_upload_goes_to_uploads_prefix_and_uses_media_base_url(app, client, aws):
    app.config.update(S3_BUCKET='postpix-media-test', AWS_REGION='us-east-2', MEDIA_BASE_URL=BASE)
    _login(client)
    response = client.post('/api/img/upload', data={'image': (_png(), 'photo.png')},
                           content_type='multipart/form-data')
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body['url'].startswith(f'{BASE}/uploads/') and body['url'].endswith('.webp')
    assert body['thumbUrl'].endswith('_thumb.webp')
    key = body['url'][len(BASE) + 1:]
    head = aws.head_object(Bucket='postpix-media-test', Key=key)
    assert head['ContentType'] == 'image/webp'
    assert 'immutable' in head['CacheControl']
    # No ACL was set: only the bucket owner has a grant.
    grants = aws.get_object_acl(Bucket='postpix-media-test', Key=key)['Grants']
    assert [g['Permission'] for g in grants] == ['FULL_CONTROL']


def test_without_media_base_url_falls_back_to_regional_s3_url(app, client, aws):
    app.config.update(S3_BUCKET='postpix-media-test', AWS_REGION='us-east-2', MEDIA_BASE_URL='')
    _login(client)
    body = client.post('/api/img/upload', data={'image': (_png(), 'p.png'), 'kind': 'avatar'},
                       content_type='multipart/form-data').get_json()
    assert body['url'].startswith('https://postpix-media-test.s3.us-east-2.amazonaws.com/uploads/')
    assert body['thumbUrl'] is None


def test_upload_without_bucket_fails_cleanly(app, client):
    app.config.update(S3_BUCKET=None)
    _login(client)
    response = client.post('/api/img/upload', data={'image': (_png(), 'p.png')},
                           content_type='multipart/form-data')
    assert response.status_code == 502
    assert 'not configured' in response.get_json()['errors'][0]


def test_manifest_covers_every_seed_image_under_seed_prefix():
    manifest = load_manifest()
    assert sorted(map(int, manifest['avatars'])) == list(range(1, 16))
    assert sorted(map(int, manifest['posts'])) == list(range(1, 51))
    entries = [manifest['default_avatar'], *manifest['avatars'].values(), *manifest['posts'].values()]
    keys = [e['key'] for e in entries]
    assert all(k.startswith('seed/') for k in keys)
    assert len(set(keys)) == len(keys)
    assert all(e['source'].startswith('https://') for e in entries)


def test_seed_uses_media_base_url_when_set(app):
    app.config['MEDIA_BASE_URL'] = BASE
    _seed()
    demo = db.session.scalar(select(User).where(User.email == 'demo@aa.io'))
    assert demo.profile_picture == f'{BASE}/seed/avatars/user-01.jpg'
    urls = db.session.scalars(select(Post.img_url)).all()
    assert len(urls) == 50 and all(u.startswith(f'{BASE}/seed/posts/') for u in urls)


def test_seed_keeps_original_urls_locally(app):
    app.config['MEDIA_BASE_URL'] = ''
    _seed()
    demo = db.session.scalar(select(User).where(User.email == 'demo@aa.io'))
    assert demo.profile_picture == load_manifest()['avatars']['1']['source']


def test_new_user_gets_default_avatar_from_media_bucket(app):
    app.config['MEDIA_BASE_URL'] = BASE
    user = User(username='new', email='n@example.com', password='x', first_name='N', last_name='U')
    db.session.add(user)
    db.session.commit()
    assert user.profile_picture == f'{BASE}/seed/avatars/default.jpg'

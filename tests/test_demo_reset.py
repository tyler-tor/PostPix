"""P41 / Q1: `flask demo reset` restores only the demo user's data, idempotently."""
import io

import boto3
import pytest
from moto import mock_aws
from PIL import Image
from sqlalchemy import delete, func, insert, select

from app import create_app
from app.models import Comment, Post, PostLike, User, db
from app.models.user import DEMO_EMAIL, follows
from app.seeds import _seed
from app.seeds.demo import reset_demo, seed_snapshot


# ---- helpers ----------------------------------------------------------------
def user(email):
    return db.session.scalar(select(User).where(User.email == email))


def demo_state():
    """The demo user's data by natural keys (comparable across resets)."""
    demo = user(DEMO_EMAIL)
    email = dict(db.session.execute(select(User.id, User.email)).all())
    posts = db.session.scalars(select(Post)).all()
    key = {p.id: (email[p.user_id], p.caption) for p in posts}
    own = sorted(
        (p.img_url, p.caption, p.likes,
         tuple(sorted((email[c.user_id], c.body) for c in p.comments)),
         tuple(sorted(email[like.user_id] for like in p.post_likes)))
        for p in posts if p.user_id == demo.id)
    comments = sorted((key[c.post_id], c.body) for c in db.session.scalars(
        select(Comment).where(Comment.user_id == demo.id)) if key[c.post_id][0] != DEMO_EMAIL)
    likes = sorted(key[like.post_id] for like in db.session.scalars(
        select(PostLike).where(PostLike.user_id == demo.id)) if key[like.post_id][0] != DEMO_EMAIL)
    following = sorted(email[i] for i in db.session.scalars(
        select(follows.c.followed_id).where(follows.c.follower_id == demo.id)))
    followers = sorted(email[i] for i in db.session.scalars(
        select(follows.c.follower_id).where(follows.c.followed_id == demo.id)))
    return {'profile': (demo.username, demo.first_name, demo.last_name, demo.profile_picture),
            'posts': own, 'comments': comments, 'likes': likes,
            'following': following, 'followers': followers}


def other_users_state():
    """Everything that does NOT involve the demo user, by natural keys."""
    demo_id = user(DEMO_EMAIL).id
    email = dict(db.session.execute(select(User.id, User.email)).all())
    demo_posts = set(db.session.scalars(select(Post.id).where(Post.user_id == demo_id)))
    posts = sorted((email[p.user_id], p.caption, p.img_url, p.likes)
                   for p in db.session.scalars(select(Post).where(Post.user_id != demo_id)))
    comments = sorted((email[c.user_id], c.post_id, c.body) for c in db.session.scalars(
        select(Comment).where(Comment.user_id != demo_id)) if c.post_id not in demo_posts)
    likes = sorted((email[lk.user_id], lk.post_id) for lk in db.session.scalars(
        select(PostLike).where(PostLike.user_id != demo_id)) if lk.post_id not in demo_posts)
    follow_rows = sorted((email[a], email[b]) for a, b in db.session.execute(
        select(follows.c.follower_id, follows.c.followed_id)
        .where(follows.c.follower_id != demo_id, follows.c.followed_id != demo_id)))
    users = sorted(email.values())
    return {'users': users, 'posts': posts, 'comments': comments, 'likes': likes,
            'follows': follow_rows}


def run_reset():
    changes = reset_demo()
    db.session.commit()
    return changes


def post_of(email, caption=None):
    query = select(Post).where(Post.user_id == user(email).id).order_by(Post.id)
    if caption:
        query = query.where(Post.caption == caption)
    return db.session.scalars(query).first()


def mess_up_as_visitors():
    """What visitors do with the demo login, plus activity by other users."""
    demo, marnie, bobbie = user(DEMO_EMAIL), user('marnie@aa.io'), user('bobbie@aa.io')
    demo_posts = db.session.scalars(select(Post).where(Post.user_id == demo.id).order_by(Post.id)).all()
    db.session.delete(demo_posts[0])                    # demo deletes a seed post
    demo_posts[1].caption = 'hacked caption'            # ... edits another
    new = Post(user_id=demo.id, img_url='https://x/new.webp', caption='visitor post', likes=0)
    db.session.add(new)
    db.session.flush()
    db.session.add(Comment(user_id=marnie.id, post_id=new.id, body='nice!'))
    db.session.add(Comment(user_id=demo.id, post_id=post_of('bobbie@aa.io').id, body='spam'))
    # demo removes one of their seed comments on someone else's post
    theirs = db.session.scalars(select(Comment).join(Post, Comment.post_id == Post.id).where(
        Comment.user_id == demo.id, Post.user_id != demo.id)).first()
    if theirs:
        db.session.delete(theirs)
    # demo unlikes a seeded like and likes something new
    seeded_like = db.session.scalars(select(PostLike).where(PostLike.user_id == demo.id)).first()
    if seeded_like:
        db.session.delete(seeded_like)
    target = post_of('taytay@aa.io') or post_of('janedoe@aa.io')
    db.session.add(PostLike(user_id=demo.id, post_id=target.id))
    # follows: demo unfollows everyone, follows a new user, marnie unfollows demo
    db.session.execute(delete(follows).where(follows.c.follower_id == demo.id))
    db.session.execute(delete(follows).where(follows.c.follower_id == marnie.id,
                                             follows.c.followed_id == demo.id))
    db.session.execute(insert(follows).values(follower_id=demo.id, followed_id=user('healz@aa.io').id))
    # Activity that has nothing to do with the demo user must survive.
    real = User(username='realperson', email='real@example.com', password='pw',
                first_name='Real', last_name='Person')
    db.session.add(real)
    db.session.flush()
    real_post = Post(user_id=real.id, img_url='https://x/real.webp', caption='mine', likes=1)
    db.session.add(real_post)
    db.session.flush()
    db.session.add(Comment(user_id=marnie.id, post_id=real_post.id, body='welcome'))
    db.session.add(PostLike(user_id=bobbie.id, post_id=real_post.id))
    db.session.execute(insert(follows).values(follower_id=real.id, followed_id=marnie.id))
    db.session.commit()


# ---- tests --------------------------------------------------------------------
@pytest.fixture
def seeded(app):
    _seed()
    return app


def test_fresh_seed_needs_no_changes(seeded):
    assert run_reset() == {}


def test_snapshot_describes_the_seeded_demo_user(seeded):
    snapshot = seed_snapshot()
    state = demo_state()
    assert snapshot['profile']['email'] == DEMO_EMAIL
    assert len(snapshot['posts']) == len(state['posts']) > 0
    assert snapshot['following'] == state['following']
    assert snapshot['followers'] == state['followers']


def test_reset_restores_demo_and_leaves_everyone_else_alone(seeded):
    expected = demo_state()
    mess_up_as_visitors()
    others_before = other_users_state()
    assert demo_state() != expected

    changes = run_reset()

    assert changes['posts removed'] == 2          # the visitor post + the edited one
    assert changes['posts restored'] == 2         # the deleted one + the edited one
    assert demo_state() == expected
    assert other_users_state() == others_before
    # Like counters everywhere equal the real number of likes.
    for post in db.session.scalars(select(Post)):
        assert post.likes == db.session.scalar(
            select(func.count()).select_from(PostLike).where(PostLike.post_id == post.id))


def test_reset_is_idempotent(seeded):
    mess_up_as_visitors()
    assert run_reset()
    state = demo_state()
    assert run_reset() == {}
    assert demo_state() == state


def test_reset_recreates_a_deleted_demo_account(seeded):
    expected = demo_state()
    db.session.delete(user(DEMO_EMAIL))
    db.session.commit()
    assert user(DEMO_EMAIL) is None
    changes = run_reset()
    assert changes['demo user recreated'] == 1
    assert demo_state() == expected
    assert user(DEMO_EMAIL).check_password('password')


def test_cli_reset_and_dry_run(seeded):
    runner = seeded.test_cli_runner()
    mess_up_as_visitors()
    messed = demo_state()
    result = runner.invoke(args=['demo', 'reset', '--dry-run'])
    assert result.exit_code == 0, result.output
    assert 'dry run, nothing saved' in result.output
    db.session.expire_all()
    assert demo_state() == messed

    result = runner.invoke(args=['demo', 'reset'])
    assert result.exit_code == 0, result.output
    assert 'posts restored 2' in result.output
    result = runner.invoke(args=['demo', 'reset'])
    assert 'already matches the seed data' in result.output


def test_cli_refuses_an_empty_database(app):
    result = app.test_cli_runner().invoke(args=['demo', 'reset'])
    assert result.exit_code == 1
    assert 'flask seed all' in result.output


def test_cli_runs_in_production(prod_env, tmp_path):
    prod_env.setenv('DATABASE_URL', f'sqlite:///{tmp_path}/prod.db')
    app = create_app('production')
    with app.app_context():
        db.create_all()
        _seed()
        db.session.delete(db.session.scalars(select(Post).where(
            Post.user_id == user(DEMO_EMAIL).id)).first())
        db.session.commit()
        result = app.test_cli_runner().invoke(args=['demo', 'reset'])
        assert result.exit_code == 0, result.output
        assert 'posts restored 1' in result.output
        db.session.remove()


def test_demo_account_cannot_be_deleted(seeded, client):
    demo = user(DEMO_EMAIL)
    client.post('/api/auth/login', json={'email': DEMO_EMAIL, 'password': 'password'})
    response = client.delete(f'/api/users/{demo.id}')
    assert response.status_code == 403
    assert response.get_json() == {'errors': ['The demo account cannot be deleted.']}
    assert user(DEMO_EMAIL) is not None


def test_demo_uploads_are_tagged_for_expiry(seeded, client, monkeypatch):
    for name in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN'):
        monkeypatch.setenv(name, 'testing')
    monkeypatch.delenv('AWS_PROFILE', raising=False)
    seeded.config.update(S3_BUCKET='postpix-media-test', AWS_REGION='us-east-2',
                         MEDIA_BASE_URL='https://m.example/media')
    def image():
        buffer = io.BytesIO()
        Image.new('RGB', (64, 64)).save(buffer, 'PNG')
        buffer.seek(0)
        return buffer

    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-2')
        s3.create_bucket(Bucket='postpix-media-test',
                         CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
        client.post('/api/auth/login', json={'email': DEMO_EMAIL, 'password': 'password'})
        body = client.post('/api/img/upload', data={'image': (image(), 'a.png')},
                           content_type='multipart/form-data').get_json()
        key = body['url'].removeprefix('https://m.example/media/')
        tags = s3.get_object_tagging(Bucket='postpix-media-test', Key=key)['TagSet']
        assert tags == [{'Key': 'postpix-demo', 'Value': 'true'}]
        # Other users' uploads are not tagged.
        client.post('/api/auth/logout')
        client.post('/api/auth/login', json={'email': 'marnie@aa.io', 'password': 'password'})
        body = client.post('/api/img/upload', data={'image': (image(), 'b.png')},
                           content_type='multipart/form-data').get_json()
        key = body['url'].removeprefix('https://m.example/media/')
        assert s3.get_object_tagging(Bucket='postpix-media-test', Key=key)['TagSet'] == []

"""Q2: the logged-in user's own payload says whether it is the demo account."""
from app.models import User, db
from app.models.user import DEMO_EMAIL


def _make(email, username):
    db.session.add(User(username=username, email=email, password='password',
                        first_name='a', last_name='b'))
    db.session.commit()


def test_demo_user_payload_has_is_demo_true(client):
    _make(DEMO_EMAIL, 'Demo')
    body = client.post('/api/auth/login', json={'email': DEMO_EMAIL, 'password': 'password'}).get_json()
    assert body['isDemo'] is True
    assert client.get('/api/auth/').get_json()['isDemo'] is True


def test_other_users_get_is_demo_false(client):
    _make('marnie@aa.io', 'marnie')
    body = client.post('/api/auth/login', json={'email': 'marnie@aa.io', 'password': 'password'}).get_json()
    assert body['isDemo'] is False


def test_public_profiles_do_not_expose_the_flag(client):
    _make(DEMO_EMAIL, 'Demo')
    _make('marnie@aa.io', 'marnie')
    client.post('/api/auth/login', json={'email': 'marnie@aa.io', 'password': 'password'})
    demo_id = db.session.scalar(db.select(User.id).where(User.email == DEMO_EMAIL))
    assert 'isDemo' not in client.get(f'/api/users/{demo_id}').get_json()

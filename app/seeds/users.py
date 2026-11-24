from app.models import db, User
from app.media import seed_avatar_url
# from faker import Faker

# fake = Faker()
# user_data = []

# for i in range(16):
#     user_data.append(
#         {'first_name': fake.first_name(), 'last_name': fake.last_name(), 'password': fake.password(), 'username': fake.simple_profile()['username'], 'email': fake.free_email(), 'profile_picture': fake.image_url()}
#     )
# print(user_data)

# Adds a demo user, you can add other users here if you want
def seed_users():
    demo = User( #1
        username='Demo', email='demo@aa.io', password='password', first_name='demo', last_name='user', profile_picture=seed_avatar_url(1))
    marnie = User( #2
        username='marnie', email='marnie@aa.io', password='password', first_name='demo1', last_name='user1', profile_picture=seed_avatar_url(2))
    bobbie = User( #3
        username='bobbie', email='bobbie@aa.io', password='password', first_name='demo2', last_name='user2', profile_picture=seed_avatar_url(3))
    theo = User( #4
        username='theoman42', email='theo@aa.io', password='password', first_name='theo', last_name='fan', profile_picture=seed_avatar_url(4))
    derek = User( #5
        username='torman', email='tor@aa.io', password='password', first_name='derk', last_name='tor', profile_picture=seed_avatar_url(5))
    alan = User( #6
        username='awdel88', email='awd@aa.io', password='password', first_name='alan', last_name='del', profile_picture=seed_avatar_url(6))
    gabe = User( #7
        username='gabeknight', email='knight@aa.io', password='password', first_name='gabriel', last_name='knight', profile_picture=seed_avatar_url(7))
    grace = User( #8
        username='grace2', email='chang@aa.io', password='password', first_name='grace', last_name='wong', profile_picture=seed_avatar_url(8))
    wilson = User( #9
        username='lalawill', email='healz@aa.io', password='password', first_name='wilson', last_name='lee', profile_picture=seed_avatar_url(9))
    chris = User( #10
        username='chrisTheMan', email='tofu@aa.io', password='password', first_name='chris', last_name='pork', profile_picture=seed_avatar_url(10))
        # //----------------------------
    matt = User( #11
        username='MattyIce', email='mattyice@aa.io', password='password', first_name='matt', last_name='smith', profile_picture=seed_avatar_url(11))
    taylor = User( #12
        username='taytay', email='taytay@aa.io', password='password', first_name='taylor', last_name='armstrong', profile_picture=seed_avatar_url(12))
    jane = User( #13
        username='janedoe', email='janedoe@aa.io', password='password', first_name='jane', last_name='doe', profile_picture=seed_avatar_url(13))
    danielle = User( #14
        username='itsdanelle', email='danelle@aa.io', password='password', first_name='danielle', last_name='schrader', profile_picture=seed_avatar_url(14))
    ronald = User( #15
        username='ronweasley', email='weasley@aa.io', password='password', first_name='ronald', last_name='weasley', profile_picture=seed_avatar_url(15))



    demo.followers = [marnie, bobbie, alan, theo, derek, chris, ronald]
    marnie.followers = [bobbie, demo, alan, gabe, wilson]
    bobbie.followers = [marnie, demo, grace, theo, derek, alan, chris]
    theo.followers = [alan, derek, gabe, ronald]
    derek.followers = [theo, alan, bobbie, danielle]
    gabe.followers = [alan, chris, demo, marnie, jane]
    grace.followers = [chris, bobbie, marnie, taylor]
    chris.followers = [alan, gabe, bobbie, jane]
    matt.followers = [demo, gabe, chris, taylor]
    taylor.followers = [jane, ronald, bobbie, grace]
    jane.followers = [chris, danielle, derek, bobbie]
    danielle.followers = [matt, theo, demo, ronald]
    ronald.followers = [matt, alan, marnie, taylor, danielle]


    db.session.add(demo)
    db.session.add(marnie)
    db.session.add(bobbie)
    db.session.add(theo)
    db.session.add(derek)
    db.session.add(alan)
    db.session.add(gabe)
    db.session.add(grace)
    db.session.add(wilson)
    db.session.add(chris)
    db.session.add(matt)
    db.session.add(taylor)
    db.session.add(jane)
    db.session.add(danielle)
    db.session.add(ronald)




    db.session.commit()
    # Seed number (#1, #2, ...) -> User, so other seed files can refer to
    # users without assuming database ids start at 1.
    return {n: user for n, user in enumerate([
        demo, marnie, bobbie, theo, derek, alan, gabe, grace, wilson, chris,
        matt, taylor, jane, danielle, ronald], start=1)}

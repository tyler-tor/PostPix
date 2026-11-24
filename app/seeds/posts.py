from app.models import db, Post
from app.media import seed_post_url

# Images: seed_post_url(n) gives MEDIA_BASE_URL + the S3 key for post n from
# media_manifest.json, or the original hot-linked URL when MEDIA_BASE_URL is
# not set (local development).
# Like counts are NOT set here: posts.likes is recalculated from the real
# post_likes rows at the end of seed_post_likes() so they always match.


def seed_posts(users):
    """users: {seed number: User} from seed_users(). Returns {seed number: Post}."""
    post1 = Post(
      user_id=users[1].id,
      img_url=seed_post_url(1),
      caption='this is post1 for demo user'
    )
    post2 = Post(
      user_id=users[2].id,
      img_url=seed_post_url(2),
      caption='this is post2 for marnie'
    )
    post3 = Post(
      user_id=users[3].id,
      img_url=seed_post_url(3),
      caption='this is post3 for bobbie'
    )

    post4 = Post(
      user_id=users[6].id,
      img_url=seed_post_url(4),
      caption='check out my first project!'
    )


    post5 = Post(
      user_id=users[4].id,
      img_url=seed_post_url(5),
      caption='best sova line up.'
    )

    post6 = Post(
      user_id=users[4].id,
      img_url=seed_post_url(6),
      caption='double shock dart at A!'
    )

    post7 = Post(
      user_id=users[5].id,
      img_url=seed_post_url(7),
      caption='look at my new design!'
    )

    post8 = Post(
      user_id=users[5].id,
      img_url=seed_post_url(8),
      caption='i did it!'
    )

    post9 = Post(
      user_id=users[5].id,
      img_url=seed_post_url(9),
      caption='I hate icebox'
    )

    post10 = Post(
      user_id=users[6].id,
      img_url=seed_post_url(10),
      caption='more darts?'
    )

    post11 = Post(
      user_id=users[6].id,
      img_url=seed_post_url(11),
      caption='double darts!'
    )

    post12 = Post(
      user_id=users[7].id,
      img_url=seed_post_url(12),
      caption='sova main?!'
    )

    post13 = Post(
      user_id=users[7].id,
      img_url=seed_post_url(13),
      caption='never used this dart'
    )

    post14 = Post(
      user_id=users[7].id,
      img_url=seed_post_url(14),
      caption='double darts!'
    )

    post15 = Post(
      user_id=users[8].id,
      img_url=seed_post_url(15),
      caption='double darts for b'
    )
    post16 = Post(
      user_id=users[8].id,
      img_url=seed_post_url(16),
      caption='double darts a main'
    )
    post17 = Post(
      user_id=users[8].id,
      img_url=seed_post_url(17),
      caption='double darts for tiles'
    )

    post18 = Post(
      user_id=users[9].id,
      img_url=seed_post_url(18),
      caption='recon dart?!'
    )

    post19 = Post(
      user_id=users[9].id,
      img_url=seed_post_url(19),
      caption='A hell recon?'
    )

    post20 = Post(
      user_id=users[9].id,
      img_url=seed_post_url(20),
      caption='recon dart for garden'
    )

    post21 = Post(
      user_id=users[10].id,
      img_url=seed_post_url(21),
      caption='recon dart for A hell'
    )
    # ----------------------------------------------------------------------------------
    post22 = Post(
      user_id=users[10].id,
      img_url=seed_post_url(22),
      caption='If I dont like something, Ill stay away from it.'
    )
    post23 = Post(
      user_id=users[10].id,
      img_url=seed_post_url(23),
      caption='He figured a few sticks of dynamite were easier than a fishing pole to catch fish.'
    )
    post24 = Post(
      user_id=users[1].id,
      img_url=seed_post_url(24),
      caption='The three-year-old girl ran down the beach as the kite flew behind her.'
    )
    post25 = Post(
      user_id=users[1].id,
      img_url=seed_post_url(25),
      caption='The light in his life was actually a fire burning all around him.'
    )
    post26 = Post(
      user_id=users[2].id,
      img_url=seed_post_url(26),
      caption='She was the type of girl who wanted to live in a pink house.'
    )
    post27 = Post(
      user_id=users[2].id,
      img_url=seed_post_url(27),
      caption='He had decided to accept his fate of accepting his fate.'
    )
    post28 = Post(
      user_id=users[3].id,
      img_url=seed_post_url(28),
      caption='Its important to remember to be aware of rampaging grizzly bears.'
    )
    post29 = Post(
      user_id=users[3].id,
      img_url=seed_post_url(29),
      caption='There should have been a time and a place, but this wasnt it.'
    )
    post30 = Post(
      user_id=users[11].id,
      img_url=seed_post_url(30),
      caption='The minute she landed she understood the reason this was a fly-over state.'
    )
    post31 = Post(
      user_id=users[11].id,
      img_url=seed_post_url(31),
      caption='Two more days and all his problems would be solved.'
    )
    post32 = Post(
      user_id=users[11].id,
      img_url=seed_post_url(32),
      caption='Purple is the best city in the forest.'
    )
    post33 = Post(
      user_id=users[12].id,
      img_url=seed_post_url(33),
      caption='She used her own hair in the soup to give it more flavor.'
    )
    post34 = Post(
      user_id=users[12].id,
      img_url=seed_post_url(34),
      caption='Id always thought lightning was something only I could see.'
    )
    post35 = Post(
      user_id=users[12].id,
      img_url=seed_post_url(35),
      caption='You cant compare apples and oranges, but what about bananas and plantains?'
    )
    post36 = Post(
      user_id=users[13].id,
      img_url=seed_post_url(36),
      caption='The best key lime pie is still up for debate.'
    )
    post37 = Post(
      user_id=users[13].id,
      img_url=seed_post_url(37),
      caption='I love bacon, beer, birds, and baboons.'
    )
    post38 = Post(
      user_id=users[13].id,
      img_url=seed_post_url(38),
      caption='The beauty of the sunset was obscured by the industrial cranes.'
    )
    post39 = Post(
      user_id=users[14].id,
      img_url=seed_post_url(39),
      caption='She did a happy dance because all of the socks from the dryer matched.'
    )
    post40 = Post(
      user_id=users[14].id,
      img_url=seed_post_url(40),
      caption='The thick foliage and intertwined vines made the hike nearly impossible.'
    )
    post41 = Post(
      user_id=users[14].id,
      img_url=seed_post_url(41),
      caption='That must be the tenth time Ive been arrested for selling deep-fried cigars.'
    )
    post42 = Post(
      user_id=users[15].id,
      img_url=seed_post_url(42),
      caption='Jerry liked to look at paintings while eating garlic ice cream.'
    )
    post43 = Post(
      user_id=users[15].id,
      img_url=seed_post_url(43),
      caption='He was sure the Devil created red sparkly glitter.'
    )
    post44 = Post(
      user_id=users[15].id,
      img_url=seed_post_url(44),
      caption='The childs favorite Christmas gift was the large box her fathers lawnmower came in.'
    )
    post45 = Post(
      user_id=users[4].id,
      img_url=seed_post_url(45),
      caption='He wondered if it could be called a beach if there was no sand.'
    )
    post46 = Post(
      user_id=users[1].id,
      img_url=seed_post_url(46),
      caption='It had been sixteen days since the zombies first attacked.'
    )
    post47 = Post(
      user_id=users[1].id,
      img_url=seed_post_url(47),
      caption='He had a vague sense that trees gave birth to dinosaurs.'
    )
    post48 = Post(
      user_id=users[2].id,
      img_url=seed_post_url(48),
      caption='Peanut butter and jelly caused the elderly lady to think about her past.'
    )
    post49 = Post(
      user_id=users[5].id,
      img_url=seed_post_url(49),
      caption='He never understood why what, when, and where left out who.'
    )
    post50 = Post(
      user_id=users[8].id,
      img_url=seed_post_url(50),
      caption='He created a pig burger out of beef.'
    )

    db.session.add(post1)
    db.session.add(post2)
    db.session.add(post3)
    db.session.add(post4)
    db.session.add(post5)
    db.session.add(post6)
    db.session.add(post7)
    db.session.add(post8)
    db.session.add(post9)
    db.session.add(post10)
    db.session.add(post11)
    db.session.add(post12)
    db.session.add(post13)
    db.session.add(post14)
    db.session.add(post15)
    db.session.add(post16)
    db.session.add(post17)
    db.session.add(post18)
    db.session.add(post19)
    db.session.add(post20)
    db.session.add(post21)
    db.session.add_all([
      post22,
      post23,
      post24,
      post25,
      post26,
      post27,
      post28,
      post29,
      post30,
      post31,
      post32,
      post33,
      post34,
      post35,
      post36,
      post37,
      post38,
      post39,
      post40,
      post41,
      post42,
      post43,
      post44,
      post45,
      post46,
      post47,
      post48,
      post49,
      post50
      ])

    db.session.commit()
    return {n: post for n, post in enumerate([
        post1, post2, post3, post4, post5, post6, post7, post8, post9, post10,
        post11, post12, post13, post14, post15, post16, post17, post18, post19, post20,
        post21, post22, post23, post24, post25, post26, post27, post28, post29, post30,
        post31, post32, post33, post34, post35, post36, post37, post38, post39, post40,
        post41, post42, post43, post44, post45, post46, post47, post48, post49, post50], start=1)}

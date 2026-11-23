from sqlalchemy import text
from app.models import db, PostLike


def recount_post_likes():
    """Set every posts.likes counter to the real number of post_likes rows."""
    db.session.execute(text(
        'UPDATE posts SET likes = '
        '(SELECT COUNT(*) FROM post_likes WHERE post_likes.post_id = posts.id)'
    ))
    db.session.commit()

def seed_post_likes(users, posts):
    """users/posts: {seed number: row} from seed_users()/seed_posts()."""
    postlike1 = PostLike(
        user_id=users[1].id,
        post_id=posts[3].id
    )
    postlike2 = PostLike(
        user_id=users[2].id,
        post_id=posts[1].id
    )
    postlike3 = PostLike(
        user_id=users[3].id,
        post_id=posts[2].id
    )

    postlike4 = PostLike(
        user_id=users[4].id,
        post_id=posts[6].id
    )
    postlike5 = PostLike(
        user_id=users[4].id,
        post_id=posts[15].id
    )
    postlike6 = PostLike(
        user_id=users[4].id,
        post_id=posts[16].id
    )
    postlike7 = PostLike(
        user_id=users[5].id,
        post_id=posts[16].id
    )
    postlike8 = PostLike(
        user_id=users[6].id,
        post_id=posts[16].id
    )
    postlike9 = PostLike(
        user_id=users[8].id,
        post_id=posts[16].id
    )

    postlike10 = PostLike(
        user_id=users[7].id,
        post_id=posts[21].id
    )
    postlike11 = PostLike(
        user_id=users[8].id,
        post_id=posts[21].id
    )

    postlike12 = PostLike(
        user_id=users[10].id,
        post_id=posts[6].id
    )
    postlike13 = PostLike(
        user_id=users[10].id,
        post_id=posts[4].id
    )
    postlike14 = PostLike(
        user_id=users[1].id,
        post_id=posts[4].id
    )
    postlike15 = PostLike(
        user_id=users[2].id,
        post_id=posts[4].id
    )
    postlike16 = PostLike(
        user_id=users[3].id,
        post_id=posts[7].id
    )
    postlike17 = PostLike(
        user_id=users[8].id,
        post_id=posts[7].id
    )



    db.session.add(postlike1)
    db.session.add(postlike2)
    db.session.add(postlike3)
    db.session.add(postlike4)
    db.session.add(postlike5)
    db.session.add(postlike6)
    db.session.add(postlike7)
    db.session.add(postlike8)
    db.session.add(postlike9)
    db.session.add(postlike10)
    db.session.add(postlike11)
    db.session.add(postlike12)
    db.session.add(postlike13)
    db.session.add(postlike14)
    db.session.add(postlike15)
    db.session.add(postlike16)
    db.session.add(postlike17)

    db.session.commit()
    recount_post_likes()


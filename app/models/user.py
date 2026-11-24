from .db import db, TimestampMixin, iso
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy import select, func, exists, literal

# Who follows whom: one row per (follower, followed) pair, no duplicates.
follows = db.Table('follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    db.UniqueConstraint('follower_id', 'followed_id', name='uq_follows_follower_followed'),
    # "Who follows user X": the unique constraint above only helps lookups that
    # start with follower_id.
    db.Index('ix_follows_followed_id', 'followed_id'),
)

class User(TimestampMixin, db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashed_password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255),
    default='https://t3.ftcdn.net/jpg/00/64/67/52/240_F_64675209_7ve2XQANuzuHjMZXP3aIYIpsDKEbF5dD.jpg')
    #added first/lastname ----------------------------------------
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)

    # User search: ?q=ab matches lower(username) in a range (see /api/users/search).
    __table_args__ = (db.Index('ix_users_username_lower', func.lower(username)),)

    posts = db.relationship('Post', back_populates='users', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='users', cascade='all, delete-orphan')

    # follows = db.relationship('User', secondary='follows', primaryjoin="follows.c.user_id==users.c.id",
    #                             secondaryjoin="follows.c.following_id==users.c.id", backref=db.backref('follows', lazy='dynamic'),
    #                             cascade='all, delete-orphan', single_parent=True)
    followers = db.relationship(
        'User', secondary=follows,
        primaryjoin=(follows.c.followed_id == id),
        secondaryjoin=(follows.c.follower_id == id),
        backref=db.backref('follows', lazy='select'), lazy='select')

    post_likes = db.relationship('PostLike', back_populates='users', cascade='all, delete-orphan')

    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # ------------------------------------------------------------------
    # Serialization. A user payload never contains the follower / following /
    # likes lists (those grew with the data and cost 3 extra queries per user).
    # It carries COUNTS computed by the database in the same query, plus
    # "isFollowedByMe" for the logged-in viewer. The lists are fetched by their
    # own endpoints (/followers, /following) when a screen needs them.
    # ------------------------------------------------------------------
    @staticmethod
    def stats_select(viewer_id=None):
        """SELECT User + follower/following/post counts + isFollowedByMe, as one
        query. Add your own .where() / .order_by() / .limit() and run it with
        db.session.execute(...); pass each row to User.row_to_dict()."""
        from .posts import Post  # local import: posts.py imports from user.py's package

        follower_count = (select(func.count()).select_from(follows)
                          .where(follows.c.followed_id == User.id)
                          .correlate(User).scalar_subquery())
        following_count = (select(func.count()).select_from(follows)
                           .where(follows.c.follower_id == User.id)
                           .correlate(User).scalar_subquery())
        post_count = (select(func.count()).select_from(Post)
                      .where(Post.user_id == User.id)
                      .correlate(User).scalar_subquery())
        if viewer_id is None:
            followed_by_me = literal(False)
        else:
            followed_by_me = exists().where(
                follows.c.follower_id == viewer_id,
                follows.c.followed_id == User.id).correlate(User)
        return select(User,
                      follower_count.label('follower_count'),
                      following_count.label('following_count'),
                      post_count.label('post_count'),
                      followed_by_me.label('followed_by_me'))

    @staticmethod
    def row_to_dict(row):
        user = row[0]
        return {
            'id': user.id,
            'username': user.username,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'profilePicture': user.profile_picture,
            'followerCount': row.follower_count,
            'followingCount': row.following_count,
            'postCount': row.post_count,
            'isFollowedByMe': bool(row.followed_by_me),
            'createdAt': iso(user.created_at),
            'updatedAt': iso(user.updated_at),
        }

    def to_public(self, viewer_id=None):
        """Fields any logged-in user may see (no email). One query."""
        if viewer_id is None and current_user and current_user.is_authenticated:
            viewer_id = current_user.id
        row = db.session.execute(
            User.stats_select(viewer_id).where(User.id == self.id)).one()
        return User.row_to_dict(row)

    def to_self(self):
        """Everything in to_public() plus private fields. Only for the user
        themselves (login, signup, GET /api/auth/)."""
        return {**self.to_public(viewer_id=self.id), 'email': self.email}

    # Old name kept so existing code keeps working; it is the PUBLIC view.
    to_dict = to_public

    def to_summary(self):
        """Smallest user shape, for lists (followers, likes, search, suggestions)."""
        return user_summary(self)


def user_summary(user):
    return {'id': user.id, 'username': user.username,
            'firstName': user.first_name, 'lastName': user.last_name,
            'profilePicture': user.profile_picture}

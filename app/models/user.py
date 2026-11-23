from .db import db, TimestampMixin, iso
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Who follows whom: one row per (follower, followed) pair, no duplicates.
follows = db.Table('follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.UniqueConstraint('follower_id', 'followed_id', name='uq_follows_follower_followed')
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

    def to_public(self):
        """Fields any logged-in user may see. No email or other private data."""
        return {
            'id': self.id,
            'username': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'followers': [{'userId': follower.id, 'username': follower.username, 'profilePicture': follower.profile_picture} for follower in self.followers],
            'following': [{'userId': follower.id, 'username': follower.username, 'profilePicture': follower.profile_picture} for follower in self.follows],
            'likes' : [{'postId': like.post_id} for like in self.post_likes],
            'profilePicture': self.profile_picture,
            'createdAt': iso(self.created_at),
            'updatedAt': iso(self.updated_at)
        }

    def to_self(self):
        """Everything in to_public() plus private fields. Only for the user
        themselves (login, signup, GET /api/auth/)."""
        return {**self.to_public(), 'email': self.email}

    # Old name kept so existing code keeps working; it is the PUBLIC view.
    to_dict = to_public

    # def un_follow(self, id):
    #     for i in range(len(self.follows)):
    #         user = self.follows[i]
    #         if(user.id == id):
    #             return

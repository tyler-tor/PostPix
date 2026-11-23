from .db import db, environment, SCHEMA, add_prefix_for_prod
from datetime import datetime


class PostLike(db.Model):
    __tablename__ = 'post_likes'

    # One like per user per post. The database rejects duplicates even if two
    # requests race each other.
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='uq_post_likes_user_post'),
    )
    if environment == "production":
        __table_args__ = __table_args__ + ({'schema': SCHEMA},)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('posts.id')), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    users = db.relationship('User', back_populates="post_likes", single_parent=True) #removed cascade here.
    posts = db.relationship('Post', back_populates='post_likes', single_parent=True) # here too


    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'postId': self.post_id,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }

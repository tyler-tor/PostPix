from .db import db, TimestampMixin, iso


class Post(TimestampMixin, db.Model):
    __tablename__ = 'posts'

    __table_args__ = (
        # Profile pages: one user's posts, newest first. (Plain ascending
        # indexes are enough: both SQLite and Postgres read an index backwards,
        # and this keeps `flask db check` free of false alarms.)
        db.Index('ix_posts_user_id_created_at', 'user_id', 'created_at'),
        # Explore and the home feed: all posts newest first (P22 cursor pagination).
        db.Index('ix_posts_created_at_id', 'created_at', 'id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    img_url = db.Column(db.String(255))
    caption = db.Column(db.String(150))

    users = db.relationship('User', back_populates="posts", single_parent=True)
    comments = db.relationship('Comment', back_populates="posts", cascade='all, delete-orphan', single_parent=True)
    post_likes = db.relationship('PostLike', back_populates="posts", cascade='all, delete-orphan')


    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'likes': self.likes,
            'imgUrl': self.img_url,
            'caption': self.caption,
            'createdAt': iso(self.created_at),
            'updatedAt': iso(self.updated_at)
        }

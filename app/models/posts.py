from .db import db, TimestampMixin, iso


class Post(TimestampMixin, db.Model):
    __tablename__ = 'posts'

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

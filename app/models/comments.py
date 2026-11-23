from .db import db, TimestampMixin, iso


class Comment(TimestampMixin, db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    body = db.Column(db.String(255))

    users = db.relationship('User', back_populates="comments", single_parent=True)
    posts = db.relationship('Post', back_populates='comments', single_parent=True)


    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'postId': self.post_id,
            'body': self.body,
            'createdAt': iso(self.created_at),
            'updatedAt': iso(self.updated_at)
        }

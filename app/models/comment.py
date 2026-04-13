from app import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
    
    quote_text = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    
    replies = db.relationship('Comment', 
                            backref=db.backref('parent', remote_side=[id]),
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    # ★修正：ここを 'user' から 'author' に変更しました！
    # これで画面側の comment.author.username が動くようになります
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    def get_like_count(self):
        """いいねの総数を返す"""
        return self.likes.count()

    def is_liked_by(self, user):
        """特定のユーザーが既にいいねしているか判定する"""
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter_by(user_id=user.id).first() is not None

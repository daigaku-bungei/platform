from app import db
from datetime import datetime


class Character(db.Model):
    """キャラクター設定モデル"""
    __tablename__ = 'character'

    id = db.Column(db.Integer, primary_key=True)

    # 基本情報
    name = db.Column(db.String(100), nullable=False)          # 名前
    role = db.Column(db.String(50))                           # 役割（主人公・ヒロイン・敵など）
    age = db.Column(db.String(50))                            # 年齢（「不明」「17歳」等に対応するためString）
    gender = db.Column(db.String(30))                         # 性別

    # 詳細設定
    appearance = db.Column(db.Text)                           # 外見
    personality = db.Column(db.Text)                          # 性格
    background = db.Column(db.Text)                           # 経歴・背景
    motivation = db.Column(db.Text)                           # 動機・目標
    notes = db.Column(db.Text)                                # その他メモ（自由記述）

    # 将来の拡張用
    image_url = db.Column(db.String(500))                     # キャラクター画像URL（任意）
    tags = db.Column(db.String(200))                          # タグ（カンマ区切り）

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # リレーション
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Character {self.name} (Novel: {self.novel_id})>'


class Plot(db.Model):
    """プロット（章・場面メモ）モデル"""
    __tablename__ = 'plot'

    id = db.Column(db.Integer, primary_key=True)

    # 章・場面の情報
    chapter_number = db.Column(db.Integer, nullable=False)    # 章番号（並び順に使用）
    title = db.Column(db.String(200))                         # 章タイトル（任意）
    summary = db.Column(db.Text, nullable=False)              # あらすじ・メモ本文

    # 執筆状態の管理
    STATUS_CHOICES = ['未着手', '執筆中', '完成']
    status = db.Column(db.String(20), default='未着手')       # 執筆ステータス

    # その他
    notes = db.Column(db.Text)                                # 補足メモ（伏線・ポイントなど）

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # リレーション
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 章番号の重複を作品内で防ぐ
    __table_args__ = (
        db.UniqueConstraint('novel_id', 'chapter_number', name='uq_novel_chapter'),
    )

    def __repr__(self):
        return f'<Plot 第{self.chapter_number}章: {self.title} (Novel: {self.novel_id})>'

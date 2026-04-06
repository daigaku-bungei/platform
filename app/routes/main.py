from flask import Blueprint, render_template, request
from sqlalchemy import func, or_
from app import db
from app.models.novel import Novel
from app.models.user import User
from app.models.like import Like

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    query = request.args.get('q', '').strip()

    if query:
        # 小説テーブルとユーザーテーブルを結合(join)して、
        # 作者名(User.username)も検索対象に含める
        search_results = Novel.query.join(User).filter(
            Novel.parent_id == None, # 連載の親か短編のみ
            or_(
                Novel.title.contains(query),
                Novel.genre.contains(query),
                Novel.tags.contains(query),
                User.username.contains(query) # ★作者名でもヒットするように追加
            )
        ).order_by(Novel.created_at.desc()).all()

        return render_template('search_results.html', novels=search_results, query=query)

    # 通常表示（最新の作品）
    latest_novels = Novel.query.filter(
        Novel.novel_type.in_(['short', 'series'])
    ).order_by(Novel.created_at.desc()).limit(5).all()

    # ▼▼▼ 人気作品の算出ロジックを大改造！ ▼▼▼
    # （いいね数 × 10） ＋ PV数 の「総合スコア」が高い順に並べ替えます！
    popular_novels = db.session.query(Novel).outerjoin(Like).group_by(Novel.id).filter(
        Novel.novel_type.in_(['short', 'series'])
    ).order_by((func.count(Like.id) * 20 + Novel.pv).desc()).limit(6).all()
    # ▲▲▲ ここまで ▲▲▲

    return render_template('index.html', latest_novels=latest_novels, popular_novels=popular_novels)

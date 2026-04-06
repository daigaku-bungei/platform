from flask import Blueprint, render_template, request
from sqlalchemy import func, or_
from app import db
from app.models.novel import Novel
from app.models.user import User
from app.models.like import Like
import csv
import io
from datetime import datetime
from flask import Response
from flask_login import login_required, current_user

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

@main_bp.route('/admin/backup')
@login_required
def download_backup():
    # 1. 管理者チェック（is_adminがTrueのユーザーだけが実行可能）
    if not getattr(current_user, 'is_admin', False):
        return "権限がありません。管理者アカウントでログインしてください。", 403

    # 2. メモリ上にCSVファイルを作成する準備
    si = io.StringIO()
    cw = csv.writer(si)

    # 3. ユーザーデータを書き込む
    cw.writerow(['--- ユーザーデータ ---'])
    cw.writerow(['ID', 'ユーザー名', 'メールアドレス', '登録日時'])
    for u in User.query.all():
        cw.writerow([u.id, u.username, u.email, u.created_at])

    cw.writerow([]) # 区切りの空行

    # 4. 小説データを書き込む
    cw.writerow(['--- 小説データ ---'])
    cw.writerow(['ID', 'タイトル', '投稿日時']) # 本文を入れると重くなるので、まずは基本情報のみ
    for n in Novel.query.all():
        cw.writerow([n.id, n.title, n.created_at])

    # 5. CSVファイルとして出力
    output = si.getvalue()
    si.close()

    # ファイル名に現在の日付と時間を入れる（例: bungei_backup_20260406_1930.csv）
    filename = f"bungei_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    # 日本語がExcelで文字化けしないように utf-8-sig でエンコードして返す
    return Response(
        output.encode('utf-8-sig'),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

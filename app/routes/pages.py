"""정적 페이지 라우트 (SSR — 네이버 Yeti 크롤링 대응)."""
from flask import Blueprint, Response, abort, redirect, render_template, session, url_for

from ..models import FemaleMember, User, db

bp = Blueprint("pages", __name__)


def _viewer_approved():
    if not session.get("user_id"):
        return False
    user = db.session.get(User, session["user_id"])
    return bool(user and user.status == "approved")


@bp.get("/")
def index():
    preview = (FemaleMember.query.filter_by(is_active=True)
               .order_by(FemaleMember.sort_order, FemaleMember.created_at.desc())
               .limit(6).all())
    return render_template("index.html", preview_members=preview)


@bp.get("/greeting")
def greeting():
    return render_template("greeting.html")


@bp.get("/license")
def license_page():
    return render_template("license.html")


@bp.get("/process")
def process():
    return render_template("process.html")


@bp.get("/video-meeting")
def video_meeting():
    return render_template("video_meeting.html")


@bp.get("/members")
def members():
    # 로그인 + 관리자 승인(approved) 회원만 잠금 해제
    rows = (FemaleMember.query.filter_by(is_active=True)
            .order_by(FemaleMember.sort_order, FemaleMember.created_at.desc()).all())
    return render_template("members.html", members=rows,
                           viewer_approved=_viewer_approved())


@bp.get("/members/<int:member_id>")
def member_detail(member_id):
    # 상세 프로필은 승인 회원 전용
    if not _viewer_approved():
        return redirect(url_for("auth.login_form"))
    m = db.session.get(FemaleMember, member_id)
    if not m or not m.is_active:
        abort(404)
    return render_template("member_detail.html", m=m)


@bp.get("/faq")
def faq():
    return render_template("faq.html")


@bp.get("/location")
def location():
    return render_template("location.html")


@bp.get("/robots.txt")
def robots():
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /signup",
        f"Sitemap: {url_for('pages.sitemap', _external=True)}",
    ]
    return Response("\n".join(lines), mimetype="text/plain")


@bp.get("/sitemap.xml")
def sitemap():
    endpoints = [
        "pages.index", "pages.greeting", "pages.license_page", "pages.process",
        "pages.video_meeting", "pages.members", "pages.faq", "pages.location",
    ]
    urls = "".join(
        f"<url><loc>{url_for(ep, _external=True)}</loc></url>" for ep in endpoints
    )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           f"{urls}</urlset>")
    return Response(xml, mimetype="application/xml")

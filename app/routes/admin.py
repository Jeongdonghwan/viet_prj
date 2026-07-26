"""관리자 — 가입 승인/차단, 여성회원 CRUD + 사진 업로드."""
import hmac
import os
import uuid
from functools import wraps

from flask import (Blueprint, abort, current_app, redirect, render_template,
                   request, session, url_for)
from PIL import Image, ImageOps

from .. import limiter
from ..models import FemaleMember, FemalePhoto, User, db

bp = Blueprint("admin", __name__, url_prefix="/admin")

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


# ---------- 인증 ----------

@bp.get("/login")
def login():
    if session.get("is_admin"):
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/login.html", error=None)


@bp.post("/login")
@limiter.limit("10 per hour", methods=["POST"])
def login_submit():
    cfg = current_app.config
    ok = (hmac.compare_digest(request.form.get("username", ""), cfg["ADMIN_USERNAME"])
          and hmac.compare_digest(request.form.get("password", ""), cfg["ADMIN_PASSWORD"]))
    if not ok:
        return render_template("admin/login.html", error="계정 정보가 올바르지 않습니다."), 401
    session["is_admin"] = True
    nxt = request.args.get("next", "")
    return redirect(nxt if nxt.startswith("/admin") else url_for("admin.dashboard"))


@bp.get("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin.login"))


# ---------- 대시보드 ----------

@bp.get("/")
@admin_required
def dashboard():
    stats = {
        "pending": User.query.filter_by(status="pending").count(),
        "approved": User.query.filter_by(status="approved").count(),
        "blocked": User.query.filter_by(status="blocked").count(),
        "members": FemaleMember.query.count(),
        "members_active": FemaleMember.query.filter_by(is_active=True).count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


# ---------- 가입 신청 관리 ----------

@bp.get("/users")
@admin_required
def users():
    status = request.args.get("status", "all")
    q = User.query.order_by(User.created_at.desc())
    if status in ("pending", "approved", "blocked"):
        q = q.filter_by(status=status)
    return render_template("admin/users.html", users=q.all(), status=status)


@bp.post("/users/<int:user_id>/status")
@admin_required
def user_status(user_id):
    user = db.session.get(User, user_id) or abort(404)
    new_status = request.form.get("status")
    if new_status not in ("pending", "approved", "blocked"):
        abort(400)
    user.status = new_status
    db.session.commit()
    return redirect(request.referrer or url_for("admin.users"))


# ---------- 여성회원 관리 ----------

@bp.get("/members")
@admin_required
def members():
    rows = FemaleMember.query.order_by(FemaleMember.sort_order,
                                       FemaleMember.created_at.desc()).all()
    return render_template("admin/members.html", members=rows)


@bp.post("/members")
@admin_required
def member_create():
    f = request.form
    try:
        age = int(f.get("age", ""))
    except ValueError:
        abort(400)
    m = FemaleMember(
        name_masked=f.get("name_masked", "").strip() or abort(400),
        age=age,
        region=f.get("region", "").strip() or abort(400),
        job_note=f.get("job_note", "").strip(),
        intro=f.get("intro", "").strip(),
        is_active=bool(f.get("is_active")),
        sort_order=int(f.get("sort_order") or 0),
    )
    db.session.add(m)
    db.session.commit()
    return redirect(url_for("admin.member_edit", member_id=m.id))


@bp.get("/members/<int:member_id>")
@admin_required
def member_edit(member_id):
    m = db.session.get(FemaleMember, member_id) or abort(404)
    return render_template("admin/member_edit.html", m=m)


@bp.post("/members/<int:member_id>")
@admin_required
def member_update(member_id):
    m = db.session.get(FemaleMember, member_id) or abort(404)
    f = request.form
    m.name_masked = f.get("name_masked", m.name_masked).strip()
    m.age = int(f.get("age") or m.age)
    m.region = f.get("region", m.region).strip()
    m.job_note = f.get("job_note", "").strip()
    m.intro = f.get("intro", "").strip()
    m.is_active = bool(f.get("is_active"))
    m.sort_order = int(f.get("sort_order") or 0)
    db.session.commit()
    return redirect(url_for("admin.member_edit", member_id=m.id))


@bp.post("/members/<int:member_id>/delete")
@admin_required
def member_delete(member_id):
    m = db.session.get(FemaleMember, member_id) or abort(404)
    for p in m.photos:
        _remove_photo_file(p)
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for("admin.members"))


# ---------- 사진 업로드 ----------

def _remove_photo_file(photo):
    path = os.path.join(current_app.static_folder, photo.path)
    try:
        os.remove(path)
    except OSError:
        pass


@bp.post("/members/<int:member_id>/photos")
@admin_required
def photo_upload(member_id):
    m = db.session.get(FemaleMember, member_id) or abort(404)
    files = request.files.getlist("photos")
    updir = os.path.join(current_app.config["UPLOAD_DIR"], str(m.id))
    os.makedirs(updir, exist_ok=True)

    saved = 0
    for file in files:
        if not file or not file.filename:
            continue
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            continue
        name = f"{uuid.uuid4().hex}.jpg"
        dest = os.path.join(updir, name)
        try:
            with Image.open(file.stream) as im:
                im = ImageOps.exif_transpose(im)
                if im.width > 1200:
                    im = im.resize((1200, round(im.height * 1200 / im.width)),
                                   Image.LANCZOS)
                if im.mode != "RGB":
                    im = im.convert("RGB")
                im.save(dest, "JPEG", quality=85, optimize=True)
        except Exception:
            current_app.logger.warning("사진 처리 실패: %s", file.filename)
            continue
        rel = f"uploads/members/{m.id}/{name}"
        is_first = not m.photos and saved == 0
        db.session.add(FemalePhoto(member_id=m.id, path=rel, is_main=is_first,
                                   sort_order=len(m.photos) + saved))
        saved += 1

    db.session.commit()
    return redirect(url_for("admin.member_edit", member_id=m.id))


@bp.post("/photos/<int:photo_id>/main")
@admin_required
def photo_set_main(photo_id):
    p = db.session.get(FemalePhoto, photo_id) or abort(404)
    for other in p.member.photos:
        other.is_main = (other.id == p.id)
    db.session.commit()
    return redirect(url_for("admin.member_edit", member_id=p.member_id))


@bp.post("/photos/<int:photo_id>/delete")
@admin_required
def photo_delete(photo_id):
    p = db.session.get(FemalePhoto, photo_id) or abort(404)
    member_id = p.member_id
    was_main = p.is_main
    _remove_photo_file(p)
    db.session.delete(p)
    db.session.flush()
    if was_main:
        remaining = FemalePhoto.query.filter_by(member_id=member_id).first()
        if remaining:
            remaining.is_main = True
    db.session.commit()
    return redirect(url_for("admin.member_edit", member_id=member_id))

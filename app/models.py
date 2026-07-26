from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _now():
    return datetime.now(timezone.utc)


class User(db.Model):
    """가입 신청 회원 — status가 approved여야 여성회원 열람 가능 (2차 구현)."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(16), unique=True, nullable=False, index=True)
    pw_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    birth = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    education = db.Column(db.String(20), nullable=False)
    job = db.Column(db.String(60), nullable=False)
    income_range = db.Column(db.String(30), nullable=False)
    is_single = db.Column(db.Boolean, default=False)
    is_married = db.Column(db.Boolean, default=False)
    is_remarriage = db.Column(db.Boolean, default=False)
    has_children = db.Column(db.Boolean, default=False)
    status = db.Column(
        db.Enum("pending", "approved", "blocked", name="user_status"),
        default="pending", nullable=False,
    )
    created_at = db.Column(db.DateTime, default=_now, nullable=False)


class FemaleMember(db.Model):
    """여성회원 — 관리자 페이지(2차)에서 CRUD. 현재 데이터 없으면 잠금 더미 노출."""
    __tablename__ = "female_members"

    id = db.Column(db.Integer, primary_key=True)
    name_masked = db.Column(db.String(20), nullable=False)  # 예: "P○○"
    age = db.Column(db.Integer, nullable=False)
    region = db.Column(db.String(40), nullable=False)       # 예: "비엔티안"
    job_note = db.Column(db.String(80), default="")          # 카드용 한 줄 소개
    intro = db.Column(db.Text, default="")                    # 상세페이지용 상세 소개
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    photos = db.relationship("FemalePhoto", backref="member",
                             order_by="FemalePhoto.sort_order",
                             cascade="all, delete-orphan")


class FemalePhoto(db.Model):
    __tablename__ = "female_photos"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("female_members.id"), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)


class Inquiry(db.Model):
    """상담신청 (선택 기능 대비 스키마만 확보)."""
    __tablename__ = "inquiries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

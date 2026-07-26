"""회원가입 — 유효성 검증 → bcrypt 해시 → DB 저장 → 관리자 메일 발송."""
import re
from datetime import date, datetime

import bcrypt
from flask import (Blueprint, current_app, redirect, render_template, request,
                   session, url_for)

from .. import limiter
from ..mailer import send_signup_mail
from ..models import User, db

bp = Blueprint("auth", __name__)

LOGIN_RE = re.compile(r"^[A-Za-z0-9]{4,16}$")
PHONE_RE = re.compile(r"^0\d{1,2}-?\d{3,4}-?\d{4}$")

EDUCATIONS = ["고등학교 졸업", "전문대 졸업", "대학교 졸업", "대학원 이상", "기타"]
INCOMES = ["2,000만원 미만", "2,000 ~ 3,000만원", "3,000 ~ 4,000만원",
           "4,000 ~ 5,000만원", "5,000 ~ 7,000만원", "7,000만원 이상"]


@bp.get("/login")
def login_form():
    if session.get("user_id"):
        return redirect(url_for("pages.members"))
    return render_template("login.html", error=None, login_id="")


@bp.post("/login")
@limiter.limit("10 per hour", methods=["POST"])
def login_submit():
    login_id = request.form.get("login_id", "").strip()
    password = request.form.get("password", "")
    user = User.query.filter_by(login_id=login_id).first()

    if not user or not bcrypt.checkpw(password.encode(), user.pw_hash.encode()):
        error = "아이디 또는 비밀번호가 올바르지 않습니다."
    elif user.status == "pending":
        error = "가입 승인 대기 중입니다. 담당자 확인 후 이용하실 수 있습니다."
    elif user.status == "blocked":
        error = "이용이 제한된 계정입니다. 고객센터로 문의해 주세요."
    else:
        session["user_id"] = user.id
        session["user_name"] = user.name
        return redirect(url_for("pages.members"))

    return render_template("login.html", error=error, login_id=login_id), 401


@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("pages.index"))


@bp.get("/signup")
def signup_form():
    return render_template("signup.html", form={}, errors={}, checked_status=[],
                           educations=EDUCATIONS, incomes=INCOMES)


@bp.get("/signup/done")
def signup_done():
    return render_template("signup_done.html")


@bp.post("/signup")
@limiter.limit("5 per hour", methods=["POST"])
def signup_submit():
    f = request.form
    errors = {}

    # 스팸 방지 honeypot — 사람 눈에 안 보이는 필드가 채워져 있으면 봇으로 간주
    if f.get("website"):
        current_app.logger.warning("honeypot 감지 — 요청 무시 (ip=%s)", request.remote_addr)
        return redirect(url_for("auth.signup_done"))

    login_id = f.get("login_id", "").strip()
    password = f.get("password", "")
    password2 = f.get("password2", "")
    name = f.get("name", "").strip()
    birth_raw = f.get("birth", "")
    phone = f.get("phone", "").strip()
    address = f.get("address", "").strip()
    education = f.get("education", "")
    job = f.get("job", "").strip()
    income = f.get("income_range", "")

    if not LOGIN_RE.match(login_id):
        errors["login_id"] = "아이디는 영문·숫자 4~16자로 입력해주세요."
    elif User.query.filter_by(login_id=login_id).first():
        errors["login_id"] = "이미 사용 중인 아이디입니다."
    if len(password) < 8:
        errors["password"] = "비밀번호는 8자 이상이어야 합니다."
    elif password != password2:
        errors["password2"] = "비밀번호가 일치하지 않습니다."
    if not name:
        errors["name"] = "이름을 입력해주세요."

    birth = None
    try:
        birth = datetime.strptime(birth_raw, "%Y-%m-%d").date()
        if not (1930 <= birth.year <= date.today().year - 19):
            errors["birth"] = "생년월일을 확인해주세요. (만 19세 이상)"
    except ValueError:
        errors["birth"] = "생년월일을 입력해주세요."

    if not PHONE_RE.match(phone):
        errors["phone"] = "연락처 형식을 확인해주세요. (예: 010-0000-0000)"
    if not address:
        errors["address"] = "주소를 입력해주세요."
    if education not in EDUCATIONS:
        errors["education"] = "최종학력을 선택해주세요."
    if not job:
        errors["job"] = "직업을 입력해주세요."
    if income not in INCOMES:
        errors["income_range"] = "연봉 구간을 선택해주세요."
    if not f.get("privacy_agree"):
        errors["privacy_agree"] = "개인정보 수집·이용 동의는 필수입니다."

    statuses = f.getlist("status")
    if errors:
        return render_template("signup.html", form=f, errors=errors,
                               checked_status=statuses,
                               educations=EDUCATIONS, incomes=INCOMES), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(
        login_id=login_id, pw_hash=pw_hash, name=name, birth=birth,
        phone=phone, address=address, education=education, job=job,
        income_range=income,
        is_single="미혼" in statuses,
        is_married="기혼" in statuses,
        is_remarriage="재혼" in statuses,
        has_children="자녀" in statuses,
    )
    db.session.add(user)
    db.session.commit()

    try:
        send_signup_mail(user)
    except Exception:
        # 메일 실패가 접수 자체를 막으면 안 됨 — DB에는 저장 완료
        current_app.logger.exception("가입 접수 메일 발송 실패 (user_id=%s)", user.id)

    return redirect(url_for("auth.signup_done"))

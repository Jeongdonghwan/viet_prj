"""가입 신청 접수 메일 발송.

- 비밀번호는 절대 메일 원문에 포함하지 않는다 (DB에 bcrypt 해시만 저장).
- SMTP 미설정(개발) 시 콘솔에 로그로 출력.
"""
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

from flask import current_app


def send_signup_mail(user):
    cfg = current_app.config
    checks = [label for flag, label in (
        (user.is_single, "미혼"),
        (user.is_married, "기혼 (혼인 중)"),
        (user.is_remarriage, "재혼 희망"),
        (user.has_children, "자녀 있음"),
    ) if flag]

    body = f"""[글로벌라오] 신규 회원가입 신청이 접수되었습니다.

아이디: {user.login_id}
이름: {user.name}
생년월일: {user.birth}
연락처: {user.phone}
주소: {user.address}
최종학력: {user.education}
직업: {user.job}
연봉구간: {user.income_range}
해당사항: {", ".join(checks) if checks else "없음"}
접수시각(UTC): {user.created_at}

관리자 승인 후 여성회원 열람 권한이 부여됩니다.
"""
    subject = f"[가입신청] {user.name} ({user.login_id})"

    if not cfg.get("SMTP_HOST"):
        current_app.logger.info("SMTP 미설정 — 메일 내용 콘솔 출력:\n%s", body)
        return

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = cfg["SMTP_USER"]
    msg["To"] = cfg["ADMIN_EMAIL"]
    msg["Date"] = formatdate(localtime=True)

    with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=15) as smtp:
        smtp.starttls()
        smtp.login(cfg["SMTP_USER"], cfg["SMTP_PASS"])
        smtp.send_message(msg)

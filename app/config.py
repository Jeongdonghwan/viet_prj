"""앱 설정 — 민감 값은 환경변수로 주입, 미설정 시 개발용 기본값 사용."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

    # DB: 운영(Cafe24)에서는 MariaDB URI를 환경변수로 지정
    #   예) mysql+pymysql://user:pass@localhost/glaos?charset=utf8mb4
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///" + os.path.join(BASE_DIR, "glaos_dev.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP (미설정 시 콘솔 로그로 대체)
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASS = os.environ.get("SMTP_PASS", "")
    # TODO(클라이언트 확인): 가입 신청 수신 이메일 — glaos2024@gmail.com 사용 여부
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "glaos2024@gmail.com")

    # 관리자 계정 — 운영 배포 시 반드시 환경변수로 교체할 것
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "glaos2024!")

    # 여성회원 사진 업로드
    UPLOAD_DIR = os.path.join(BASE_DIR, "app", "static", "uploads", "members")
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15MB


# 사이트 전역 정보 — 템플릿에 context_processor로 주입.
# 미확정 값은 TODO 주석 참고, 이 파일 한 곳만 수정하면 전체 반영됨.
SITE = {
    "brand_ko": "인터내셔널투어앤웨딩",
    "brand_en": "K-GLOBAL LAOS",                   # 라오스 파트너 법인 브랜드
    "company_kr": "(주)인터내셔널투어앤웨딩",        # 한국 법인 상호 (사업자등록증)
    "company_lao": "K GLOBAL LAO Sole Co., Ltd",  # 라오스 법인명 (간판 표기)
    "ceo": "이승훈",                                # 한국 법인 대표 (사업자등록증)
    "ceo_lao": "구본건",                            # 라오스 법인 대표 (인삿말 서명)
    "email": "glaos2024@gmail.com",
    "tel_kr": "1551-9924",
    "mobile_kr": "010-2608-9987",
    "tel_laos": "+856 20 9616 7176",
    "tel_vn": "+84 037 418 1199",
    "addr_kr": "전남광주통합특별시 북구 하서로 421 양산빌딩 5층",
    "addr_laos": "Hongkae Village, Xaisedtha District, Vientiane Capital, Laos",
    "biz_no": "704-88-03145",
    # TODO(클라이언트 확인): 한국 국제결혼중개업 등록번호 (등록 완료 후 기재)
    "broker_no": "",
    # TODO(클라이언트 확인): 카카오톡 채널/오픈채팅 URL — 현재는 QR 이미지만 보유
    "kakao_url": "#",
    "hours": "평일 09:00 – 18:00 (주말·공휴일 사전예약)",
}

# gunicorn 설정 — Cafe24 가상서버 (기존 서비스들과 공존: 포트 8000)
# 도메인 연결 전에는 0.0.0.0:8000 직접 노출, nginx 연결 후 127.0.0.1:8000 로 변경
bind = "0.0.0.0:8000"
workers = 2
timeout = 60
accesslog = "-"   # systemd journal 로 출력
errorlog = "-"

# gunicorn 설정 — Cafe24 가상서버용
bind = "127.0.0.1:8000"   # nginx 리버스 프록시 뒤에서 실행
workers = 2               # 가상서버 1~2코어 기준
timeout = 60
accesslog = "/var/log/glaos/access.log"
errorlog = "/var/log/glaos/error.log"

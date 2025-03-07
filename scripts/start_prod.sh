#!/bin/bash

# 환경 변수 로드
set -a
source .env
set +a

# 운영 모드로 실행
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
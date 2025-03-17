#!/bin/bash

# 환경 변수 로드
set -a
source .env
set +a

# 개발 모드로 실행 (poetry를 통해 uvicorn 실행)
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8008
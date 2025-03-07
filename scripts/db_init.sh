#!/bin/bash

# 환경 변수 로드
set -a
source .env
set +a

# Docker로 PostgreSQL 실행
docker compose up -d postgres

# 데이터베이스 마이그레이션 실행
poetry run alembic upgrade head
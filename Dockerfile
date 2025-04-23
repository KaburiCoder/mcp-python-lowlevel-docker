# --- 스테이지 1: 빌더 ---
# 의존성 설치 및 프로젝트 빌드를 위한 중간 단계
FROM python:3.13-slim AS builder

# uv 설치 (빌더 단계에서 필요하다고 가정)
# 참고: pip를 사용해 설치할 수도 있습니다: RUN pip install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 빌더 단계 내에 가상 환경 생성
RUN python -m venv /app/.venv
# 가상 환경의 bin 디렉토리를 PATH에 추가
ENV PATH="/app/.venv/bin:$PATH"

# uv 캐시 마운트를 사용하여 가상 환경에 의존성 설치
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-dev --no-editable

# 프로젝트 소스 코드 복사
COPY . /app

# 프로젝트 자체를 가상 환경에 설치
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev --no-editable

# --- 스테이지 2: 최종 런타임 이미지 ---
FROM python:3.13-slim

# 중요: 'app' 그룹과 'app' 사용자 생성
# -r: 시스템 사용자/그룹으로 생성 (서비스에 적합)
# --no-create-home: 홈 디렉토리 생성 안 함
# --shell /sbin/nologin: 보안상 로그인 쉘 비활성화
RUN groupadd -r app && useradd --no-log-init -r -g app --no-create-home --shell /sbin/nologin app

WORKDIR /app

# 애플리케이션 소스 코드 복사 (CMD에서 가상환경 외부 파일을 직접 실행할 경우 필요)
COPY --from=builder --chown=app:app /app /app

# 최종 이미지의 PATH에 가상 환경 bin 디렉토리 추가
ENV PATH="/app/.venv/bin:$PATH"

# 권한이 없는 'app' 사용자로 전환
USER app

# 웹 서버인 경우 포트 노출 (예: FastAPI, Flask)
# EXPOSE 8000

# 애플리케이션 실행 명령
CMD ["python", "main.py"]
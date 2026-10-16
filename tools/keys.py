"""API 키 읽기: 환경변수 우선, 없으면 저장소 루트 .env. 키를 코드·문서·로그에 남기지 않는다."""
import os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def get(name):
    v = os.environ.get(name)
    if v:
        return v.strip()
    env = ROOT / '.env'
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith(name + '='):
                return line.split('=', 1)[1].strip()
    raise SystemExit(f'{name} 가 없습니다 (환경변수 또는 .env)')

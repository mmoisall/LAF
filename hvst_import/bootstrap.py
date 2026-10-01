"""LAFhvst `core` 위치를 탐색해 sys.path 에 등록한다.

이관 도구는 LAFhvst 의 `core`(models/database/site_url)를 그대로 재사용한다.
따라서 실제 LAFhvst 소스 경로를 찾아 import 경로에 넣어야 하며, 그래야 대상
`lafhvst.db` 도 올바르게 지정된다.

탐색 우선순위:
    1. `--lafhvst <경로>` 인자
    2. `LAFHVST_HOME` 환경변수
    3. 자동탐지: 형제 폴더 `../LAFhvst`, 현재 작업 폴더, 저장소 루트
"""

import os
import sys

_CORE_MARKER = os.path.join("core", "database.py")


def _is_lafhvst_home(path):
    if not path:
        return False
    return os.path.isfile(os.path.join(path, _CORE_MARKER))


def _explicit_from_argv(argv):
    for index, token in enumerate(argv):
        if token == "--lafhvst" and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith("--lafhvst="):
            return token.split("=", 1)[1]
    return None


def resolve_lafhvst_home(explicit=None):
    """LAFhvst 소스 경로를 반환한다. 찾지 못하면 None."""
    candidates = []
    if explicit:
        candidates.append(explicit)
    env = os.environ.get("LAFHVST_HOME")
    if env:
        candidates.append(env)
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    candidates.append(os.path.join(os.path.dirname(repo_root), "LAFhvst"))
    candidates.append(os.getcwd())
    candidates.append(repo_root)
    for candidate in candidates:
        candidate = os.path.abspath(candidate)
        if _is_lafhvst_home(candidate):
            return candidate
    return None


def ensure_core(explicit=None):
    """`core` import 가 가능하도록 sys.path 를 설정하고 경로를 반환한다."""
    home = resolve_lafhvst_home(explicit)
    if not home:
        sys.stderr.write(
            "LAFhvst 소스 경로를 찾지 못했습니다.\n"
            "  --lafhvst <경로> 옵션 또는 LAFHVST_HOME 환경변수로 지정하세요.\n"
            "  예: set LAFHVST_HOME=C:\\path\\to\\LAFhvst\n"
        )
        raise SystemExit(2)
    if home not in sys.path:
        sys.path.insert(0, home)
    return home


def ensure_core_from_argv(argv):
    return ensure_core(_explicit_from_argv(list(argv or [])))

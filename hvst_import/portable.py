"""구형 HVST → LAFhvst 이관 도구의 포터블(EXE) 진입점.

배포 형태: `hvst_import.exe` 옆에 두 폴더를 나란히 둔다.

    <아무 폴더>/
      hvst_import.exe
      구형/            # 구형 HVST 폴더 (hvst.db 또는 data/hvst.db 포함)
      현재/            # 현재 LAFhvst 폴더 (lafhvst.db 포함)

탐지 우선순위(각 경로별): 명령행 인자 > 환경변수 > exe 옆 자동탐지.
자동탐지 규칙:
  - 구형 폴더: `hvst.db` 또는 `data/hvst.db` 가 있는 폴더
  - 현재 폴더: `lafhvst.db` 가 있는 폴더(없으면 `core/database.py` 가 있는 폴더)

core(LAFhvst models/database/site_url)는 현재 폴더의 `core/`(소스)를 우선 쓰고,
없으면 exe 에 동봉된 core 로 폴백한다. 어느 경우든 DB 경로는 현재 폴더 기준이 된다.
"""

import os
import sys

FROZEN = bool(getattr(sys, "frozen", False))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def base_dir() -> str:
    """탐지 기준 폴더: 패키징 실행이면 exe 가 있는 폴더, 소스 실행이면 저장소 루트."""
    if FROZEN:
        return os.path.dirname(os.path.abspath(sys.executable))
    return REPO_ROOT


def _argv_value(argv, flag):
    for index, token in enumerate(argv):
        if token == flag and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(flag + "="):
            return token.split("=", 1)[1]
    return None


def _subdirs(root):
    try:
        names = sorted(os.listdir(root))
    except OSError:
        return []
    return [os.path.join(root, name) for name in names if os.path.isdir(os.path.join(root, name))]


def _has_core(folder) -> bool:
    return bool(folder) and os.path.isfile(os.path.join(folder, "core", "database.py"))


def _legacy_db(folder):
    for rel in ("hvst.db", os.path.join("data", "hvst.db")):
        path = os.path.join(folder, rel)
        if os.path.isfile(path):
            return path
    return None


def _legacy_settings(folder, db_path):
    candidates = []
    if db_path:
        candidates.append(os.path.join(os.path.dirname(db_path), "hvst_setting.json"))
    candidates.append(os.path.join(folder, "hvst_setting.json"))
    candidates.append(os.path.join(folder, "data", "hvst_setting.json"))
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _current_score(folder):
    """현재 폴더 후보 점수(높을수록 우선): lafhvst.db > core/."""
    has_db = os.path.isfile(os.path.join(folder, "lafhvst.db"))
    has_core = _has_core(folder)
    if not has_db and not has_core:
        return -1
    return (2 if has_db else 0) + (1 if has_core else 0)


def _find_current(candidates, exclude):
    best, best_score = None, -1
    for folder in candidates:
        if os.path.abspath(folder) in exclude:
            continue
        score = _current_score(folder)
        if score > best_score:
            best, best_score = folder, score
    return best


def _find_legacy(candidates, exclude):
    for folder in candidates:
        if os.path.abspath(folder) in exclude:
            continue
        if _legacy_db(folder):
            return folder
    return None


def resolve_paths(argv):
    """(현재 폴더, 구형 db 경로, 구형 settings 경로)를 결정한다."""
    base = base_dir()
    subdirs = _subdirs(base)

    current = _argv_value(argv, "--lafhvst") or os.environ.get("LAFHVST_HOME") or ""
    if current and not os.path.isdir(current):
        current = ""
    if not current:
        current = _find_current(subdirs, set()) or ""

    legacy_db = _argv_value(argv, "--db") or os.environ.get("HVST_DB") or ""
    legacy_settings = _argv_value(argv, "--settings") or os.environ.get("HVST_SETTINGS") or ""

    exclude = {os.path.abspath(current)} if current else set()
    if not legacy_db:
        legacy = _find_legacy(subdirs, exclude)
        if legacy:
            legacy_db = _legacy_db(legacy) or ""
            if not legacy_settings:
                legacy_settings = _legacy_settings(legacy, legacy_db) or ""

    return current, legacy_db, legacy_settings


def _install_core(current):
    """core import 경로를 준비한다. 반환: 이관 대상 데이터 루트."""
    from hvst_import import bootstrap

    target = current or base_dir()

    if not FROZEN:
        # 소스 실행: 기존 자동탐지(형제 ../LAFhvst 등)를 그대로 사용한다.
        bootstrap.ensure_core_from_argv(sys.argv)
        import core.utils as core_utils

        core_utils.project_root = lambda: target
        return target

    # 패키징 실행: 현재 폴더의 core(소스) 우선, 없으면 동봉된 core 로 폴백.
    meipass = getattr(sys, "_MEIPASS", "")
    if meipass and meipass not in sys.path:
        sys.path.insert(0, meipass)
    if current and _has_core(current):
        while current in sys.path:
            sys.path.remove(current)
        sys.path.insert(0, current)  # 동봉 core 보다 우선하도록 맨 앞에 둔다.

    import core.utils as core_utils

    core_utils.project_root = lambda: target
    # 동봉 core 를 쓰는 경우 bootstrap 의 디스크 탐색은 불필요/실패하므로 우회한다.
    bootstrap.ensure_core = lambda explicit=None: target
    bootstrap.ensure_core_from_argv = lambda argv=None: target
    return target


def _report_failure(show_dialog=True):
    """실패 시 exe 옆에 로그를 남기고(필요하면) 메시지 박스를 띄운다."""
    import traceback

    text = traceback.format_exc()
    try:
        log_path = os.path.join(base_dir(), "hvst_import_error.log")
        with open(log_path, "w", encoding="utf-8") as handle:
            handle.write(text)
    except OSError:
        log_path = "(로그 저장 실패)"
    try:
        if sys.stderr is not None:
            sys.stderr.write(text)
    except Exception:
        pass
    if not show_dialog:
        return
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            None,
            "이관 도구 실행 중 오류가 발생했습니다.\n\n%s\n\n자세한 내용: %s"
            % (text.strip().splitlines()[-1], log_path),
            "HVST 이관 도구",
            0x10,
        )
    except Exception:
        pass


class _NullStream:
    """창 없는(windowed) 실행에서 stdout/stderr 가 None 일 때 쓰는 더미 스트림."""

    encoding = "utf-8"
    errors = "replace"

    def write(self, text):
        return len(text) if text else 0

    def flush(self):
        pass

    def isatty(self):
        return False

    def writable(self):
        return True

    def readable(self):
        return False

    def seekable(self):
        return False

    def fileno(self):
        raise OSError("no fileno")


def _ensure_stdio():
    """windowed exe 는 콘솔이 없으면 sys.stdout/stderr 가 None 이 된다.

    uvicorn 등이 ``sys.stderr.isatty()`` 를 호출하므로 더미 스트림으로 채운다.
    """
    if sys.stdout is None:
        sys.stdout = _NullStream()
    if sys.stderr is None:
        sys.stderr = _NullStream()


def _force_utf8_stdio():
    """CLI/서버 출력이 콘솔 코드페이지(cp949/cp1252)에 막히지 않도록 UTF-8 로 맞춘다."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _run(argv):
    current, legacy_db, legacy_settings = resolve_paths(argv)

    if current:
        os.environ["LAFHVST_HOME"] = current
    if legacy_db:
        os.environ["HVST_DB"] = legacy_db
    if legacy_settings:
        os.environ["HVST_SETTINGS"] = legacy_settings

    _ensure_stdio()
    _force_utf8_stdio()
    _install_core(current)

    if "--cli" in argv:
        argv.remove("--cli")
        from hvst_import.importer import run_cli

        return run_cli(argv[1:])

    from hvst_import import app

    app.main()
    return 0


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    headless = "--cli" in argv or "--serve" in argv or os.environ.get("LAF_NO_GUI") == "1"
    try:
        return _run(argv)
    except SystemExit:
        raise
    except BaseException:
        _report_failure(show_dialog=not headless)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

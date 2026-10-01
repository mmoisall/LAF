"""구형 HVST → LAFhvst 이관 CLI 진입점.

사용 예:
    python import_hvst.py --lafhvst "C:\\path\\to\\LAFhvst" --db "C:\\path\\to\\hvst.db" --dry-run
    python import_hvst.py --db "C:\\path\\to\\hvst.db" --apply
    set LAFHVST_HOME=C:\\path\\to\\LAFhvst   # 환경변수로 지정 가능
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hvst_import import bootstrap  # noqa: E402

bootstrap.ensure_core_from_argv(sys.argv)

from hvst_import.importer import run_cli  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(run_cli())

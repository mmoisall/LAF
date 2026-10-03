# -*- mode: python ; coding: utf-8 -*-
"""구형 HVST → LAFhvst 이관 도구 — 포터블 onefile EXE 빌드 스펙.

exe 하나로 동작하도록 LAFhvst 의 `core` 를 동봉한다(런타임에 현재 폴더의 core 가
있으면 그것을 우선 사용). UI 정적 파일(index.html/ui.css/ui.js)도 함께 넣는다.

LAFhvst 경로는 환경변수 `HVST_IMPORT_LAFHVST` 로 지정하며, 없으면 LAF 저장소의
형제 폴더 `../LAFhvst` 를 사용한다.
"""

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = os.path.dirname(os.path.abspath(SPECPATH))
LAFHVST_ROOT = os.environ.get("HVST_IMPORT_LAFHVST") or os.path.join(
    os.path.dirname(ROOT), "LAFhvst"
)
CORE_DIR = os.path.join(LAFHVST_ROOT, "core")
if not os.path.isfile(os.path.join(CORE_DIR, "database.py")):
    raise SystemExit(
        "LAFhvst core 를 찾지 못했습니다: %s\n"
        "HVST_IMPORT_LAFHVST 환경변수로 LAFhvst 경로를 지정하세요." % CORE_DIR
    )


def _core_sources():
    """동봉할 core 소스(.py)만 모은다 (__pycache__/.pyc 제외)."""
    out = []
    for dirpath, dirnames, filenames in os.walk(CORE_DIR):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            src = os.path.join(dirpath, name)
            rel = os.path.relpath(src, CORE_DIR)
            out.append((src, os.path.join("core", os.path.dirname(rel))))
    return out


datas = [
    (os.path.join(ROOT, "hvst_import", "index.html"), "hvst_import"),
    (os.path.join(ROOT, "hvst_import", "ui.css"), "hvst_import"),
    (os.path.join(ROOT, "hvst_import", "ui.js"), "hvst_import"),
]
datas += _core_sources()

binaries = []
hiddenimports = []
for package in ("webview", "pythonnet", "clr_loader"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

hiddenimports += collect_submodules("uvicorn")
# core 는 PYZ 에서 제외했으므로(아래 excludes) 그 의존성을 직접 지정한다.
# core/models·database → sqlalchemy, core/metadata → yaml.
hiddenimports += ["sqlalchemy", "sqlalchemy.dialects.sqlite", "yaml"]
hiddenimports += [
    "clr",
    "webview.platforms.edgechromium",
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
]

ICON = os.path.join(LAFHVST_ROOT, "assets", "LAFhvst.ico")

analysis = Analysis(
    [os.path.join(ROOT, "hvst_import", "portable.py")],
    pathex=[ROOT, LAFHVST_ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # core 는 PYZ 에 넣지 않고 데이터로 동봉한다 → 런타임에 현재 폴더의 core 가
    # 있으면 그쪽이 sys.path 우선순위로 선택된다(스키마 불일치 방지).
    excludes=["core"],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="hvst_import",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    icon=ICON if os.path.isfile(ICON) else None,
)

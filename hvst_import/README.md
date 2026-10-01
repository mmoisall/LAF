# LAF — 구형 HVST → LAFhvst 이관 도구

구형 HVST의 `hvst.db`(folder/source 단일 테이블 트리)를 [LAFhvst](https://github.com/mmoisall/LAFhvst)의
`lafhvst.db`(folders/sources)로 이관하는 도구입니다. CLI와 로컬 웹 UI를 제공합니다.

- 기존 자료는 보존하고 **중복은 건너뜁니다** (폴더=전체 경로, 소스=(정규화 site, key) [없으면 url]).
- 자격증명(cookies/refresh-token/api-key/password 등)은 **기본 제외**됩니다.
- 폐기 필드(`loc_alt`/`loc_cmb`/`cyc_min`/`cyc_max`/`ignore_level` 등)는 이관하지 않습니다.

## LAFhvst core 재사용

이 도구는 LAFhvst의 `core`(models/database/site_url)를 그대로 재사용합니다. 즉 **LAFhvst 소스가
필요**하며, 실행 시 대상 LAFhvst 경로를 아래 우선순위로 찾습니다.

1. `--lafhvst <경로>` 옵션
2. `LAFHVST_HOME` 환경변수
3. 자동탐지: 형제 폴더 `../LAFhvst`, 현재 작업 폴더, 이 저장소 루트

찾은 경로의 `lafhvst.db` 가 이관 대상이 됩니다. (LAF와 LAFhvst를 형제 폴더로 두면 자동으로 잡힙니다.)

## 요구 사항

- Python 3.11+
- 의존성 설치: `pip install -r hvst_import/requirements.txt`
- LAFhvst 소스 (별도 저장소)

## CLI

```bash
# 미리보기 (기본)
python import_hvst.py --lafhvst "C:\path\to\LAFhvst" --db "C:\path\to\hvst.db" --dry-run

# 실제 이관
python import_hvst.py --lafhvst "C:\path\to\LAFhvst" --db "C:\path\to\hvst.db" --apply

# 환경변수로 LAFhvst 경로 지정
set LAFHVST_HOME=C:\path\to\LAFhvst
python import_hvst.py --db "C:\path\to\hvst.db"
```

주요 옵션:

| 옵션 | 설명 |
| --- | --- |
| `--lafhvst` | LAFhvst 소스 경로 (또는 `LAFHVST_HOME`) |
| `--db` | 구형 `hvst.db` 경로 (또는 `HVST_DB`) |
| `--settings` | 구형 `hvst_setting.json` 경로 (또는 `HVST_SETTINGS`) |
| `--apply` | 실제 이관 (미지정 시 미리보기) |
| `--dry-run` | 미리보기만 |
| `--include-secrets` | 자격증명 포함 (주의) |
| `--exclude-columns` | 제외할 열 (쉼표 구분) |
| `--exclude-rows` | 제외할 행 old_id (`folder:1,source:2`) |
| `--json` | JSON 출력 |

## 웹 UI

```bash
python hvst_import/app.py --lafhvst "C:\path\to\LAFhvst"
```

창에서 구형 DB 경로를 입력하고 점검 → 미리보기 → 이관을 진행합니다. `--serve`(또는 `LAF_NO_GUI=1`)로
창 없이 서버만 실행할 수 있습니다(기본 포트 17374).

## 관련 저장소

- LAFhvst (본체): https://github.com/mmoisall/LAFhvst

## 라이선스

[MIT](../LICENSE) © mmoisall

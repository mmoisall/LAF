# LAFhvst old
LAF를 위한 다운로드 관리 프로그램
내가 쓰려고 만듬

설명
1. 파이썬, gallery-dl 설치 필요

2. "C:\Users\사용자명\AppData\Roaming\gallery-dl" 에 "config.json" 복사

3. json 세팅 (hvst_setting.json)
    - config_default : ??? 부분들 수정하여 로그인 정보 등록
    - save_path : 다운로드 위치
    - comb_path : 폴더합본 생성 위치
    - alt_path  : 폴더 추가 저장 위치
    - config_default : 다운로드 실행시 사이트에 해당하는부분을 갤디엘config에 적용.
    db의 내용이 우선시 됨.
    - 시간 보정(h) : 실행할때 기준 시간에 이 값을 빼서 함 (추천:3~24)










!참고사항!

창을 닫아도 작업표시줄 아이콘 트레이에 남아서 백그라운드 실행됨.
완전히 종료하려면 작은 아이콘을 우클.

appdata\log\hvst.log 에 로그가 많이 쌓이면 용량이 커지니 지워야할수있음.
log_level을 DEBUG 사용시 기록이 많고 CRITICAL 로 갈수록 적음.

현재 지원 사이트 : 'twitter', 'pixiv', 'tumblr', 'deviantart', 'bluesky', 'baraag.net', 'instagram', 'naver', 'naverwebtoon', 'e621'

console버전 사용하면 로그콘솔창 나옴. 기본 버전도 log에서 동일하게 확인가능



웹사이트 다운로드에 https://github.com/mikf/gallery-dl 를 사용함. 





스파게티 코딩입니다.

커뮤니티
- https://discord.gg/PW37BpRR6w
- https://gall.dcinside.com/mini/board/lists?id=furrylost2022



---

## 구형 HVST 이관 도구 (`hvst_import/`)

이 저장소에는 구형 HVST의 `hvst.db` 를 새 [LAFhvst](https://github.com/mmoisall/LAFhvst)의
`lafhvst.db` 로 이관하는 도구가 포함되어 있습니다. 자격증명(cookies/토큰/비밀번호)은 기본 제외되고,
중복 항목은 건너뜁니다.

- 폴더: [`hvst_import/`](hvst_import/) — CLI + 로컬 웹 UI
- **포터블 EXE 다운로드**: [Releases](https://github.com/mmoisall/LAF/releases/tag/hvst-import-v0.1.0) 의 `hvst_import.exe`
  (exe 옆에 구형 폴더와 현재 LAFhvst 폴더를 나란히 두고 실행)
- 자세한 사용법: [hvst_import/README.md](hvst_import/README.md)

```bash
pip install -r hvst_import/requirements.txt

# 미리보기
python import_hvst.py --lafhvst "C:\path\to\LAFhvst" --db "C:\path\to\hvst.db" --dry-run

# 실제 이관
python import_hvst.py --lafhvst "C:\path\to\LAFhvst" --db "C:\path\to\hvst.db" --apply
```

> 이관 도구는 LAFhvst 소스(`core`)를 재사용합니다. `--lafhvst` 옵션 또는 `LAFHVST_HOME`
> 환경변수로 LAFhvst 경로를 지정하거나, 두 폴더를 형제로 두면 자동 탐지됩니다.



# The Sims 2: Castaway (PSP) 한국어 패치

PSP용 **The Sims 2: Castaway (USA / ULUS-10296)** 한국어 패치 프로젝트입니다.

현재 공개 기준판은 **FINAL_20261017_R5 / v0.1.0-beta** 입니다.

> **Beta:** 파일 수준의 빌드·패치 재현 검사는 통과했지만, 모든 플레이 화면의 번역 적용 상태·글자 잘림·위치·문구 자연스러움까지 완전히 검증된 완성판은 아닙니다.

## 대상 원본

- Platform: PSP
- Region / Game ID: USA / ULUS-10296
- Original ISO SHA-256: `fd46c3b338fc6ee1a15d2c29aadd300425b263ddc14e859a4ac80d3396a2e21c`

원본 ISO, 수정 ISO, 상용 폰트, PPSSPP, 저장 데이터는 저장소와 Release에 포함하지 않습니다.

## FINAL_20261017_R5

- 추출 텍스트: 16,550행
- 초벌 번역: 13,430행
- 저장/불러오기 보충 문구: 52개
- EA 소개 영상 문장: 1개
- 조사한 텍스처: 3,374개
- 비ASCII 폰트 문자: 1,224개
- 상태: `DRAFT`
- `all_assets_translated=false`

`text_master.tsv` 기준으로 남은 항목은 빈칸, 키보드/폰트 문자, 기호/제어 태그, 기술 식별자입니다. 현재 추출표에서 번역 대기 문장은 없지만, 아직 발견하지 못한 에셋이나 실제 플레이에서 드러나는 표시 문제는 남아 있을 수 있습니다.

### R5 주요 수정

- SHPM type `0x46`을 PSP DXT3/BC2 explicit alpha로 올바르게 처리
- 메인 로고 알파 줄무늬 문제 수정
- 한글 제목 폰트 signed Y bearing / 기준선 보정
- `main10`, `main11`, `main13`, `title`, `title_glow` raster 크기 조정
- 일부 튜토리얼·채집·도움말 문구 길이 축약
- 원래 영문 폰트 픽셀과 기존 글자 레코드 보존

## 패치 적용

1. 합법적으로 보유한 ULUS-10296 USA 원본 ISO를 준비합니다.
2. 위 원본 SHA-256과 일치하는지 확인합니다.
3. Releases에서 `CASTAWAY_FINAL_20261017_R5.patch.zip`을 받습니다.
4. 패치 ZIP의 안내/도구로 원본 ISO에 패치를 적용합니다.
5. 기대 결과:
   - Size: `1,163,851,776 bytes`
   - SHA-256: `03b8aa99ddc753e9324463e556b7055bb364a72a5a6152e514a88cdf267bebb4`

## 개발 / 재빌드

주요 기능은 `src/castaway/` 아래에 모듈화되어 있습니다.

- ARC / QuickDat
- dataset / index
- font / font packing
- texture
- ISO patch / delta
- LOCH/LOCL locale
- PMF packet-slot/timestamp-preserving tooling

재빌드:

```powershell
.\run.ps1 -Mode Build -BuildId NEW_UNIQUE_ID -VerifyPatch
```

필요 환경:

- Python 3.9+
- Pillow 11.3.0
- FFmpeg (`libx264`, `drawtext`)
- 사용자가 직접 준비한 ULUS-10296 원본 ISO
- 로컬 Malgun Gothic 폰트

패치 적용 자체는 Python 표준 라이브러리만 필요하도록 구성되어 있습니다.

## 번역 데이터 주의

`translation/text_master.tsv`가 번역 정본입니다.

과거 batch/glossary를 정본 위에 무작정 재적용하지 마세요. UTF-8 BOM/CRLF, `source_sha256`, 변수 및 제어 태그 순서를 보존해야 합니다.

## 검증 상태

R5에서 확인된 것은 **파일 수준 검사**입니다.

- 전체 빌드
- 컨테이너 재구성
- 원본 ISO에서 패치 적용 후 결과 재현
- 결과 ISO SHA-256 일치
- DXT3 alpha 독립 검사
- 한글 높이 및 title/title_glow 치수 검사

모든 게임 화면의 정상 표시가 확인된 상태는 아닙니다.

## 인수인계

프로젝트를 이어서 작업할 경우 최신 `FINAL_HANDOFF.md`, `HANDOFF_NEXT.md`, `PROJECT_STATE.md`를 우선 읽으세요. 이전 STEP028/R2/R3/R4 기록은 역사 기록입니다.

## 저작권

이 프로젝트는 비공식 팬 번역 프로젝트입니다. 원본 게임 저작권은 각 권리자에게 있습니다. 사용자는 합법적으로 보유한 원본 게임에서 패치를 적용해야 합니다. 원본 게임 ISO는 제공하지 않습니다.
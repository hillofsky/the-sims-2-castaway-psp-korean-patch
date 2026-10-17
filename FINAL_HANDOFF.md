# 화면 표시 수정판 R5

2026-10-17T16:50:57.203439+09:00

사용자가 제공한 로고 줄무늬, 글자 잘림, 제목 위치 문제를 대상으로 수정했습니다.

- 로고: 원본 DXT3 투명도를 DXT5로 잘못 기록한 오류 수정. 디자인·원본 ISO는 그대로입니다.
- 한글: 제목의 음수 세로 기준선 복원, 제목/빛효과의 글자 크기·폭·기준선 일치.
- 새 한글 크기: 본문13→11, 본문11→10, 본문10→9픽셀. 제목과 빛효과는11픽셀로 통일. 원래 영문 글자와 원본 폰트 픽셀은 보존했습니다.
- 튜토리얼, 야자잎 채집 버튼, 도움말 닫기 문구를 짧게 다듬었습니다.

본문13,430개, 저장 안내52개, 영상 문구1개 번역을 유지합니다. 글꼴은1,224개 비ASCII 문자를 모두 포함합니다.

## 결과

ISO: build/CASTAWAY_FINAL_20261017_R5_KO_EXPERIMENTAL.iso
SHA256: 03b8aa99ddc753e9324463e556b7055bb364a72a5a6152e514a88cdf267bebb4

패치: build/CASTAWAY_FINAL_20261017_R5_EXPERIMENTAL.patch.zip
코드·정본·기록: CASTAWAY_FINAL_20261017_R5_SOURCE_HANDOFF.zip

빌드와 원본에서의 패치 재현이 성공했습니다. 독립 DXT3 디코더에서 로고의 투명/불투명 오류가 각각0개이며, 제목/빛효과의 한글 치수가 일치합니다. 이는 파일 수준 검사이며 게임 실행 결과가 아닙니다.

게임은 실행하지 않았습니다. 실제 화면에서 글자·버튼·제목 위치가 정상인지 사용자가 다시 확인해야 합니다. 폰트 크기 조정에 따라 이전 판보다 한글이 작게 보일 수 있습니다.

## 이어서 작업

정본 translation/text_master.tsv. 수정 내역 logs/FIX_084/fix_summary.json 및 wording_fit.json. 검사 scripts/check_render_fixes.py --build-id 새빌드ID. 원본 ISO, 로컬 한글 폰트, Python3.9+, Pillow11.3.0, FFmpeg(libx264/drawtext)가 필요합니다.

빌드: .\run.ps1 -Mode Build -BuildId 새고유ID -VerifyPatch

R3와 중간R4 대신 이 R5를 사용하세요. R4는 잘못된 로고 형식이 남은 중간 결과로 전달하지 않았습니다. 런타임 검증은 사용자 소유입니다. GitHub에는 업로드하지 않았습니다.

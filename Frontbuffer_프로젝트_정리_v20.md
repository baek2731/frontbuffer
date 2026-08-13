# Frontbuffer 프로젝트 정리 v20
> 작성일: 2026-07-28

---

## 1. 현재 상태 요약

### 발행 현황
- `_posts/` 발행 완료: **16편** (오늘 portable-gaming_COMPARISON + EXPLAINER 추가)
- `final/` 발행 대기: **17편** (001~015 스포크 + H001~H002 HUB)
- 애드센스 목표: 20편 → 현재 16편 (4편 부족, 내일부터 자동 발행)

### 발행된 글 목록 (_posts/)
| 날짜 | 클러스터 | 타입 | URL |
|------|---------|------|-----|
| 07-14 | Steam Machine | GUIDE | /gaming/how-to-troubleshoot-steam-machine-overheating-and-red-light-issues/ |
| 07-15 | Steam Machine | COMPARISON | /gaming/steam-machine-led-error-codes-what-each-warning-light-actually-means/ |
| 07-16 | Samsung Health | GUIDE | /tech/how-to-backup-samsung-health-data-before-account-deletion/ |
| 07-17 | Samsung Health | COMPARISON | /tech/samsung-health-vs-google-health-connect-feature-comparison/ |
| 07-18 | Chrome MV2 | GUIDE | /tech/how-to-check-if-chrome-extensions-use-manifest-v2/ |
| 07-19 | Chrome MV2 | LISTICLE | /tech/best-manifest-v3-alternatives-for-older-chrome-extensions/ |
| 07-20 | Chrome MV2 | EXPLAINER | /tech/what-is-chrome-manifest-v3-and-why-extensions-break/ |
| 07-20 | Chrome MV2 | HUB | /tech/chrome-manifest-v2-deprecation-complete-guide/ |
| 07-21 | Android Ecosystem | COMPARISON | /tech/android-ecosystem-comparison/ |
| 07-21 | Android Ecosystem | EXPLAINER | /tech/android-ecosystem_explainer/ |
| 07-22 | Android Ecosystem | GUIDE | /tech/android-ecosystem_guide/ |
| 07-23 | Fallout Series | COMPARISON | /gaming/fallout-series_comparison/ |
| 07-24 | Fallout Series | EXPLAINER | /gaming/fallout-series_explainer/ |
| 07-26 | Fallout Series | GUIDE | /gaming/fallout-series_guide/ |
| 07-27 | Portable Gaming | COMPARISON | /gaming/ayaneo-handhelds-vs-steam-deck-performance-portability-comparison/ |
| 07-28 | Portable Gaming | EXPLAINER | (오늘 발행) |

### final/ 발행 대기 (17편)
```
001_2026-W29_portable-gaming_EXPLAINER.md     ← 오늘 발행됨 (확인 필요)
002_2026-W29_portable-gaming_GUIDE.md
003_2026-W30_01-galaxy-fold_COMPARISON.md
004_2026-W30_01-galaxy-fold_EXPLAINER.md
005_2026-W30_01-galaxy-fold_GUIDE.md
006_2026-W30_samsung-galaxy-z-foldflip-series_COMPARISON.md
007_2026-W30_samsung-galaxy-z-foldflip-series_EXPLAINER.md
008_2026-W30_samsung-galaxy-z-foldflip-series_GUIDE.md
009_2026-W30_06-android-auto_COMPARISON.md
010_2026-W30_06-android-auto_GUIDE.md
011_2026-W30_google-android-ecosystem_COMPARISON.md
012_2026-W30_google-android-ecosystem_EXPLAINER.md
013_2026-W30_google-android-ecosystem_GUIDE.md
014_2026-W30_gaming-media-formats_COMPARISON.md
015_2026-W30_gaming-media-formats_GUIDE.md
H001_2026-W30_samsung-health-data-ecosystem_HUB.md   ← hub_ready True → 최상위 발행
H002_2026-W30_steam-machine-hardware-management_HUB.md ← hub_ready True → 최상위 발행
```

---

## 2. 오늘 완료한 작업 (2026-07-28)

### W30 Step 2~3 실행 및 버그 수정

#### ① folder 자동 매핑 추가 (research_gemini.py)
- **문제**: Gemini가 folder 값을 비워서 dedup_by_folder() 미작동
- **해결**: trends_dir 하위 폴더명과 cluster_name 퍼지 매칭으로 자동 채움

#### ② file_id 전달 버그 수정 (step3_write.yml)
- **문제**: gemini_review_api.py에 --file-id 미전달로 review_prompt 파일 못 찾음
- **해결**: FILE_ID 변수 추출 후 gemini_api.py, gemini_review_api.py에 전달

#### ③ cmd_review _ct_tag 덮어쓰기 버그 수정 (write.py)
- **문제**: cmd_review에서 _ct_tag가 빈 문자열로 덮어써져 file_id 불일치
- **해결**: 해당 줄 제거

#### ④ git pull rebase 에러 처리 (step3_write.yml)
- **문제**: unstaged 변경사항으로 git pull --rebase 실패 (exit 128)
- **해결**: git stash || true, git pull --rebase || true 처리

#### ⑤ Android Ecosystem GUIDE 무한루프 수정
- **문제**: W29/W30 두 개가 candidate로 공존해서 Step 3 무한루프
- **해결**: 두 항목 모두 writing으로 수동 마킹

#### ⑥ W30 candidate folder 수동 패치
- **문제**: Step 2 실행 시 folder 값 비어있던 7개 candidate
- **해결**: patch_w30.py로 folder 수동 매핑

#### ⑦ publish_one.py 신버전 파일명 파싱 버그 수정
- **문제**: 001_2026-W30_... 형식에서 slug 파싱 실패
- **해결**: 정규식으로 신버전/구버전 분기 파싱

#### ⑧ Step 2→3 자동 연쇄 추가 (step2_plan.yml)
- **해결**: github-script dispatch로 step3_write.yml 트리거

### final/ 구조 정비

#### ① 넘버링 재정립 (reorder_final.py)
- 허브 완성도 기준 클러스터별 순서 재배치
- 001~015 스포크, H001~H002 HUB

#### ② HUB H prefix 도입
- HUB 파일명에 H prefix (H001, H002...) 부여
- publish_one.py 정렬 시 H prefix 인식

#### ③ publish_order 연속 넘버링 (research_gemini.py)
- 기존: 매 Step 2마다 1부터 시작
- 변경: final/ 현재 최대값 + 1부터 시작 (무한 증가)
- HUB는 H001, H002... 별도 넘버링

#### ④ hub_ready() 전체 스포크 완료 방식으로 변경 (publish_one.py)
- 기존: 스포크 2개 이상이면 발행
- 변경: hub_clusters.spoke_urls 모두 http면 발행
- hub_ready True면 발행 순서 최상위로

#### ⑤ Samsung Health, Steam Machine spoke_urls 수동 패치
- hub_clusters.spoke_urls가 /drafts/ 상태였던 것을 실제 URL로 패치
- 두 허브 모두 hub_ready() True 확인

---

## 3. 파이프라인 전체 흐름 (정비 후)

```
Step 1 (월 UTC 02:00, 자동 OR final/ 7편 이하 시 Step 4에서 자동 트리거)
  research.py → RSS 수집 → Discord "CSV 올려주세요"
  → research_data/trends/{week_tag}/ 폴더 생성

Step 2 (CSV 업로드 후 수동 트리거)
  research_gemini.py
    → folder 자동 매핑 (trends_dir 퍼지 매칭)
    → 중복 클러스터 자동 필터 (dedup_by_folder)
    → Grade/트렌드/타입 기준 정렬
    → publish_order 부여 (final/ 최대값+1부터 연속)
    → HUB는 H001, H002... 별도 넘버링
  pipeline.py → content_pipeline.json 저장
  → Step 3 자동 트리거 (github-script dispatch)

Step 3 (Step 2 완료 후 자동)
  write.py next → file_id 반환
  write.py prep → write_prompt_{file_id}.txt
  gemini_api.py --file-id → 초안 생성
  write.py review → review_prompt_{file_id}.txt
  gemini_review_api.py --file-id → final/{file_id}.md
  quality_check.py → 품질 체크

Step 4 (평일 UTC 14:00, 자동 FIFO)
  publish_one.py
    → hub_ready() True인 HUB → 최상위 발행
    → 일반 스포크 → 번호 순
    → hub_ready() False인 HUB → 맨 뒤 대기
    → 스택 7편 이하 → Step 1 자동 트리거 (구현 예정)

Step 5 (금 UTC 15:00, 자동)
  step5_audit.py → 품질 감사 → Discord 알림
```

---

## 4. 현재 남은 이슈

### 🔴 미완료
| # | 이슈 | 파일 |
|---|------|------|
| 1 | Step 4 스택 7편 이하 시 Step 1 자동 트리거 | step4_publish.yml |

### 🟡 추후 처리
| # | 이슈 | 파일 |
|---|------|------|
| 1 | Samsung Health HUB 발행 후 내부링크 교체 | _posts/ 07-16, 07-17 |
| 2 | Android/Fallout HUB 없음 | 다음 Step 2 때 HUB 타입 추가 |
| 3 | 발행 전체 감사 (permalink, tags, sources, 서론) | 애드센스 승인 후 |
| 4 | Sources 형식 통일 자동화 | gemini_review_api.py 프롬프트 수정 |
| 5 | published/ 폴더 제거 (publish_one.py에서 아카이브 저장 끄기) | publish_one.py |
| 6 | 백링크 전략 실행 (Quora, Reddit) | 수동 |

### 🟢 완료
- folder 자동 매핑
- file_id 전달 버그
- cmd_review _ct_tag 버그
- git pull rebase || true
- Android Ecosystem 무한루프
- publish_one.py 신버전 파일명 파싱
- Step 2→3 자동 연쇄
- final/ 넘버링 재정립 (001~015, H001~H002)
- HUB H prefix 도입
- publish_order 연속 넘버링
- hub_ready() 전체 스포크 완료 방식
- hub_ready True → 발행 최상위
- Samsung Health, Steam Machine spoke_urls 패치

---

## 5. Search Console 현황

```
색인 생성됨: 17페이지
미생성: 21페이지 (발견됨 - 대기 중 16개)
Google Organic 유입: 6명 (시작됨)
Bing 노출: Chrome MV2 키워드 2위
```

---

## 6. 다음 대화 시작 시 보낼 파일

```
Frontbuffer_프로젝트_정리_v20.md  ← 항상
content_pipeline.json              ← Step 2/3 완료 후
수정이 필요한 파일만               ← 이슈 발생 시
```

---

## 7. GitHub 리포

```
https://github.com/baek2731/frontbuffer
현재 public (Free 플랜 — GitHub Pages 때문에 public 유지)
Private 전환: Pro 플랜($4/월) 필요 → 애드센스 수익 후 고려
```

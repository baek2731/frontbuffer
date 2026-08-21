# Frontbuffer 프로젝트 정리 v25
> 작성일: 2026-08-13

---

## 0. Claude 작업 지침

- **확인은 하되 "오늘 많이 했으니 쉬어요", "다음에 해요" 같은 말은 하지 말 것.** 작업 여부는 사용자가 결정한다.
- **파일은 항상 전체 파일로 제공할 것.** 부분 수정 안내 금지.
- **푸시 코드는 항상 함께 제공할 것.**
- **한국어로만 소통할 것.**

---

## 1. 현재 상태 요약

### 발행 현황
- `_posts/` 발행 완료: **31편** (7/14~8/13)
- `final/` 발행 대기: **9편** (W32 정리 완료, 발행 예정)
- 애드센스: **검토 중** (2026-08-08 신청, ads.txt 추가 완료)
- Step 1 자동 트리거: **3편 이하** 시 자동 실행
- W32 파이프라인: Step 2/3 완료, final/ 9편 대기 중
- W33 weekly_seeds: **입력 완료** (Switch 2 클러스터 3개 + Odyssey G8 클러스터 3개)
- posts.json: **32편** 기록
- W31: **스킵** (W32로 바로 진행)
- W33: Step 1 트리거(8/22 경) 후 Step 2 예정

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
| 07-20 | Chrome MV2 | HUB | /tech/google-chrome-manifest-v2-migration_HUB/ |
| 07-21 | Android Ecosystem | COMPARISON | /tech/android-ecosystem_comparison/ |
| 07-21 | Android Ecosystem | EXPLAINER | /tech/android-ecosystem_explainer/ |
| 07-22 | Android Ecosystem | GUIDE | /tech/android-ecosystem_guide/ |
| 07-23 | Fallout Series | COMPARISON | /gaming/fallout-series_comparison/ |
| 07-24 | Fallout Series | EXPLAINER | /gaming/fallout-series_explainer/ |
| 07-26 | Fallout Series | GUIDE | /gaming/fallout-series_guide/ |
| 07-27 | Portable Gaming | COMPARISON | /gaming/ayaneo-handhelds-vs-steam-deck-performance-portability-comparison/ |
| 07-28 | Portable Gaming | EXPLAINER | /gaming/portable-gaming_explainer/ |
| 07-29 | Samsung Health | HUB | /tech/samsung-health-data-ecosystem/ |
| 07-30 | Steam Machine | HUB | /gaming/steam-machine-hardware-management/ |
| 07-31 | Portable Gaming | GUIDE | /gaming/portable-gaming_guide/ |
| 08-01 | Galaxy Fold | COMPARISON | /tech/01-galaxy-fold_comparison/ |
| 08-02 | Galaxy Fold | EXPLAINER | /tech/01-galaxy-fold_explainer/ ※ sitemap:false + canonical |
| 08-03 | Galaxy Fold | GUIDE | /tech/01-galaxy-fold_guide/ |
| 08-04 | Galaxy Z Flip | COMPARISON | /tech/samsung-galaxy-z-foldflip-series_comparison/ |
| 08-05 | Galaxy Z Flip | EXPLAINER | /tech/samsung-galaxy-z-foldflip-series_explainer/ |
| 08-07 | Galaxy Z Flip | GUIDE | /tech/samsung-galaxy-z-foldflip-series_guide/ |
| 08-08 | Android Auto | COMPARISON | /tech/06-android-auto_comparison/ |
| 08-09 | Android Auto | GUIDE | /tech/06-android-auto_guide/ ※ sitemap:false + canonical |
| 08-10 | Galaxy Fold | EXPLAINER | /tech/the-promise-of-silicon-carbon-batteries-and-samsungs-strateg/ ※ sitemap:false + canonical |
| 08-11 | Android Auto | COMPARISON | /tech/best-wireless-android-auto-adapter-for-older-cars-comparison/ ※ sitemap:false + canonical |
| 08-12 | Android Ecosystem | COMPARISON | /tech/google-pixel-launcher-vs-third-party-android-launchers-featu/ |
| 08-13 | Gaming Media | COMPARISON | /gaming/physical-vs-digital-games-ownership-licenses-and-player-choi/ |

---

## 2. 글쓰기 톤앤매너

### 핵심 원칙
Frontbuffer는 기술/게이밍 주제를 다루는 영어 블로그로, 독자는 특정 문제를 해결하거나 구매/사용 결정을 내리려는 실용적 목적의 방문자다.

### ① 서론: 문제 상황으로 즉시 진입
- **금지**: "has emerged as", "In this article, we will explore", "delves into" 등 AI 관용구
- **권장**: 독자가 실제로 맞닥뜨리는 상황이나 핵심 정보로 첫 문장 시작

### ② 사실 기반, 구체적 수치
- 모델명, 버전, 날짜, 수치를 문장 안에 자연스럽게 녹임

### ③ 외부 링크: 각주 아닌 인라인
- 출처를 앵커 텍스트로 본문에 삽입

### ④ 결론: 실용적 takeaway
- 요약 반복 금지. 독자가 다음에 무엇을 해야 하는지 명확히 제시

### ⑤ 콘텐츠 타입별 특성
| 타입 | 목적 | 특징 |
|------|------|------|
| GUIDE | 단계별 해결 | 번호 리스트, 구체적 절차 |
| EXPLAINER | 개념 이해 | 섹션별 소제목, 비교/한계점 명시 |
| COMPARISON | 선택 보조 | 표 또는 항목별 병렬 구조, 결론에 추천 조건 |
| LISTICLE | 목록형 정보 | 각 항목 독립적으로 읽힘 |
| HUB | 클러스터 허브 | 스포크 글 전체 링크, 내부링크 중심 |

### ⑥ 피해야 할 표현
```
has emerged as / it's worth noting / in conclusion, it is clear that /
in today's world / this article aims to / let's dive into /
it is essential/crucial to / solidify X's position at the forefront /
delves into / unparalleled / furthermore / underscore / hinges on /
boils down to / enduring appeal / paramount / vibrant / shed light on
```

### ⑦ Sources 품질 기준
- ✅ 공식 문서, 제조사 페이지, The Verge/Ars Technica/Android Authority
- ❌ YouTube, Reddit, eBay, Amazon, Game Rant, Fextralife

---

## 3. 파이프라인 전체 흐름

```
Step 1 (final/ 3편 이하 시 Step 4에서 자동 트리거)
  research.py (로컬 수동 실행)
  → RSS 수집 + 락 파일 생성 (.step1_done)
  → Discord "CSV 올려주세요"

Step 2-1 (선택, 수동 트리거)
  seed_inject.py
  → 수동 시드 주제 입력
  → Google News RSS 수집
  → Gemini 기획 → content_pipeline.json append
  → Step 3 자동 트리거

Step 2 (CSV 업로드 후 수동 트리거)
  research_gemini.py
  → weekly_seeds (config.json) 주입
  → content_pipeline.json 저장
  → Step 3 자동 트리거

Step 3 (Step 2 완료 후 자동)
  write.py prep → gemini_api.py (초안) → gemini_review_api.py (최종본)
  → quality_check.py (R5: 발행 불가 패턴)
  → final/{file_id}.md
  → write.py done (pipeline status 업데이트)

Step 4 (매일 UTC 14:00)
  publish_one.py
  → Gemini SEO excerpt 자동 생성 (140~155자)
  → _posts/ 발행
  → posts.json 자동 업데이트
  → og_generator.py (Unsplash + R2 og.png)
  → IndexNow 자동 제출 (Bing)
  → 스택 3편 이하 → Step 1 자동 트리거

Step 5 (금 UTC 15:00)
  step5_audit.py → 품질 감사 → Discord 알림
```

---

## 4. 이미지 시스템

- `og_generator.py` — Unsplash API + R2 업로드
- URL: `https://images.frontbuffer.net/posts/{slug}/og.png`
- header: `og.png` (`overlay_filter: 0`)
- 버킷: `frontbuffer-images` / 도메인: `images.frontbuffer.net`

---

## 5. 수익화

### 애드센스
- **신청일**: 2026-08-08
- **상태**: 검토 중 (2~4주 소요)
- **ads.txt**: 추가 완료 (`pub-7854141204158785`)
- **예상 결과**: 8/22~9/5

### 목표
- 블로그 유지비 + 월 10만원
- 필요 월간 PV: 약 14,000 (일 470 PV)
- 현재 일 평균 ~4명 → 약 100배 성장 필요
- 현실적 달성 시점: 2027년 2~5월 (6~9개월 후)
- 핵심 변수: 애드센스 승인보다 Google organic 유입

### 거절 시 대안
1. Impact.com 제휴 (Best Buy, Newegg 등)
2. 트래픽 일 50명 이상 시 Ezoic 시도
3. 트래픽 일 200명 이상 시 스폰서십 직접 컨택

---

## 6. SEO 현황 (2026-08-13 기준)

### Google Analytics (7/17~8/13, 28일)
- 활성 사용자: 114명 (신규 112명)
- 평균 참여 시간: 13초
- 인기 페이지: Steam Machine LED, Z Flip 8 커버스크린, Fold 8 Ultra 비교
- 유입 소스: Direct 99 / Google organic 6 / Product Hunt 3 / Quora 1

### Google Search Console
- 색인: 17편 (발행 31편)
- 발견됨-색인미생성: 24편 (크롤 예산 부족)
- 수동 색인 요청: 완료

### Bing Webmaster
- Indexed URLs: 16개
- Impressions: 65 (상승 중)
- Clicks: 2
- URL Submission: 32개 제출 완료

---

## 7. 백링크 루틴

### 계정 현황
| 사이트 | 계정 | 상태 | 링크 가능 시점 |
|--------|------|------|--------------|
| Quora | FrontBuffer | 활성 (답변 10개+) | 즉시 가능 |
| Dev.to | Frontbuffer Editorial | 활성 | 즉시 가능 |
| Hacker News | FrontBuffer_FB | 활성 | 즉시 가능 |
| XDA Developers | Frontbuffer | 워밍업 중 | 8/20 이후 |
| Reddit | - | 워밍업 중 | 카르마 쌓인 후 |
| Product Hunt | buffer_front | 8/12 론칭 완료 | - |

### 요일별 정규 루틴 (15~20분)
| 요일 | 작업 | 비고 |
|------|------|------|
| 월 | Quora 답변 1개 (링크 포함) | 발행된 글 중 시의성 있는 것 |
| 화 | XDA 답변 1개 (링크 없이 → 8/20 후 링크 포함) | |
| 수 | Quora 답변 1개 (링크 포함) | |
| 목 | Dev.to 글 발행 1개 (canonical URL 필수) | |
| 금 | HN 제출 1개 | 그 주 발행된 글 중 1개 |
| 토 | Reddit 워밍업 (링크 없이) | 관련 서브레딧 순수 답변 |
| 일 | 휴식 or 밀린 것 보완 | |

### 백링크 작업 원칙
- Quora: 링크는 3~4개 답변 중 1개에만 포함
- Dev.to: canonical URL 반드시 설정
- XDA: 8/20 이전은 링크 없이 순수 답변만
- Reddit: 서브레딧 규칙 확인 후 진행
- 질문 찾기 → 내용 파악 → 답변 작성 순서 준수

### 오늘(8/13) 완료
- Quora: Samsung Health 백업/전송 답변 (링크 포함) ✅
- XDA Android Auto General: 무선 연결 Wi-Fi 안정성 답변 (링크 없이) ✅

---

## 8. 현재 이슈

### 🟡 진행 중
| # | 이슈 | 예정 |
|---|------|------|
| 1 | 애드센스 결과 대기 | 8/22~9/5 |
| 2 | XDA 링크 포함 전환 | 8/20 이후 |
| 3 | W33 Step 1 트리거 대기 → Step 2 수동 실행 | 8/22 경 |
| 4 | Reddit 워밍업 | 지속 |
| 5 | Dev.to 글 발행 | 목요일 정규 루틴 |

### 중복 글 현황 (처리 완료)
| 글 | 중복 대상 | 처리 |
|---|---|---|
| 08-02 Galaxy Fold EXPLAINER | 08-05 Silicon-Carbon EXPLAINER | ✅ sitemap:false + canonical |
| 08-09 Android Auto GUIDE | 08-08 Android Auto COMPARISON | ✅ sitemap:false + canonical |
| 08-10 Silicon-Carbon EXPLAINER | 08-05 Silicon-Carbon EXPLAINER | ✅ sitemap:false + canonical |
| 08-11 Android Auto COMPARISON | 08-08 Android Auto COMPARISON | ✅ sitemap:false + canonical |

### 🟢 완료
- W32 Step 2/3 완료 (9편 final/ 대기)
- W33 weekly_seeds 입력 완료 (Switch 2 + Odyssey G8 클러스터)
- Gemini SEO excerpt 자동 생성 (publish_one.py)
- sitemap 정리, ads.txt, IndexNow
- 백링크 계정 전체 셋업
- SEO excerpt em dash → 하이픈 교체 (15개 파일)
- 전체 31편 글 품질 점검 및 AI 톤 수정 완료
- 백링크 요일별 정규 루틴 설계 완료

---

## 9. W33 weekly_seeds (config.json 입력 완료)

### Nintendo Switch 2 클러스터
1. `why old microSD cards do not work in Nintendo Switch 2 and which microSD Express cards are compatible`
2. `Nintendo Switch 2 Pro Controller vs 8BitDo Ultimate 2C comparison for drift and value in 2026`
3. `how to set up and expand storage on Nintendo Switch 2 with microSD Express step by step`

### Samsung Odyssey G8 클러스터
4. `Samsung Odyssey G8 Dual Mode explained when to use 6K 165Hz vs 3K 330Hz for gaming`
5. `Samsung Odyssey G8 IPS vs OLED G8 which monitor to buy for gaming in 2026`
6. `what GPU do you need to run 6K gaming on Samsung Odyssey G80HS in 2026`

---

## 10. 주요 파일

```
publish_one.py          — Step 4 발행
og_generator.py         — OG 이미지 생성 + R2 업로드
research.py             — Step 1 RSS 수집
research_gemini.py      — Step 2 Gemini 기획
seed_inject.py          — Step 2-1 개별 주제 추가
write.py                — Gemini 프롬프트 + 글 생성
step5_audit.py          — 주간 품질 감사
config.json             — weekly_seeds 설정
posts.json              — 발행 글 목록
```

---

## 11. GitHub

```
https://github.com/baek2731/frontbuffer
Public (GitHub Pages Free 플랜)
```

---

## 12. 다음 대화 시작 시 보낼 파일

```
Frontbuffer_프로젝트_정리_v25.md  ← 항상
content_pipeline.json              ← Step 2/3 완료 후
수정이 필요한 파일만               ← 이슈 발생 시
```

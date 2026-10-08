# Frontbuffer 프로젝트 정리 v32
> 작성일: 2026-10-08 (v31 → v32: 9/29~10/5 글 전수 수정, 중복 정리 1차, OG 생성기 개편, GA/Bing/Search Console 분석 반영)

---

## 0. Claude 작업 지침

- **확인은 하되 "오늘 많이 했으니 쉬어요", "다음에 해요" 같은 말은 하지 말 것.** 작업 여부는 사용자가 결정합니다.
- **파일은 항상 전체 파일로 제공할 것.** 부분 수정 안내 금지.
- **푸시/풀 코드만 별도로 제공할 것.** 파일 복사/붙여넣기는 사용자가 직접 하므로 `copy` 명령은 안내하지 않습니다.
- **한국어로만 소통할 것. 말투는 항상 존댓말(~습니다 / ~입니다 / ~하세요 체).**
- **다운로드 경로: C:\Users\B\Downloads / 로컬 루트: C:\Users\B\Projects\blogauto2**
- **사실 확인 원칙:** 가격, 스펙, 날짜, 패치 버전은 기억이 아니라 검색(공식 + 복수 매체)으로 확인하고, 확인 못 한 것은 "확인 필요"로 표시합니다.
- **출처 원칙:** 루트 도메인(메인 페이지) 링크 금지. 개별 기사 URL만 사용. 금지 출처는 섹션 2⑦ 참조.

---

## 🔧 자주 쓰는 명령어 모음

### Git 기본
```cmd
# 풀 받기 (저장 안 한 변경이 있으면 stash 사용)
cd C:\Users\B\Projects\blogauto2 && git pull
cd C:\Users\B\Projects\blogauto2 && git stash && git pull && git stash pop

# 전체 푸시 (순서 중요: 커밋 → pull --rebase → push)
cd C:\Users\B\Projects\blogauto2 && git add -A && git commit -m "커밋메시지" && git pull --rebase && git push

# 글 삭제 (파일만 삭제, posts.json은 건드리지 않음)
cd C:\Users\B\Projects\blogauto2\_posts && del 파일명.md

# 파일 위치 찾기
dir /s /b C:\Users\B\Projects\blogauto2\*검색어*
```
> ⚠️ `git pull --rebase`는 저장 안 한 변경이 있으면 실행되지 않습니다. 반드시 **commit 먼저, pull --rebase 나중에**.
> ⚠️ cmd에서 한글 줄이 깨져 보이는 것은 화면 표시 문제일 뿐 파일은 정상입니다.

### 주요 커밋 메시지 패턴
```cmd
git commit -m "add W40 step1 CSV"
git commit -m "fix: quality pass 날짜범위, 수정내용"
git commit -m "feat: 기능내용"
git commit -m "chore: OG 이미지 재생성 — 날짜"
```

### 파이프라인 수동 실행 순서
```
1. git pull
2. Step 1: GitHub Actions → step1_research.yml → Run workflow
3. Step 1 완료 후 CSV 다운로드 → research_data/ 폴더에 넣기
4. git add -A && git commit -m "add W?? step1 CSV" && git pull --rebase && git push
5. Step 2: GitHub Actions → step2_plan.yml → Run workflow
6. Step 3: 자동 실행 (Step 2 완료 후)
7. Step 4: 자동 실행 (매일 UTC 14:00) 또는 step4_publish.yml → Run workflow
```

### OG 이미지 재생성 (v2, 2026-10 개편)
```
GitHub Actions → OG Image Regenerate → Run workflow
→ date: 여러 개 가능  예) 2026-10-01 2026-10-02   또는   2026-10-01,2026-10-02
→ 비워두면 OG 없는 글만 생성 (이미 있으면 스킵)
→ force_all: true  (소문자 true만 인식. 전체 강제 재생성)
→ refresh_photo: false (기본. 기존 배경 사진 재사용 → Unsplash API 호출 없음)
   true 로 하면 배경 사진도 Unsplash에서 새로 받음 (전체에 쓰지 말 것: 호출 제한)
```
- 워크플로우 파일 위치: `.github/workflows/og_regenerate.yml` (루트에 두면 적용 안 됨)
- OG 이미지에는 **제목 + excerpt가 들어갑니다.** 제목/excerpt를 바꾼 글은 해당 날짜로 재생성 필요.
- 로그 확인: `♻️ 기존 배경 사진 재사용` 정상 / `기존 배경 사진 없음`, `모든 시도 실패`는 0이어야 정상.
- 같은 날짜에 글이 여러 개면 모두 재생성됩니다.
- 확인 URL 예: `https://images.frontbuffer.net/posts/{slug}/og.png?v=숫자` (캐시 회피)

---

## 📋 자주 묻는 작업 패턴

### 새 대화 시작 시 루틴
1. `Frontbuffer_프로젝트_정리_v32.md` 업로드
2. "어디까지 했지?" → 이 MD의 **섹션 10 남은 작업** 참조
3. 작업할 파일들 업로드

### 발행 대기 글 전수조사 (final/)
```
final/ 파일을 업로드하면 Claude가 확인:
- 금지어 / 불량출처 / 루트 도메인 링크
- front matter (제목 깨짐, excerpt 마크다운 기호, 태그 junk, 카테고리)
- 사실 오류(가격/스펙/날짜) → 검색으로 대조
- 기존 글과 주제 중복 여부 (기기 × 의도)
```

### _posts/ 글 피드백 루틴
```
1. git pull
2. _posts/ 에서 피드백 안 된 날짜 파일 업로드
3. Claude가 전수조사 후 수정본 제공
4. 수정본 _posts/ 에 덮어쓰기
5. 푸시 → 제목/excerpt 바뀐 글은 OG 재생성(날짜 여러 개 입력)
```

### 중복 글 정리 판단 기준
```
1. Bing 페이지 리포트(PageTrafficReport)에서 URL별 노출/클릭 대조
2. 노출 있는 글 = 대표 글. 없는 글은 고유 내용만 대표에 병합 후 삭제
3. 삭제 시 posts.json은 건드리지 않음 (재발행 방지)
4. 대표 글의 파일명/카테고리는 바꾸지 않음 (URL 유지)
```

### Bing CTR 최적화 / Search Console 색인 요청
```
Bing: Search Performance CSV → 순위 1~5위인데 CTR 0% 키워드 → 제목/excerpt 수정
Search Console: URL 검사 → 색인 생성 요청 (하루 3~4개)
  제외: 페이지네이션(/page?/), 중복 정리 대기 글
```

---

## 1. 현재 상태 요약 (2026-10-08 기준)

### 발행 현황
- `_posts/` 파일: **69편** (10/6 OG 재생성 시점, `android-system-features` 슬러그 충돌 2편 포함)
- 애드센스: **거절** (사유: 가치가 별로 없는 콘텐츠 + 복제된 콘텐츠) / 목표: Ezoic
- Step 1 트리거: 스택 기반 (월요일 cron 제거)
- 중복 정리: **1차 완료 5편 삭제**, 2차 대기 (섹션 10)

### 이번 라운드(v31→v32) 완료 내역
| 구분 | 내용 |
|---|---|
| 글 수정 (9/29~10/5, 8편) | Elden Ring(카테고리 gaming으로 변경), Skyrim, Ubisoft, Googlebook 3편(가격/칩/화면/배터리 교정), Pixel 10 vs 11(스펙/출시 시점 교정), Pixel voice typing |
| 허브/가이드 | Chrome MV2 HUB(8/31 제거 사실 반영), Z Flip 8 커버 화면 앱 글 재작성 |
| 중복 삭제 | 08-02, 08-10, 08-11, 08-29, 09-02 |
| 대표 글 복원/보정 | 08-26 Android 16 desktop mode, 08-31 Switch 2 microSD Express, 07-16 Samsung Health(09-02 병합), 08-05 메타 정리 |
| OG 생성기 v2 | `--date` 다중 입력, 기존 배경 재사용, 배지/크레딧 겹침 수정, `''` 표시 수정, 말줄임, `refresh_photo` |
| OG 전체 재생성 | 69편 완료 (재사용 100%, 실패 0) |

### 최근 발행 이력 (9/29 이후)
| 날짜 | 제목 | 상태 |
|------|------|------|
| 09-29 | Elden Ring PC vs console performance | ✅ 수정 완료 (URL이 /tech/→/gaming/으로 바뀜) |
| 09-29 | Skyrim IKEA mods | ✅ |
| 09-30 | Ubisoft Connect offline | ✅ |
| 10-01 | Chromebook vs Googlebook: which one should you buy? | ✅ 구매 결정형 |
| 10-02 | Googlebook models compared | ✅ |
| 10-03 | Pixel 10 vs Pixel 11 camera | ✅ |
| 10-04 | What is Googlebook | ✅ 기능 설명형 |
| 10-05 | Pixel voice typing | ✅ |
| 10-06 | Galaxy Z Fold Series vs Flip Series | ⚠️ 미검수, Fold/Flip 4번째 비교 → 정리 대기 |

### 피드백 현황
- **마지막 피드백 완료:** 2026-10-05
- **미검수:** 10-06 이후 발행분
- **정리 대기:** 08-25, 09-07 (슬러그 충돌), 08-09 vs 08-14 (Android Auto), 09-10 vs 09-16 (Pixel 11 vs Pro), 09-04 / 09-15 / 10-06 (Fold vs Flip)

---

## 2. 글쓰기 톤앤매너

### 핵심 원칙
영어 블로그. 독자는 특정 문제를 해결하거나 구매/사용 결정을 내리려는 실용적 방문자입니다.

### ① 서론: 문제 상황으로 즉시 진입
- 금지: "has emerged as", "In this article, we will explore", "This article covers/explains", "delves into"
- 권장: 독자가 맞닥뜨리는 상황이나 핵심 정보로 첫 문장 시작

### ② 사실 기반, 구체적 수치
- 모델명, 버전, 날짜, 수치를 문장에 녹이고, **확인 날짜(Checked 날짜)**를 본문에 표기합니다.
- 직접 테스트하지 않았으면 "직접 테스트하지 않았다"고 명시합니다.

### ③ 외부 링크: 각주 아닌 인라인
### ④ 결론: 실용적 takeaway (요약 반복 금지)

### ⑤ 콘텐츠 타입별 특성
| 타입 | 목적 | 특징 |
|------|------|------|
| GUIDE | 단계별 해결 | 번호 리스트, 문제 해결 순서 |
| EXPLAINER | 개념 이해 | 섹션별 소제목, 한계점 명시 |
| COMPARISON | 선택 보조 | 표, 결론에 추천 조건 |
| LISTICLE | 목록형 | 각 항목 독립적으로 읽힘 |
| HUB | 클러스터 허브 | 상황별로 어느 글을 읽을지 안내, 내부링크 중심 |

### ⑥ 피해야 할 표현
```
has emerged as / it's worth noting / in conclusion, it is clear that /
in today's world / this article aims to / let's dive into /
it is essential/crucial to / delves into / unparalleled / furthermore /
underscore / hinges on / boils down to / enduring appeal / paramount /
vibrant / shed light on / revolutionary / cutting-edge / innovative /
pushing the boundaries / remarkable / seamlessly / comprehensive / robust /
testament to / meticulous / commendable / highly anticipated / non-negotiable
```

### ⑦ Sources 품질 기준
- ✅ 공식 문서, 제조사 페이지, The Verge/Ars Technica/Android Authority/9to5Google (개별 기사 URL)
- ❌ YouTube, Reddit, eBay, Amazon, Game Rant, Fextralife, CNET, PhoneArena, GSMArena, TechRadar, Tom's Guide, SamMobile, Wikipedia, Gadgets360
- ❌ 루트 도메인 링크 (androidauthority.com 등 메인 페이지)

### ⑧ front matter 규칙
- `tags`: 의미 있는 단어만 (`"and"`, `"features"` 같은 junk 금지). 첫 태그는 타입(guide/explainer/comparison/hub).
- `categories`: 내용에 맞게 (gaming / tech). **카테고리 변경 = URL 변경** (아래 ⑨).
- `excerpt`: 140~160자, 마크다운 기호(`*`, 백틱) 금지, 잘린 `…` 금지 (OG 이미지와 메타 설명에 그대로 쓰임).
- 제목 약 65자 이하 (Bing "Title too long" 방지).

### ⑨ URL 규칙 (중요)
- `permalink: /:categories/:title/` → **파일명(슬러그) 또는 카테고리를 바꾸면 URL이 바뀜.** `jekyll-redirect-from` 플러그인이 없어 옛 URL은 404.
- 노출/순위가 있는 글은 파일명과 카테고리를 바꾸지 않음.
- 07-16 Samsung Health 글은 `permalink:`가 front matter에 고정되어 있음.
- 내부 링크는 `{% post_url 날짜-슬러그 %}` 사용 가능하나, **파일명을 바꾸면 Jekyll 빌드가 깨질 수 있음.** 파일명 변경 시 이 링크 먼저 확인.
- 같은 슬러그의 파일 2개 = 같은 URL을 차지해 한쪽이 안 보임 (섹션 10 #1).

---

## 3. 파이프라인 전체 흐름

```
Step 1 (final/ 3편 이하 시 Step 4에서 자동 트리거)
  research.py → RSS 수집 → Discord 알림

Step 2 (CSV 업로드 후 수동 트리거)
  research_gemini.py → content_pipeline.json → Step 3 자동 트리거

Step 3 (Step 2 완료 후 자동)
  write.py → gemini_api.py → gemini_review_api.py → final/{file_id}.md

Step 4 (매일 UTC 14:00 = 한국 밤 11시)
  publish_one.py
  → 발행 여부: posts.json 기반 1차 + pipeline url 소문자 비교 2차
  → _posts/ 발행 → posts.json 업데이트
  → og_generator.py (Unsplash + R2)
  → IndexNow 자동 제출 (Bing)
  → 스택 3편 이하 → Step 1 자동 트리거

Step 5 (금 UTC 15:00)
  step5_audit.py → 품질 감사 → Discord 알림
```

**알려진 구조적 문제:** 같은 주제를 설명/가이드/비교/허브 4종으로 반복 생성하고, 기존 글과의 주제 중복 검사가 없어 Fold vs Flip 비교가 4~5편 나옴 (섹션 10 #12).

---

## 4. 이미지 시스템

- `og_generator.py` v2 — Unsplash API + R2 업로드. 재생성 시 `header.jpg`(social_output 또는 R2)를 재사용.
- URL: `https://images.frontbuffer.net/posts/{slug}/og.png` (slug = 파일명에서 날짜 뺀 부분)
- 이미지 구성: 사이트명, 제목, excerpt(2줄), 카테고리 배지, "Photo: Unsplash" 크레딧, 도메인.
- 같은 슬러그 2개면 R2의 og.png/header.jpg가 서로 덮어씀.

---

## 5. 수익화

### 애드센스
- **상태:** 거절 (가치 없는 콘텐츠 + 복제된 콘텐츠)
- **트래픽 최소 기준은 공식적으로 확인되지 않음.** 본질은 콘텐츠 품질과 중복.
- **재신청 점검 목록:** (1) 중복 정리 완료 (2) 조회 상위 10~15편 사실 오류 점검 (3) 5~10편에 직접 확인한 요소 추가 (4) About/Privacy/Disclosure 확인 + **Contact 링크 추가** (5) Bing `research_data` URL 제거 (6) Google 색인 40편+ ✅ (47편)
- **목표 시점:** 점검 목록 완료 후 개선 2~4주 대기 → **빠르면 11월 중순** (미완료 시 연기. 같은 상태로 재신청 금지)

### 제휴 / Ezoic
- 트래픽 없이는 수익이 거의 0 → 트래픽과 품질이 선행 과제. 제휴 링크는 구매 결정 글에 넣어 두되 **글 상단에 제휴 안내 한 줄** 필수.
- Ezoic 요건은 공식 페이지에서 재확인 필요.

---

## 6. SEO / 트래픽 현황

### Google Analytics (10/1~10/6, 5일 유효)
- 활성 사용자 35명 (일 약 7명), 신규 33명, 참여시간 **16.3초** (이전 20.3초)
- Direct 77%, DuckDuckGo 5, Bing 2, **Google organic 0**
- 데이터센터 도시(Singapore, Boardman, Ashburn 등) 16명(46%) → **봇 비중 높음, 실제 사람은 일 1~2명 추정**
- 새 글은 모두 2뷰/1명/이벤트 5 동일 패턴 (크롤러 또는 본인 확인 추정)
- 이탈률 낮은 글: Steam Machine 문제해결 글 3개 + Google Photos 글

### Bing Webmaster (10/6 export, 기간 미표시)
- 키워드 511개 / 노출 787 / 클릭 18 (CTR 2.3%) | 페이지 39개 / 노출 1,052 / 클릭 18
- 노출의 약 60%가 허브·가이드·비교 계열 URL에서 발생
- **7단어 이상 긴 문장 검색어 55%** → AI 어시스턴트 검색일 가능성 (노출 대비 클릭 낮음)
- 가장 CTR 좋은 글: Steam Machine LED Error Codes (노출 28, 클릭 2, 4.4위)
- 9/29~10/5 신규 글은 Bing 노출 0 (아직 색인/순위 없음)
- 과거 `research_data/...` URL이 Bing에 색인된 기록 → **Block URLs 요청 필요** (현재 404)

### Google Search Console (10/4 기준)
- 색인 **47** / 미색인 **31** (발견됨-미색인 24, 크롤링됨-미색인 2, 리디렉션 포함 3, 리디렉션 오류 1, robots 차단 1)
- 노출: 7/20주 288 → 9월 초 주 6~18 → 9/25~28에 191 (급증) → 최근 6일 12
- **9/25~28 급증은 단일 페이지:** `/tech/android-system-features/` (Google Messages 롱프레스 메뉴 글) 노출 185, 클릭 4, **평균 1.01위** — 검색어 "google messages new menu update" 등. 미국 모바일 94%.
- 시사점: **신기능 롤아웃 직후 "무엇이 바뀌었나 + 사용법" 글**이 Google에서 이기는 유일한 유형. 단, 노출은 4일 만에 소멸.
- 24개 "발견됨-미색인" 대부분이 9/17~9/30 글 → 2주 넘게 크롤되지 않음. 10/1~10/5 글은 목록에도 없음 → 사이트맵이 오래됐을 가능성.

### 현재 병목
**Google이 새 글을 읽지 않음 + 사이트 내 유사 글 중복 + 외부 링크 부족(dev.to 1개)**

---

## 7. 전망 로드맵

| Phase | 내용 | 상태/시점 |
|-------|------|---------|
| 1 | 색인 40편 달성 | ✅ 47편 |
| 2 | 중복 정리 + 사이트 품질 점검 | 10월 진행 중 |
| 3 | Google 크롤 정상화 (24개 backlog 해소) + Bing organic 안정화 | 10~11월 |
| 4 | 애드센스 재신청 | 조건 충족 시 11월 중순~12월 |
| 5 | Ezoic / 제휴 | 트래픽 이후 |

---

## 8. 백링크 루틴

| 요일 | 작업 |
|------|------|
| 월 | Quora 답변 1개 |
| 화 | XDA 답변 1개 |
| 수 | Quora 답변 1개 |
| 목 | Dev.to 발행 (canonical 필수) |
| 금 | HN 제출 1개 |
| 토 | Reddit 워밍업 |

> ⚠️ 추석 이후 **미재개**. 횟수를 줄이고 질을 올리는 방향 권장 (Dev.to 주 1회 + Hashnode 등 canonical 허용 플랫폼 + 실제 문제를 해결하는 포럼 답변).

---

## 9. 주요 파일

```
publish_one.py                  — Step 4 발행
og_generator.py (v2)            — OG 생성 (--date 다중, 사진 재사용)
.github/workflows/og_regenerate.yml — OG 수동 재생성 (date 다중, refresh_photo)
research.py / research_gemini.py / write.py — Step 1~3
step5_audit.py                  — 주간 품질 감사
config.json                     — weekly_seeds
posts.json                      — 발행 글 목록 (발행 여부 판단 소스)
content_pipeline.json           — 파이프라인 상태
_config.yml                     — exclude: research_data/ 설정됨 (정상)
```

---

## 10. 남은 작업 (우선순위 순)

### 🔴 긴급
| # | 작업 | 필요한 것 |
|---|------|----------|
| 1 | **`android-system-features` 슬러그 충돌:** 08-25(Quick Settings)와 09-07(Google Messages)이 같은 URL. **09-07은 이름 변경 금지**(Google 1위 URL). **08-25만 새 슬러그로 변경** + `header.image` 경로 수정 + `--date 2026-08-25` OG 재생성 | `2026-08-25-android-system-features.md`, `2026-09-07-android-system-features.md` |
| 2 | **Android Auto 중복:** 08-09 `06-android-auto_guide`(복원했으나 08-14와 동일 제목) vs 08-14 `how-to-fix-android-auto-wireless-connection-issues` → 하나 삭제/병합 | `2026-08-14-how-to-fix-android-auto-wireless-connection-issues.md` |
| 3 | **Pixel 11 vs Pro 중복:** 09-10 `...camera-differences` vs 09-16 `...camera-features-and-differences`(Bing 노출 있음, 대표) → 09-10 병합 후 삭제 | 두 파일 |
| 4 | **Fold vs Flip 중복(4편):** 09-04(`...is-b`), 09-15(`anticipating`), 09-22(`shou`, 검수 완료·대표), 10-06 → 병합/삭제 | 09-04, 09-15, 10-06 파일 |
| 5 | **Search Console 사이트맵:** Sitemaps에서 마지막 읽은 날짜 확인 → 재제출. 색인 보고서를 "제출된 모든 페이지"로도 확인 | 직접 |
| 6 | **Bing Block URLs:** `https://frontbuffer.net/research_data/write/published/2026-07-14-how-to-troubleshoot-steam-machine-overheating-and-red-light-issues/` 제거 요청 | 직접 |

### 🟠 이번 주
| # | 작업 | 비고 |
|---|------|------|
| 7 | **색인 요청 (하루 3~4개):** ① chat bubbles(Messages 주제) ② Steam Frame 세팅 ③ Steam Frame vs Steam Deck ④ Fold vs Flip 09-22 대표 ⑤ DLSS 5 ⑥ Android passkeys ⑦ 01-galaxy-fold_guide(배터리) | 제외: 페이지네이션, 정리 대기 글(09-04, speculative-showdown) |
| 8 | **허브 2개 신규:** Galaxy Z Fold 8/Flip 8 허브(Fold/Flip 계열 8개 URL 묶기), Steam Frame 허브(3편 묶기) → 크롤 backlog 해소용 내부 링크 | 중복 정리 후 |
| 9 | **Google Search Console 확인:** "크롤링됨-미색인 2", 리디렉션 4, robots 1의 URL 목록 확인 (의도된 것인지) | Search Console 내보내기 |
| 10 | **Bing SEO 경고:** Title too long 3, Meta description too short 8 | `SEOAnalysisSummary` CSV 필요 |
| 11 | **Elden Ring URL 변경(/tech→/gaming):** IndexNow로 새 URL 제출. 옛 URL은 404(무시) | |
| 12 | **파이프라인 중복 방지 개선** (아래 별도 항목) | `config.json`, `research_gemini.py`, `write.py`, `content_pipeline.json` |
| 13 | **GA4 내부 트래픽 필터** 설정 | 직접 |
| 14 | **백링크 루틴 재개** (축소 버전) | |

### 12번 상세: 파이프라인 중복 방지 / 주제 폭 확장
- 중복 기준을 **"기기 × 의도"**로 변경 (같은 기기도 설정/문제해결/호환/대안/업데이트는 서로 다른 글).
- 글 계획 시 기존 제목 목록을 프롬프트에 넣고 "다루지 않은 각도만" 제안.
- 후보 제목을 posts.json 기존 제목과 단어 겹침률로 비교(60%+면 건너뜀).
- 이미 있는 주제에 새 사실이 생기면 새 글 대신 **기존 글 업데이트**.
- **신기능 롤아웃 뉴스형 seeds 추가:** Pixel Drop, Android QPR, Google Messages, One UI, Steam 클라이언트, Chrome 릴리스 변경 (24~48시간 내 "what changed + how to use").
- 출시 전 추측/기대(anticipating, speculative) 글 축소.
- 발행 속도 **주 3~4편 + 직접 확인 요소 포함 글 우선** 검토.
- **Bing 키워드 기반 주제 후보(월 1회 갱신):**
  - Steam Machine 증상: 파란불 숨쉬듯 깜박임 / 파란불 고정 부팅 불가 / 노란불 / 초록 깜박임 / LED 밝기·색 변경·끄기
  - Z Flip 8 커버 화면 앱 추천, 앱 연속성(continuity)
  - Samsung Health: 삭제 데이터 복원, 병합, CSV 가져오기 불가 설명
  - Chromium 계열 브라우저 MV2 지원 현황, uMatrix 대체
  - AYANEO 모델별 vs Steam Deck, Switch 2 microSD Express 설치 방법, DLSS 5 호환 기기
  - Google Photos storage (기존 이슈 #8)

### 🟡 사실 점검 대기 (이번 라운드에서 확인 못 한 것)
- 08-05 실리콘카본: "Fold 8 Ultra 30분 67% 충전", "저온 성능" 수치
- 08-08 Android Auto 어댑터 비교: 직접 테스트 안 했다는 명시, 일부 사용자 사례 인용 정리
- Z Flip 8 글: 12개 시스템 앱 이름 목록, 서드파티 4개(Netflix 포함) 실제 폰에서 대조
- Googlebook: Lenovo 가격($1,099 vs $1,299), 공식 페이지 대조
- Pixel 10 vs 11: Pixel 11 출시 월(8월), 이전 Pixel 11 글과 날짜 일치 확인
- 열리는지 확인 안 된 URL: Google Pixel 11 공식, Android Authority Pixel 11, Ubisoft/Steam 지원, Pixel/Gboard 지원, Android Auto Help, Samsung AU 백업 지원 페이지
- Elden Ring: Patch 1.02.1/1.02.2 공식 패치노트(TechRadar 출처였음)
- 07-16 Samsung Health 최신본 푸시 여부 (`git log`에서 "07-16 전송 가이드 링크 복원" 커밋 확인)

### 🟢 모니터링 (1~2주 후)
- Bing CTR 변화 (9/29 최적화 9개 + 허브 수정 + 제목 변경 글)
- Google 24개 backlog 해소 / 색인 47 → 증가 여부
- GA Google organic 첫 유입 여부
- Steam Machine 증상별 글 신규 반응

### 중복 글 (sitemap:false 이력)
- 삭제 완료: 08-02, 08-10, 08-11, 08-29, 09-02
- 단독 글로 복원: 08-26, 08-31 (canonical/sitemap:false 제거)
- 아직 sitemap:false+canonical 상태: **08-09**(정리 대기), 나머지 이력 글은 `findstr "sitemap:" *.md`로 확인

### 🔧 버그 수정 완료 이력
- publish_one.py v27/v29/v30, og_regenerate.yml 위치/입력 개편, og_generator.py v2
- GTA VI, Nintendo Switch YAML, 04-pixel-pro slug 충돌
- research_data는 `_config.yml` exclude 설정 정상 (Bing의 옛 URL 기록만 잔존)

---

## 11. GitHub

```
https://github.com/baek2731/frontbuffer
Public (GitHub Pages Free 플랜)
```

---

## 12. 다음 대화 시작 시 보낼 파일

```
Frontbuffer_프로젝트_정리_v32.md   ← 항상

[긴급 작업용 — 이 순서로]
_posts\2026-08-25-android-system-features.md
_posts\2026-09-07-android-system-features.md
_posts\2026-08-14-how-to-fix-android-auto-wireless-connection-issues.md
_posts\2026-09-10-pixel-11-vs-pixel-11-pro-camera-differences.md
_posts\2026-09-16-pixel-11-vs-pixel-11-pro-camera-features-and-differences.md
_posts\2026-09-04-galaxy-z-fold-8-vs-galaxy-z-flip-8-which-foldable-phone-is-b.md
_posts\2026-09-15-galaxy-z-fold-8-vs-galaxy-z-flip-8-anticipating-samsungs-nex.md
_posts\2026-10-06-galaxy-z-fold-series-vs-galaxy-z-flip-series-which-foldable-.md

[파이프라인 개선용]
config.json, research_gemini.py, write.py, content_pipeline.json

[분석용 — 월 1회]
GA 보고서_개요.csv / Bing CSV 6종(SearchPerformanceOverview, KeywordReport,
AIPerformanceOverviewStats, AISearchQueriesReport, ReferringDomains, SEOAnalysisSummary) /
Search Console 성능·색인 CSV
```

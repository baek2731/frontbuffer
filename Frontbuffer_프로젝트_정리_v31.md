# Frontbuffer 프로젝트 정리 v31
> 작성일: 2026-09-29

---

## 0. Claude 작업 지침

- **확인은 하되 "오늘 많이 했으니 쉬어요", "다음에 해요" 같은 말은 하지 말 것.** 작업 여부는 사용자가 결정합니다.
- **파일은 항상 전체 파일로 제공할 것.** 부분 수정 안내 금지.
- **푸시 코드는 항상 함께 제공할 것.**
- **한국어로만 소통할 것.**
- **말투: 항상 존댓말(~습니다 / ~입니다 / ~하세요 체)로 소통할 것.**
- **다운로드 경로: C:\Users\B\Downloads**
- **로컬 루트: C:\Users\B\Projects\blogauto2**

---

## 🔧 자주 쓰는 명령어 모음

### Git 기본
```cmd
# 풀 받기
cd C:\Users\B\Projects\blogauto2 && git pull

# 전체 푸시 (가장 자주 씀)
cd C:\Users\B\Projects\blogauto2 && git add -A && git commit -m "커밋메시지" && git push

# 특정 파일만 푸시
cd C:\Users\B\Projects\blogauto2 && git add 파일경로 && git commit -m "커밋메시지" && git push

# 특정 날짜 파일 확인
dir C:\Users\B\Projects\blogauto2\_posts\2026-09-15*

# 파일명 변경
rename 원본파일명.md 새파일명.md

# sitemap 처리된 파일 확인
cd C:\Users\B\Projects\blogauto2\_posts && findstr "sitemap:" *.md
```

### 주요 커밋 메시지 패턴
```cmd
# 주차 CSV 푸시
git commit -m "add W40 step1 CSV"

# 글 품질 수정
git commit -m "fix: quality pass 날짜범위, 수정내용"

# 버그 수정
git commit -m "fix: 버그내용"

# 기능 추가
git commit -m "feat: 기능내용"

# OG 이미지
git commit -m "chore: OG 이미지 재생성 — 날짜"
```

### 파이프라인 수동 실행 순서
```
1. git pull
2. Step 1: GitHub Actions → step1_research.yml → Run workflow
3. Step 1 완료 후 CSV 다운로드 → research_data/ 폴더에 넣기
4. git add -A && git commit -m "add W?? step1 CSV" && git push
5. Step 2: GitHub Actions → step2_plan.yml → Run workflow
6. Step 3: 자동 실행 (Step 2 완료 후)
7. Step 4: 자동 실행 (매일 UTC 14:00) 또는 step4_publish.yml → Run workflow
```

### OG 이미지 재생성
```
GitHub Actions → OG Image Regenerate → Run workflow
→ date 입력: 2026-09-14 (해당 날짜 파일 재생성)
→ 비워두면 전체 미처리
→ force_all: true 이면 전체 강제
```

---

## 📋 자주 묻는 작업 패턴

### 새 대화 시작 시 루틴
1. `Frontbuffer_프로젝트_정리_v??.md` 업로드
2. 필요시 `content_pipeline.json` 업로드
3. 작업할 파일들 업로드
4. "어디까지 했지?" → 이 MD의 섹션 10 이슈 목록 참조

### 발행 대기 글 전수조사
```
final/ 폴더 파일들을 업로드하면 Claude가:
- cite 패턴 / 한국어 본문 / [INTERNAL LINK] 차단 패턴 확인
- 금지어 / 불량출처 확인
- front matter 버그 (제목 깨짐, excerpt "layout: single") 확인
→ 문제 있으면 수정본 제공
```

### _posts/ 글 피드백 루틴
```
1. git pull
2. _posts/ 에서 피드백 안 된 날짜 파일들 업로드
3. Claude가 전수조사 후 수정본 제공
4. 수정본 _posts/ 에 덮어쓰기
5. git add -A && git commit -m "fix: quality pass" && git push
```

### 피드백 현황 (v31 기준)
- **마지막 피드백 완료**: 2026-09-25 (Steam Frame vs Steam Deck)
- **다음 피드백 대상**: 09-29 이후 발행되는 W37/W38 글들
- **W37/W38 final/ 수정 완료**: 026, 033, 034, 035, 036, 017, 037, 038, 039, 040, 041, 042, 043 (13개)
- **미발행 잔여**: 035~043 중 026 제외 8편 순차 발행 중

### slug 충돌 해결
```cmd
# 파일명 변경으로 slug 분리
rename 2026-09-10-04-pixel-pro.md 2026-09-10-pixel-11-vs-pixel-11-pro-camera-differences.md
git add -A && git commit -m "fix: resolve slug conflict" && git push
```

### Bing CTR 최적화 루틴
```
1. Bing Webmaster → Search Performance → Queries 탭 CSV 내보내기
2. 순위 1~5위인데 CTR 0% 키워드 파악
3. 해당 글 파일 업로드
4. Claude가 제목/excerpt 수정안 제공
5. 수정본 _posts/ 에 덮어쓰기 후 푸시
→ 효과: 1~2주 후 Bing Search Performance에서 CTR 변화 확인
```

### Search Console 색인 요청 루틴
```
1. Search Console → 색인 생성 안된 페이지 목록 확인
2. 페이지네이션(/page?/), 구버전 slug, sitemap:false 글 제외
3. 나머지 URL 하루 3~4개씩 수동 요청
4. Claude에게 목록 주면 텍스트 파일로 정리해드림
```

---

## 1. 현재 상태 요약

### 발행 현황
- `_posts/` 발행 완료: **66편+** (7/14~9/29)
- `final/` 발행 대기: W37/W38 나머지 8편 순차 발행 중
- 애드센스: **거절** (사유: 가치가 별로 없는 콘텐츠 + 복제된 콘텐츠)
- 수익화 목표: **Ezoic** (일 20~30명 organic 도달 시)
- Step 1 트리거: **스택 기반** (월요일 cron 제거 완료)
- posts.json: **66편+** 기록

### 최근 발행 이력 (9/10 이후)
| 날짜 | 제목 | 비고 |
|------|------|------|
| 09-13 | Galaxy Z Fold 8 vs Fold 7 Hinge Durability | ✅ |
| 09-14 | Why GTA VI Targets 30 FPS | ✅ 제목/카테고리/excerpt 수정 |
| 09-15 | Galaxy Z Fold 8 vs Flip 8 (실제 스펙) | ✅ |
| 09-16 | Pixel 11 vs Pixel 11 Pro Camera | ✅ |
| 09-17 | Nvidia DLSS 5 Explained | ✅ 제목 CTR 최적화 |
| 09-18 | How to Set Up Pixel 11 Pro | ✅ 제목/excerpt 버그 수정 |
| 09-19 | How to Enable Custom Chat Bubbles | ✅ 태그 수정 |
| 09-20 | Steam Frame vs Meta Quest 3 | ✅ |
| 09-21 | Pixel 11 Pro vs iPhone Duo | ✅ 실제 스펙 재작성 |
| 09-22 | Galaxy Z Fold 8 vs Flip 8: Which to Buy | ✅ |
| 09-23 | How to Set Up Valve Steam Frame for PC VR | ✅ |
| 09-24 | How to Transfer Android Passkeys | ✅ 태그 수정 |
| 09-25 | Steam Frame vs Steam Deck | ✅ |
| 09-29 | Elden Ring PC vs Console Performance | ✅ W37 첫 발행 |

---

## 2. 글쓰기 톤앤매너

### 핵심 원칙
Frontbuffer는 기술/게이밍 주제를 다루는 영어 블로그로, 독자는 특정 문제를 해결하거나 구매/사용 결정을 내리려는 실용적 목적의 방문자입니다.

### ① 서론: 문제 상황으로 즉시 진입
- **금지**: "has emerged as", "In this article, we will explore", "delves into" 등 AI 관용구
- **권장**: 독자가 실제로 맞닥뜨리는 상황이나 핵심 정보로 첫 문장 시작

### ② 사실 기반, 구체적 수치
- 모델명, 버전, 날짜, 수치를 문장 안에 자연스럽게 녹입니다.

### ③ 외부 링크: 각주 아닌 인라인
- 출처를 앵커 텍스트로 본문에 삽입합니다.

### ④ 결론: 실용적 takeaway
- 요약 반복 금지. 독자가 다음에 무엇을 해야 하는지 명확히 제시합니다.

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
boils down to / enduring appeal / paramount / vibrant / shed light on /
revolutionary / cutting-edge / innovative / pushing the boundaries /
remarkable / seamlessly / comprehensive / robust / testament to /
meticulous / commendable / highly anticipated / non-negotiable
```

### ⑦ Sources 품질 기준
- ✅ 공식 문서, 제조사 페이지, The Verge/Ars Technica/Android Authority/9to5Google
- ❌ YouTube, Reddit, eBay, Amazon, Game Rant, Fextralife, CNET, PhoneArena, GSMArena, TechRadar, Tom's Guide, SamMobile, Wikipedia, Gadgets360

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
  → 발행 여부: posts.json 기반 1차 + pipeline url 소문자 비교 2차 (v30)
  → _posts/ 발행 → posts.json 업데이트
  → og_generator.py (Unsplash + R2)
  → IndexNow 자동 제출 (Bing)
  → 스택 3편 이하 → Step 1 자동 트리거

Step 5 (금 UTC 15:00)
  step5_audit.py → 품질 감사 → Discord 알림
```

---

## 4. 이미지 시스템

- `og_generator.py` — Unsplash API + R2 업로드
- URL: `https://images.frontbuffer.net/posts/{slug}/og.png`
- OG 재생성: `.github/workflows/og_regenerate.yml` — 날짜 입력으로 수동 트리거

---

## 5. 수익화

### 애드센스
- **상태**: 거절 / **재신청 조건**: Google organic 일 10명+ / 참여시간 1분+ / 색인 40편+
- **예상 재신청**: 2027년 상반기 (현재 속도 기준)

### 현재 목표: Ezoic
- 조건: 일 20~30명 organic / 예상: 2027년 하반기

### 대안 (즉시 가능)
- **Impact.com 제휴** — 트래픽 조건 없음, 구매 결정 글(COMPARISON/GUIDE)에 제휴 링크 삽입

---

## 6. SEO 현황 (2026-09-29 기준)

### Google Analytics (8/31~9/27, 28일)
- 활성 사용자: **185명** / 일 평균 **6.6명**
- 참여시간: **20.3초** / Direct **78%**
- 실제 인간 유입 추정: 일 **3~4명** (봇 제외)

### 유입 소스
| 소스 | 사용자 | 비율 |
|------|--------|------|
| Direct | 145 | 78% |
| Bing organic | 11 | 6% |
| DuckDuckGo | 8 | 4% |
| Google organic | 6 | 3.2% |
| Ecosia | 5 | 2.7% |
| Copilot/Perplexity | 2 | 1% |

### Bing Webmaster (9/28 기준)
- Copilot 인용: **하루 100회+** (9/25 기준 125회, 16페이지)
- 총 키워드: 382개 / 일 평균 노출 45회 / 클릭 0.7회
- Backlinks: **dev.to 1개** (매우 부족)
- SEO 이슈: Title too long 3개 (high), Meta description too short 8개 (moderate)

### Bing CTR 최적화 완료 (9/29, 9개 글)
| 글 | 수정 내용 |
|----|----------|
| 07-31 Moonlight/Sunshine | 제목 + excerpt |
| 08-07 Z Flip 8 Cover Screen | 제목 + excerpt |
| 09-17 DLSS 5 | 제목 |
| 08-16 Fold 8 vs Fold 7 Camera | 제목 + GSMArena 제거 |
| 07-14 Steam Machine Overheating | 제목 + TechRadar/Wikipedia 제거 |
| 07-16 Samsung Health Backup | 제목 + Wikipedia 제거 |
| 07-18 Chrome MV2 Check | 제목 |
| 07-19 MV3 Alternatives | 제목 |
| 07-22 Samsung Health Transfer | 제목 + Gadgets360 제거 |

### Google Search Console (9/22 기준)
- 색인: **39편** / 색인 요청 10개 진행 중

---

## 7. 전망 로드맵

| Phase | 내용 | 예상 시점 |
|-------|------|---------|
| 1 | 색인 40편 달성 | 10월 초 ✅ 거의 완료 |
| 2 | Bing organic 안정화 + Copilot 클릭 전환 | 10~11월 |
| 3 | Google organic 첫 안정화 | 11월 |
| 4 | 애드센스 재신청 | 2027년 상반기 |
| 5 | Ezoic | 2027년 하반기 |

**병목**: Google organic 일 10명 (현재 0.21명) → 백링크 + 롱테일 키워드 선점이 유일한 레버

---

## 8. 백링크 루틴

| 요일 | 작업 |
|------|------|
| 월 | Quora 답변 1개 (링크 포함) |
| 화 | XDA 답변 1개 |
| 수 | Quora 답변 1개 |
| 목 | Dev.to 발행 (canonical 필수) |
| 금 | HN 제출 1개 |
| 토 | Reddit 워밍업 |

> ⚠️ 추석 연휴로 중단됨. 재개 필요.

---

## 9. 주요 파일

```
publish_one.py          — Step 4 발행 (v30: PENDING 소문자 비교 수정)
og_generator.py         — OG 이미지 생성 + R2
og_regenerate.yml       — OG 수동 재생성 워크플로우
research.py             — Step 1
research_gemini.py      — Step 2
write.py                — Step 3 글 생성
step5_audit.py          — 주간 품질 감사
config.json             — weekly_seeds
posts.json              — 발행 글 목록 (발행 여부 판단 소스)
content_pipeline.json   — 파이프라인 상태
```

---

## 10. 현재 이슈

### 🟡 진행 중
| # | 이슈 | 예정 |
|---|------|------|
| 1 | W37/W38 나머지 8편 발행 | 매일 UTC 14:00 자동 |
| 2 | Search Console 색인 요청 10개 | 3~4개씩 진행 |
| 3 | Title too long 3개 수정 | Bing SEO Analysis 확인 후 |
| 4 | Meta description too short 8개 | excerpt 보강 필요 |
| 5 | W40 Step 2 트리거 | CSV 푸시 후 수동 실행 |
| 6 | 백링크 루틴 재개 | 즉시 |
| 7 | Copilot 인용 → 클릭 전환 구조 개선 | 다음 대화 |
| 8 | Google photos storage 글 신규 작성 | W40~41 seeds 추가 |

### 🔧 버그 수정 완료
- publish_one.py v27 — front matter 중복
- publish_one.py v29 — pipeline 의존 → posts.json
- publish_one.py v30 — PENDING 대소문자 비교 버그
- og_regenerate.yml — OG 수동 재생성
- GTA VI 제목/카테고리/excerpt + OG
- Nintendo Switch YAML 버그
- 04-pixel-pro slug 충돌

### 중복 글 (sitemap:false 처리 완료)
08-02, 08-09, 08-10, 08-11, 08-26, 08-29, 08-31, 09-02

---

## 11. GitHub

```
https://github.com/baek2731/frontbuffer
Public (GitHub Pages Free 플랜)
```

---

## 12. 다음 대화 시작 시 보낼 파일

```
Frontbuffer_프로젝트_정리_v31.md   ← 항상
수정이 필요한 파일만               ← 이슈 발생 시
content_pipeline.json              ← pipeline 이슈 시
보고서_개요.csv                    ← GA 분석 시 (월 1회)
Bing CSV 파일들 (6개)              ← Bing 분석 시 (월 1회)
  - SearchPerformanceOverview
  - KeywordReport
  - AIPerformanceOverviewStats
  - AISearchQueriesReport
  - ReferringDomains
  - SEOAnalysisSummary
```

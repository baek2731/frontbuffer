# Frontbuffer 프로젝트 정리 v29
> 작성일: 2026-09-28

---

## 0. Claude 작업 지침

- **확인은 하되 "오늘 많이 했으니 쉬어요", "다음에 해요" 같은 말은 하지 말 것.** 작업 여부는 사용자가 결정합니다.
- **파일은 항상 전체 파일로 제공할 것.** 부분 수정 안내 금지.
- **푸시 코드는 항상 함께 제공할 것.**
- **한국어로만 소통할 것.**
- **말투: 항상 존댓말(~습니다 / ~입니다 / ~하세요 체)로 소통할 것.**
- **다운로드 경로: C:\Users\B\Downloads**

---

## 1. 현재 상태 요약

### 발행 현황
- `_posts/` 발행 완료: **65편+** (7/14~9/27)
- `final/` 발행 대기: W37/W38 수정본 정상화 진행 중
- 애드센스: **거절** (사유: 가치가 별로 없는 콘텐츠 + 복제된 콘텐츠)
- 수익화 목표: **Ezoic** (일 20~30명 organic 도달 시)
- Step 1 트리거: **스택 기반** (월요일 cron 제거 완료)
- posts.json: **65편+** 기록

### 주요 발행 이력 (9/10 이후 추가분)
| 날짜 | 제목 | 비고 |
|------|------|------|
| 09-13 | Galaxy Z Fold 8 vs Fold 7 Hinge Durability | ✅ AI 문체 수정 완료 |
| 09-14 | Why GTA VI Targets 30 FPS | ✅ 제목/카테고리/excerpt 수정 완료 |
| 09-15 | Galaxy Z Fold 8 vs Flip 8 (실제 스펙 기반) | ✅ 루머 기반 → 실제 스펙 재작성 |
| 09-16 | Pixel 11 vs Pixel 11 Pro Camera | ✅ 금지어/불량출처 수정 완료 |
| 09-17 | What is Nvidia DLSS 5 | ✅ 금지어 수정 완료 |
| 09-18 | How to Set Up Pixel 11 Pro | ✅ 제목/excerpt 버그 수정 완료 |
| 09-19 | How to Enable Custom Chat Bubbles in Google Messages | ✅ 태그 수정 완료 |
| 09-20 | Steam Frame vs Meta Quest 3 | ✅ Amazon 링크 제거 완료 |
| 09-21 | Pixel 11 Pro vs iPhone Duo | ✅ 루머 기반 → iPhone Duo 실제 스펙 재작성 |
| 09-22 | Galaxy Z Fold 8 vs Flip 8: Which to Buy | ✅ |
| 09-23 | How to Set Up Valve Steam Frame for PC VR | ✅ |
| 09-24 | How to Transfer Android Passkeys | ✅ 태그 수정 완료 |
| 09-25 | Steam Frame vs Steam Deck | ✅ |

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
- ❌ YouTube, Reddit, eBay, Amazon, Game Rant, Fextralife, CNET, PhoneArena, GSMArena, TechRadar, Tom's Guide, SamMobile

---

## 3. 파이프라인 전체 흐름

```
Step 1 (final/ 3편 이하 시 Step 4에서 자동 트리거 — 월요일 cron 제거됨)
  research.py
  → RSS 수집 + 락 파일 생성 (.step1_done)
  → Discord 알림

Step 2 (CSV 업로드 후 수동 트리거)
  research_gemini.py
  → weekly_seeds (config.json) 주입
  → content_pipeline.json 저장
  → Step 3 자동 트리거

Step 3 (Step 2 완료 후 자동)
  write.py → gemini_api.py → gemini_review_api.py
  → quality_check.py
  → final/{file_id}.md

Step 4 (매일 UTC 14:00 = 한국 밤 11시)
  publish_one.py
  → 발행 여부: posts.json 기반 판단 (v29 수정 — pipeline 의존 제거)
  → 기존 front matter 자동 제거 후 새 front matter 생성
  → Gemini SEO excerpt 자동 생성
  → _posts/ 발행
  → posts.json 업데이트
  → og_generator.py (Unsplash + R2)
  → IndexNow 자동 제출 (Bing)
  → 스택 3편 이하 → Step 1 자동 트리거

Step 5 (금 UTC 15:00)
  step5_audit.py → 품질 감사 → Discord 알림
  (HUB 타입 단어 수 검사 제외 적용됨)
```

---

## 4. 이미지 시스템

- `og_generator.py` — Unsplash API + R2 업로드
- URL: `https://images.frontbuffer.net/posts/{slug}/og.png`
- 버킷: `frontbuffer-images` / 도메인: `images.frontbuffer.net`
- OG 재생성 워크플로우: `.github/workflows/og_regenerate.yml` — 날짜 입력으로 수동 트리거 가능

---

## 5. 수익화

### 애드센스
- **신청일**: 2026-08-08
- **상태**: 거절 (가치가 별로 없는 콘텐츠 + 복제된 콘텐츠)
- **재신청 조건**: Google organic 일 10명+ / 참여시간 28일 평균 1분+ / 색인 40편+
- **예상 재신청**: 2026년 11월 말~12월

### 현재 목표: Ezoic
- 조건: 일 20~30명 organic 유입
- 예상 수익: 월 $30~80
- 예상 달성: 2027년 2~3월

### 거절 시 대안
1. Ezoic — 일 20명 이상
2. Impact.com 제휴 — 즉시 가능
3. 스폰서십 직접 컨택 — 일 200명 이상

---

## 6. SEO 현황 (2026-09-28 기준)

### Google Analytics 최신 (8/31~9/27, 28일)
- 활성 사용자: **185명** (일 평균 **6.6명** — 이전 3.6명 대비 +83%)
- 평균 참여 시간: **20.3초** (이전 16.97초 대비 개선)
- 이벤트 수: 761 (일 평균 27.2)
- ⚠️ Direct 비율 **78%** (이전 86%에서 감소 — 개선 추세)
- ⚠️ 중국 유입 증가 (Hangzhou 9명, Zhangjiajie 8명 등) — 실제 인간 트래픽 가능성 있음

### 유입 소스 (8/31~9/27, 첫 사용자 기준)
| 소스 | 사용자 | 비율 | 이전 대비 |
|------|--------|------|---------|
| Direct | 145 | 78% | ⬇️ -8%p |
| Bing organic | 11 | 6% | ⬆️ +4.4%p |
| DuckDuckGo organic | 8 | 4% | ⬇️ -1%p |
| Google organic | 6 | 3.2% | ⬆️ +0.9%p |
| Ecosia organic | 5 | 2.7% | 신규 |
| Copilot / Perplexity | 2 | 1% | 신규 |

> Bing organic이 4위→2위로 올라섰습니다. Copilot, Perplexity 유입도 시작됐습니다.

### 상위 콘텐츠 (8/31~9/27, 조회수 기준)
| 글 | 조회수 | 이탈률 |
|----|--------|--------|
| Steam Machine LED COMPARISON | 12 | 58% |
| Samsung Health Transfer GUIDE | 10 | 70% |
| Why GTA VI Targets 30 FPS | 10 | 67% |
| Google Messages 리디자인 EXPLAINER | 9 | 78% |
| Moonlight/Sunshine GUIDE | 9 | 89% |
| Galaxy Z Fold 8 배터리 GUIDE | 7 | 83% |
| Z Flip 8 커버스크린 GUIDE | 7 | 86% |
| uBlock Origin Lite MV3 | 7 | - |

### Google Search Console (9/22 기준)
- 색인: **39편** (발행 65편+)
- 미색인: 20편 (페이지네이션 4 / 구버전 slug 7 / 신규 미처리 9)
- 색인 요청 완료: 이전 14개 + 신규 10개 진행 중

### Bing Webmaster
- 9월 Bing organic 11명 — 전월 대비 큰 폭 상승
- impressions 안정적 상승 추세 유지

---

## 7. 전망 로드맵 (2026-09-28 재설계)

### 현실 진단

| 지표 | 현재 | 애드센스 재신청 기준 | 갭 |
|------|------|---------------------|-----|
| Google organic/일 | **0.21명** (6명/28일) | 10명/일 | **47배** (이전 125배에서 개선) |
| 참여시간 (28일 평균) | **20.3초** | 60초+ | **3배** |
| 색인 수 | **39편** | 40편+ | **1편** — 거의 달성 |

### Phase별 로드맵

#### Phase 1 — 색인 완성 (10월 초) ✅ 거의 완료
- 색인 39편 → 40편: Search Console 신규 요청 10개 중 1개만 색인되면 달성
- **예상 달성**: 10월 초

#### Phase 2 — Bing/대안 검색엔진 organic 안정화 (10~11월)
- Bing organic이 빠르게 성장 중 (9월 11명, 일 0.39명)
- Bing 순위 안정화 → Google보다 먼저 organic 수치 개선 가능
- Ecosia, Copilot, Perplexity 유입도 모니터링 대상
- **예상 달성**: 10월 말

#### Phase 3 — Google organic 첫 안정화 (11월)
- 색인 확대 + 백링크 루틴 → 롱테일 키워드 순위 진입
- Steam Frame 클러스터 (9월 출시 직후 4편) 가 롱테일 유입 가능성 최고
- Googlebook 클러스터 (9월 21일 출시 직후) 도 경쟁 낮은 신규 주제
- **예상 달성**: 11월 중

#### Phase 4 — 애드센스 재신청 (11월 말~12월)
- Google organic 일 10명 + 참여시간 60초+ 동시 달성 필요
- organic 비중이 오르면 참여시간은 자동으로 따라옴
- **예상 재신청**: 2026년 11월 말~12월

#### Phase 5 — Ezoic (2027년 1분기)
- **예상 달성**: 2027년 2~3월

### 병목 우선순위

1. **백링크 루틴 재개** — 추석 연휴로 중단됨. 즉시 재개 필요. Google organic의 유일한 레버.
2. **Steam Frame / Googlebook 클러스터** — 경쟁 낮은 신규 주제. 추가 글로 클러스터 완성.
3. **참여시간 개선** — organic 비중 확대가 유일한 경로. 콘텐츠 수정보다 유입 구조 개선.

---

## 8. 백링크 루틴

### 계정 현황
| 사이트 | 상태 | 링크 가능 |
|--------|------|---------|
| Quora | 활성 | 즉시 |
| Dev.to | 활성 | 즉시 |
| Hacker News | 활성 | 즉시 |
| XDA Developers | 워밍업 완료 | 링크 포함 가능 |
| Reddit | 워밍업 중 | 카르마 쌓인 후 |

### 요일별 정규 루틴
| 요일 | 작업 |
|------|------|
| 월 | Quora 답변 1개 (링크 포함) |
| 화 | XDA 답변 1개 (링크 포함) |
| 수 | Quora 답변 1개 (링크 포함) |
| 목 | Dev.to 글 발행 (canonical 필수) |
| 금 | HN 제출 1개 |
| 토 | Reddit 워밍업 |
| 일 | 휴식 or 보완 |

---

## 9. 현재 이슈

### 🟡 진행 중
| # | 이슈 | 예정 |
|---|------|------|
| 1 | 애드센스 재신청 | organic 개선 후 11~12월 |
| 2 | W37/W38 final/ 파일 발행 정상화 | publish_one.py 수정 후 모니터링 중 |
| 3 | Google organic 유입 개선 | 백링크 루틴 재개 필요 |
| 4 | Search Console 색인 요청 10개 | 3~4개씩 진행 중 |

### 🔧 버그 수정 완료
- publish_one.py — front matter 중복 생성 버그 수정 (v27)
- publish_one.py — 발행 여부 판단 로직 개선 (v29): pipeline 의존 → posts.json 기반
- content_pipeline.json — 잘못 등록된 published 항목 반복 제거
- step1_research.yml — 월요일 cron 제거, 스택 기반 트리거로 전환
- step5_audit.py — HUB 타입 단어 수 검사 예외 처리
- og_regenerate.yml — OG 이미지 수동 재생성 워크플로우 추가
- 2026-09-14 GTA VI — 제목/카테고리/excerpt 수정, OG 이미지 재생성
- 2026-08-31 Nintendo Switch — YAML 이스케이프 버그 수정
- 2026-09-10/18 04-pixel-pro — slug 충돌 해결 (파일명 분리)

### 중복 글 처리 완료
| 글 | 처리 |
|---|---|
| 08-02 Galaxy Fold EXPLAINER | ✅ sitemap:false + canonical |
| 08-09 Android Auto GUIDE | ✅ sitemap:false + canonical |
| 08-10 Silicon-Carbon EXPLAINER | ✅ sitemap:false + canonical |
| 08-11 Android Auto COMPARISON | ✅ sitemap:false + canonical |
| 08-26 Android Desktop Mode | ✅ sitemap:false + canonical |
| 08-29 Fold 8 vs Flip 8 | ✅ sitemap:false + canonical |
| 08-31 Nintendo Switch | ✅ sitemap:false + canonical |
| 09-02 Samsung Health Backup | ✅ sitemap:false + canonical |

### 🟢 완료
- Cloudflare Bot Fight Mode 활성화
- Cloudflare Mixed Purpose Crawlers — "continue to be allowed" 설정
- GA4 내부 트래픽 필터 활성화
- 전체 글 품질 점검 (9/10 기준 52편 + 9/10 이후 13편 추가)
- W37/W38 final/ 파일 13개 품질 수정 (금지어, 불량출처, 차단패턴 제거)
- 044 손상 파일 삭제
- OG 재생성 워크플로우 추가 및 GTA VI OG 재생성

---

## 10. 주요 파일

```
publish_one.py          — Step 4 발행 (posts.json 기반 발행 여부 판단 — v29)
og_generator.py         — OG 이미지 생성 + R2 업로드
og_regenerate.yml       — OG 이미지 수동 재생성 워크플로우 (날짜 입력)
research.py             — Step 1 RSS 수집
research_gemini.py      — Step 2 Gemini 기획
seed_inject.py          — Step 2-1 개별 주제 추가
write.py                — Gemini 프롬프트 + 글 생성
step5_audit.py          — 주간 품질 감사 (HUB 예외 처리 완료)
step1_research.yml      — Step 1 트리거 (스택 기반, cron 제거)
config.json             — weekly_seeds 설정
posts.json              — 발행 글 목록 (발행 여부 판단 소스)
content_pipeline.json   — 파이프라인 상태
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
Frontbuffer_프로젝트_정리_v29.md   ← 항상
수정이 필요한 파일만               ← 이슈 발생 시
content_pipeline.json              ← pipeline 이슈 시
```

# Frontbuffer 프로젝트 정리 v27
> 작성일: 2026-09-10

---

## 0. Claude 작업 지침

- **확인은 하되 "오늘 많이 했으니 쉬어요", "다음에 해요" 같은 말은 하지 말 것.** 작업 여부는 사용자가 결정한다.
- **파일은 항상 전체 파일로 제공할 것.** 부분 수정 안내 금지.
- **푸시 코드는 항상 함께 제공할 것.**
- **한국어로만 소통할 것.**
- **다운로드 경로: C:\Users\B\Downloads**

---

## 1. 현재 상태 요약

### 발행 현황
- `_posts/` 발행 완료: **52편** (7/14~9/10)
- `final/` 발행 대기: **확인 필요** (W35 글 발행 진행 중)
- 애드센스: **거절** (사유: 가치가 별로 없는 콘텐츠 + 복제된 콘텐츠)
- 수익화 목표: **Ezoic** (일 20~30명 organic 도달 시)
- Step 1 트리거: **스택 기반** (월요일 cron 제거 완료)
- W35 파이프라인: Step 2/3 완료, 발행 진행 중
- posts.json: **52편+** 기록

### 발행된 글 목록 (_posts/)
| 날짜 | 제목 | 비고 |
|------|------|------|
| 07-14 | Steam Machine Overheating GUIDE | ✅ |
| 07-15 | Steam Machine LED COMPARISON | ✅ |
| 07-16 | Samsung Health Backup GUIDE | ✅ |
| 07-17 | Samsung Health vs Health Connect | ✅ |
| 07-18 | Chrome MV2 Check GUIDE | ✅ |
| 07-19 | MV3 Alternatives LISTICLE | ✅ 제목 수정 완료 |
| 07-20 | Chrome MV3 EXPLAINER | ✅ 제목 수정 완료 |
| 07-20 | Chrome MV2 HUB | ✅ 제목 수정 완료 |
| 07-21 | Android Ecosystem COMPARISON | ✅ |
| 07-21 | Android Ecosystem EXPLAINER | ✅ |
| 07-22 | Samsung Health Transfer GUIDE | ✅ 제목 수정 완료 |
| 07-23 | Fallout Remaster COMPARISON | ✅ AI 문체 수정 완료 |
| 07-24 | Fallout NV Endings EXPLAINER | ✅ AI 문체 수정 완료 |
| 07-26 | Fallout Modding GUIDE | ✅ |
| 07-27 | AYANEO vs Steam Deck COMPARISON | ✅ |
| 07-28 | Portable Gaming EXPLAINER | ✅ |
| 07-29 | Samsung Health HUB | ✅ |
| 07-30 | Steam Machine HUB | ✅ |
| 07-31 | Moonlight/Sunshine GUIDE | ✅ AI 문체 수정 완료 |
| 08-01 | Galaxy Fold COMPARISON | ✅ AI 문체 수정 완료 |
| 08-02 | Galaxy Fold EXPLAINER | ✅ sitemap:false + canonical |
| 08-03 | Fold Battery GUIDE | ✅ |
| 08-04 | Z Fold/Flip COMPARISON | ✅ |
| 08-05 | Silicon-Carbon EXPLAINER | ✅ |
| 08-07 | Z Flip Cover Screen GUIDE | ✅ |
| 08-08 | Android Auto COMPARISON | ✅ |
| 08-09 | Android Auto GUIDE | ✅ sitemap:false + canonical |
| 08-10 | Silicon-Carbon EXPLAINER | ✅ sitemap:false + canonical |
| 08-11 | Android Auto Adapter | ✅ sitemap:false + canonical |
| 08-12 | Pixel Launcher COMPARISON | ✅ |
| 08-13 | Physical vs Digital COMPARISON | ✅ |
| 08-14 | Android Auto Fix GUIDE | ✅ |
| 08-15 | Game Library GUIDE | ✅ |
| 08-16 | Fold 8 vs Fold 7 Camera | ✅ AI 문체 수정 완료 |
| 08-17 | Fold 8 First 5 Things | ✅ AI 문체 수정 완료 |
| 08-19 | Assistant vs Gemini | ✅ |
| 08-20 | VRAM GUIDE | ✅ |
| 08-25 | Quick Settings GUIDE | ✅ front matter 수정 완료 |
| 08-26 | Android 16 Desktop Mode | ✅ sitemap:false + canonical |
| 08-27 | Desktop Mode vs DeX | ✅ AI 문체 수정 완료 |
| 08-28 | App Lock COMPARISON | ✅ |
| 08-29 | Fold 8 vs Flip 8 | ✅ sitemap:false + canonical + AI 문체 |
| 08-30 | Fold 8 Ultra vs S26 Ultra | ✅ |
| 08-31 | Nintendo Switch 2 microSD | ✅ sitemap:false + canonical |
| 09-01 | Pixel QPR2 Beta GUIDE | ✅ |
| 09-02 | Samsung Health Backup GUIDE | ✅ sitemap:false + canonical |
| 09-03 | Pixel 11 Pro Fold COMPARISON | ✅ |
| 09-04 | Fold 8 vs Flip 8 COMPARISON | ✅ AI 문체 수정 완료 |
| 09-05 | Nintendo Switch 2 Storage GUIDE | ✅ |
| 09-06 | RTX 50 Series GPU GUIDE | ✅ |
| 09-07 | Google Messages EXPLAINER | ✅ front matter 수정 완료 |
| 09-10 | Pixel 11 vs Pixel 11 Pro | ✅ front matter 수정 완료 |

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
boils down to / enduring appeal / paramount / vibrant / shed light on /
revolutionary / cutting-edge / innovative / pushing the boundaries /
remarkable / seamlessly / comprehensive / robust / testament to /
meticulous / commendable / highly anticipated / non-negotiable
```

### ⑦ Sources 품질 기준
- ✅ 공식 문서, 제조사 페이지, The Verge/Ars Technica/Android Authority/9to5Google
- ❌ YouTube, Reddit, eBay, Amazon, Game Rant, Fextralife, CNET, PhoneArena

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
  → 기존 front matter 자동 제거 후 새 front matter 생성 (v27 버그 수정 완료)
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

---

## 5. 수익화

### 애드센스
- **신청일**: 2026-08-08
- **상태**: 거절 (가치가 별로 없는 콘텐츠 + 복제된 콘텐츠)
- **재신청 조건**: Google organic 일 10명+ / 참여시간 28일 평균 1분+ / 색인 40편+
- **예상 재신청**: 10~11월

### 현재 목표: Ezoic
- 조건: 일 20~30명 organic 유입
- 예상 수익: 월 $30~80
- 예상 달성: 2027년 1~2월

### 거절 시 대안
1. Ezoic — 일 20명 이상
2. Impact.com 제휴 — 즉시 가능
3. 스폰서십 직접 컨택 — 일 200명 이상

---

## 6. SEO 현황 (2026-09-10 기준)

### Google Analytics (9/1~9/10, 10일)
- 활성 사용자: 53명 (일 평균 5.3명)
- 평균 참여 시간: **34초** (이전 11~12초 → 3배 향상)
- 상위 페이지: Moonlight/Sunshine GUIDE (9조회), Steam Machine LED (5조회)
- 유입 소스: Direct 45 / DuckDuckGo 3 / Bing 2 / Copilot 1 / Ecosia 1
- Google organic: 0 (여전히 병목)

### Google Search Console
- 색인: **26편** (발행 52편)
- 미색인: 30편 (발견됨 24 / 리디렉션 3 / robots.txt 1 / 크롤링 1 / 리디렉션 오류 1)
- robots.txt 차단: /tags/ (의도적, 정상)
- 리디렉션 오류: trailing slash 문제 (정상 동작)

### Bing Webmaster (7/22~9/7)
- Total Clicks: 5 / Total Impressions: 최고 29회 (9/7)
- 상승 추세 지속 중
- 9월 들어 impressions 15~29 안정적 유지

---

## 7. 백링크 루틴

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

## 8. 현재 이슈

### 🟡 진행 중
| # | 이슈 | 예정 |
|---|------|------|
| 1 | 애드센스 재신청 | organic 개선 후 10~11월 |
| 2 | W35 발행 진행 중 | 자동 발행 중 |
| 3 | Google organic 유입 개선 | 백링크 루틴 지속 |

### 🔧 버그 수정 완료
- publish_one.py — 기존 front matter 중복 생성 버그 수정 (v27)
- content_pipeline.json — 잘못 등록된 published 항목 반복 제거
- step1_research.yml — 월요일 cron 제거, 스택 기반 트리거로 전환
- step5_audit.py — HUB 타입 단어 수 검사 예외 처리

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
- 전체 52편 글 품질 점검 완료 (AI 문체 수정, front matter 수정)
- publish_one.py front matter 중복 버그 수정
- Jekyll workflow_run 트리거 추가
- robots.txt 확장 (py/json/md/bat 차단)
- Bing CTR 최적화 (07-19, 07-22, 07-20 제목/excerpt 수정)
- W34 seeds 입력 완료 (Samsung Health 3개 + GTA VI + Pixel 11 Pro)

---

## 9. W34 weekly_seeds (config.json 입력 완료)

1. `how to export Samsung Health data to share with a doctor or medical professional`
2. `Samsung Health vs Google Health Connect which app should you use in 2026`
3. `how to recover missing Samsung Health data after switching to a new phone`
4. `GTA VI PC release date and system requirements what we know in 2026`
5. `Google Pixel 11 Pro vs Samsung Galaxy S26 Ultra camera and AI features comparison 2026`

---

## 10. 주요 파일

```
publish_one.py          — Step 4 발행 (front matter 중복 버그 수정 완료)
og_generator.py         — OG 이미지 생성 + R2 업로드
research.py             — Step 1 RSS 수집
research_gemini.py      — Step 2 Gemini 기획
seed_inject.py          — Step 2-1 개별 주제 추가
write.py                — Gemini 프롬프트 + 글 생성
step5_audit.py          — 주간 품질 감사 (HUB 예외 처리 완료)
step1_research.yml      — Step 1 트리거 (스택 기반, cron 제거)
config.json             — weekly_seeds 설정
posts.json              — 발행 글 목록
content_pipeline.json   — 파이프라인 상태 (published 정확성 중요)
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
Frontbuffer_프로젝트_정리_v27.md   ← 항상
수정이 필요한 파일만               ← 이슈 발생 시
content_pipeline.json              ← pipeline 이슈 시
```

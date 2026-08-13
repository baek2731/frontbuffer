# Frontbuffer 프로젝트 정리 v23
> 작성일: 2026-08-13

---

## 1. 현재 상태 요약

### 발행 현황
- `_posts/` 발행 완료: **28편** (7/14~8/12)
- `final/` 발행 대기: **13편** (W32 정리 완료, 8/13~8/25 발행 예정)
- 애드센스: **검토 중** (2026-08-08 신청, ads.txt 추가 완료)
- Step 1 자동 트리거: **3편 이하** 시 자동 실행
- W32 파이프라인: Step 2/3 완료, final/ 13편 대기 중
- posts.json: **31편** 기록 (publish_one.py 자동 업데이트)
- W31: **스킵** (W32로 바로 진행)
- W33: weekly_seeds 입력 후 Step 2 예정

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
| 08-02 | Galaxy Fold | EXPLAINER | /tech/01-galaxy-fold_explainer/ |
| 08-03 | Galaxy Fold | GUIDE | /tech/01-galaxy-fold_guide/ |
| 08-04 | Galaxy Z Flip | COMPARISON | /tech/samsung-galaxy-z-foldflip-series_comparison/ |
| 08-05 | Galaxy Z Flip | EXPLAINER | /tech/samsung-galaxy-z-foldflip-series_explainer/ |
| 08-07 | Galaxy Z Flip | GUIDE | /tech/samsung-galaxy-z-foldflip-series_guide/ |
| 08-08 | Android Auto | COMPARISON | /tech/06-android-auto_comparison/ |
| 08-09 | Android Auto | GUIDE | /tech/06-android-auto_guide/ |
| 08-10 | Galaxy Fold | EXPLAINER | /tech/the-promise-of-silicon-carbon-batteries-and-samsungs-strateg/ |
| 08-11 | Android Auto | COMPARISON | /tech/best-wireless-android-auto-adapter-for-older-cars-comparison/ |
| 08-12 | Android Ecosystem | COMPARISON | /tech/google-pixel-launcher-vs-third-party-android-launchers-featu/ |

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
it is essential/crucial to / solidify X's position at the forefront
```

### ⑦ Sources 품질 기준
- ✅ 공식 문서, 제조사 페이지, The Verge/Ars Technica/Android Authority
- ❌ YouTube, Reddit, eBay, Amazon

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

### 거절 시 대안
1. Impact.com 제휴 (Best Buy, Newegg 등)
2. 트래픽 일 50명 이상 시 Ezoic 시도
3. 트래픽 일 200명 이상 시 스폰서십 직접 컨택

---

## 6. SEO 현황 (2026-08-13 기준)

### Google Search Console
- 색인: 17편 (발행 28편)
- 발견됨-색인미생성: 24편 (크롤 예산 부족)
- 수동 색인 요청: 7편 완료
- sitemap: 정리 완료 (research_data 제거, tags/categories 제외)

### Bing Webmaster
- Indexed URLs: 16개
- Impressions: 65 (상승 중)
- Clicks: 2
- URL Submission: 31개 제출 완료
- 경고: 메타 디스크립션 → excerpt 수정 완료 (반영 대기)

---

## 7. 백링크 루틴

### 계정 현황
| 사이트 | 계정 | 상태 |
|--------|------|------|
| Quora | FrontBuffer | 활성 (답변 10개+, 247 views) |
| Dev.to | Frontbuffer Editorial | 활성 (Chrome MV3 글 발행) |
| Hacker News | FrontBuffer_FB | 활성 (Chrome MV3 제출) |
| XDA Developers | Frontbuffer | 생성 완료 (워밍업 중) |
| Product Hunt | buffer_front | 8/12 론칭 완료 |
| tldr.tech | - | 이메일 제보 완료 |

### 일일 루틴 (15~20분)

**매일:**
- Quora 1~2개 답변
  - 검색: samsung health, chrome manifest, galaxy fold, android auto
  - 링크는 3~4개 답변 중 1개에만

**주 1~2회:**
- Dev.to 글 발행 (canonical URL 필수)
- Hacker News 제출 (ET 오전 9~11시 = 한국 밤 10시~자정)

**XDA (워밍업 중):**
- 링크 없이 순수 답변 먼저 3~5개
- 1주 후 링크 포함 답변 시작

### 사이트별 주의사항
```
Quora: 하루 2개 이상 링크 포함 금지, 크레딧: Tech Writer & Editor at Frontbuffer
Dev.to: canonical URL 필수, 태그: chrome/webdev/javascript/security/android
HN: 같은 도메인 연속 제출 금지, ET 오전 9~11시 타이밍
XDA: 포럼 답변 방식, Galaxy Fold/Android Auto/Android 생태계
```

### Dev.to 발행 현황
| 날짜 | 제목 | 연결 글 |
|------|------|---------|
| 08-11 | Chrome Manifest V2 Is Gone After August 31 | /tech/google-chrome-manifest-v2-migration_HUB/ |

---

## 8. 현재 이슈

### 🟡 진행 중
| # | 이슈 | 예정 |
|---|------|------|
| 1 | 애드센스 결과 대기 | 8/22~9/5 |
| 2 | XDA 워밍업 (링크 없이 답변 3~5개) | 이번 주 |
| 3 | W33 weekly_seeds 입력 후 Step 2 | 다음 주 |
| 4 | Reddit 워밍업 (카르마 쌓기) | 지속 |
| 5 | Bing excerpt 수정 반영 대기 | 3~7일 |

### 🟢 완료
- og_generator.py og.png + overlay_filter: 0 수정
- step3_write.yml file_id 전달 + break→continue + write.py done
- research.py 락 파일 (Step1 중복 방지)
- seed_inject.py + step2_1_seed_inject.yml (Step 2-1)
- weekly_seeds 시드 주입
- publish_one.py URL 슬러그 제목 기반
- publish_one.py posts.json 자동 업데이트
- publish_one.py Gemini SEO excerpt 자동 생성
- 기존 28편 SEO excerpt 수동 수정 완료
- sitemap 정리 (research_data 제거)
- ads.txt 추가
- Bing URL Submission 31개
- Dev.to/HN/XDA/Product Hunt/tldr.tech 계정 및 활동
- Quora 답변 10개+
- step4_publish.yml Step1 트리거 3편으로 변경
- step5_audit.py regex 버그 수정
- W31 스킵 → W32 직행
- W32 Step 2/3 완료 (13편 final/ 대기)

---

## 9. 주요 파일

```
publish_one.py          — Step 4 발행 (Gemini SEO excerpt 포함)
og_generator.py         — OG 이미지 생성 + R2 업로드
research.py             — Step 1 RSS 수집 (락 파일 포함)
research_gemini.py      — Step 2 Gemini 기획 (weekly_seeds 주입)
seed_inject.py          — Step 2-1 개별 주제 추가
write.py                — Gemini 프롬프트 + 글 생성
gemini_api.py           — 초안 생성
gemini_review_api.py    — 팩트체크 + 최종본
step5_audit.py          — 주간 품질 감사
config.json             — weekly_seeds 설정
posts.json              — 발행 글 목록 (31편)
set_env.bat             — 로컬 환경변수
.github/workflows/      — GitHub Actions
```

---

## 10. GitHub

```
https://github.com/baek2731/frontbuffer
Public (GitHub Pages Free 플랜)
```

---

## 11. 다음 대화 시작 시 보낼 파일

```
Frontbuffer_프로젝트_정리_v23.md  ← 항상
content_pipeline.json              ← Step 2/3 완료 후
수정이 필요한 파일만               ← 이슈 발생 시
```

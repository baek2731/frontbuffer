# Frontbuffer 프로젝트 정리 v22
> 작성일: 2026-08-09

---

## 1. 현재 상태 요약

### 발행 현황
- `_posts/` 발행 완료: **26편** (W29 + W30 순차 발행 중)
- `final/` 발행 대기: **약 7편** (W30 잔여)
- 애드센스: **신청 완료** (2026-08-08 21:15, 검토 중)
- Step 1 자동 트리거: **완료** (스택 10편 이하 시 자동 실행)
- W31 리서치: Step 1 완료, CSV 업로드 → Step 2 대기 중

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

---

## 2. 글쓰기 톤앤매너

### 핵심 원칙
Frontbuffer는 기술/게이밍 주제를 다루는 영어 블로그로, 독자는 특정 문제를 해결하거나 구매/사용 결정을 내리려는 실용적 목적의 방문자다. 모든 글은 아래 원칙을 따른다.

### ① 서론: 문제 상황으로 즉시 진입
- **금지**: "X has emerged as a significant player", "In this article, we will explore", "delves into", "it's worth noting" 등 AI 관용구
- **권장**: 독자가 실제로 맞닥뜨리는 상황이나 핵심 정보의 한계/맥락으로 첫 문장 시작

### ② 사실 기반, 구체적 수치
- 모델명, 버전, 날짜, 수치를 문장 안에 자연스럽게 녹임
- 수치는 출처와 함께 인라인 링크로 처리

### ③ 외부 링크: 각주 아닌 인라인
- 출처를 별도 footnote가 아닌 앵커 텍스트로 본문에 삽입
- Sources 섹션은 별도 유지

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
has emerged as / has become a significant / it's worth noting /
in conclusion, it is clear that / in today's world /
this article aims to / let's dive into / it goes without saying /
solidify X's position at the forefront / underscores commitment to innovation /
The Evolving Landscape of X / Navigating the X / The Future of X
```

### ⑦ Sources 품질 기준
- ✅ 공식 문서, 제조사 페이지, The Verge/Ars Technica/Android Authority 등
- ❌ YouTube, Reddit, eBay, Amazon — Sources 목록에서 제거
- ❌ 확인 불가한 URL 제거

---

## 3. 파이프라인 전체 흐름

```
Step 1 (final/ 10편 이하 시 Step 4에서 자동 트리거)
  research.py → RSS 수집 → Discord "CSV 올려주세요"

Step 2 (CSV 업로드 후 수동 트리거)
  research_gemini.py → content_pipeline.json 저장
  → Step 3 자동 트리거

Step 3 (Step 2 완료 후 자동)
  write.py → gemini_api.py → gemini_review_api.py
  → quality_check.py (R5: 발행 불가 패턴 감지)
  → final/{file_id}.md

Step 4 (매일 UTC 14:00, 주말 포함)
  publish_one.py
    → BLOCK_PATTERNS 감지 시 발행 차단 + Discord 알림
    → hub_ready() True인 HUB → 최상위 발행 (order = hub_num-10000)
    → 일반 스포크 → 번호 순
    → hub_ready() False인 HUB → 맨 뒤 대기 (order = 99000+hub_num)
    → 발행 후 og_generator.py 자동 실행 (Unsplash + R2 업로드)
    → IndexNow 자동 제출 (Bing)
    → 스택 10편 이하 → Step 1 자동 트리거

Step 5 (금 UTC 15:00, 자동)
  step5_audit.py → 품질 감사 → Discord 알림
```

---

## 4. 이미지 시스템

### Unsplash + Cloudflare R2
- `og_generator.py` — Unsplash API로 이미지 자동 검색 + R2 업로드
- Step 4 발행 시 자동 실행
- 이미지 URL: `https://images.frontbuffer.net/posts/{slug}/og.png`
- 글 상단 header: `og.png` 사용 (`overlay_filter: 0`)
- 중복 방지: `social_output/.used_unsplash_ids.json`에 사용한 photo ID 저장
- 품질 검증: 밝기 10~140, 색상 분산 체크
- Unsplash API: `color=black` 필터로 어두운 이미지만 가져옴

### R2 설정
- 버킷: `frontbuffer-images`
- 도메인: `images.frontbuffer.net`
- GitHub Secrets: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`

### 로컬 재생성 명령어
```cmd
cd C:\Users\B\Projects\blogauto2
set_env.bat
rmdir /s /q social_output
python og_generator.py --all
git add social_output/ _posts/
git commit -m "fix: 이미지 재생성"
git push
```

---

## 5. 애드센스

- **신청일**: 2026-08-08 21:15
- **상태**: 검토 중 (수일~2주 소요)
- **성공 가능성**: 65~70%
- **예상 반영일**: 8/15~8/22
- **거절 시**: 2주 후 재신청 (편수/트래픽 증가 후)

---

## 6. SEO 현황 (2026-08-08 기준)

### Google Search Console
- 색인: 17페이지 / 발행: 26편
- Google Organic 유입: 일 1~5명 수준
- sitemap: 45페이지 발견 (정상)

### Bing Webmaster
- 색인: 2페이지 (IndexNow 제출 완료)
- 키워드: Samsung Health 관련 2~3위, Chrome MV2 5~9위
- IndexNow: step4_publish.yml에 자동 제출 로직 포함

---

## 7. 현재 남은 이슈

### 🟡 추후 처리
| # | 이슈 | 파일 |
|---|------|------|
| 1 | Android/Fallout HUB 없음 | 다음 Step 2 때 HUB 타입 추가 |
| 2 | W31 CSV 업로드 → Step 2 실행 필요 | 8월 중순 전 |
| 3 | 이미지 전체 재검토 (색상/관련성) | 수동 |
| 4 | Quora/Reddit 활동 지속 | 수동 |
| 5 | 애드센스 승인 후 광고 배치 설정 | 승인 후 |

### 🟢 완료
- publish_one.py HUB ready order 버그 수정
- 톤앤매너 가이드 문서화
- HUB permalink `_hub` 제거
- Step 4 주말 발행 추가
- Step 1 자동 트리거 (스택 10편 이하)
- IndexNow 자동 제출
- Unsplash + R2 이미지 자동화
- 기존 26편 이미지 소급 적용
- write.py 프롬프트 품질 강화 (금지 패턴 확장, Sources 기준)
- quality_check.py R5 발행 불가 패턴 추가
- publish_one.py 발행 차단 로직 추가
- step5_audit.py 정규식 버그 수정
- 애드센스 코드 삽입 (_includes/head/custom.html)
- adsense_audit.py 품질 검사 스크립트
- 발행 전 품질 감사 완료 (YouTube 출처 제거, 숫자 태그 제거)
- publish_one.py 숫자 태그 필터링 추가

---

## 8. 주요 파일 위치

```
publish_one.py          — Step 4 발행 스크립트
og_generator.py         — OG 이미지 생성 + R2 업로드
set_env.bat             — 로컬 환경변수 설정 (gitignore)
adsense_audit.py        — 애드센스 신청 전 품질 검사
write.py                — Gemini 프롬프트 + 글 생성
quality_check.py        — Step 3 품질 체크
.github/workflows/      — GitHub Actions 워크플로우
_includes/head/custom.html — 애드센스 코드
```

---

## 9. GitHub 리포

```
https://github.com/baek2731/frontbuffer
현재 public (Free 플랜 — GitHub Pages 때문에 public 유지)
Private 전환: Pro 플랜($4/월) 필요 → 애드센스 수익 후 고려
```

---

## 10. 다음 대화 시작 시 보낼 파일

```
Frontbuffer_프로젝트_정리_v22.md  ← 항상
content_pipeline.json              ← Step 2/3 완료 후
수정이 필요한 파일만               ← 이슈 발생 시
```

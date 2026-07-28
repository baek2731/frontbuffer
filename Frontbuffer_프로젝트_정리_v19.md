# Frontbuffer 프로젝트 정리 v19
> 작성일: 2026-07-28

---

## 1. 현재 상태 요약

### 발행 현황
- `_posts/` 발행 완료: **15편** (오늘 portable-gaming_COMPARISON 추가)
- `final/` 발행 대기: **8편**
- 애드센스 목표: 20편 → 현재 15편 (5편 부족)

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

### final/ 발행 대기 (8편, 알파벳 순 발행)
```
portable-gaming_EXPLAINER.md
portable-gaming_GUIDE.md
samsung-health-data-ecosystem_COMPARISON.md
samsung-health-data-ecosystem_GUIDE.md
samsung-health-data-ecosystem_HUB.md
steam-machine-hardware-management_COMPARISON.md
steam-machine-hardware-management_GUIDE.md
steam-machine-hardware-management_HUB.md
```

---

## 2. 오늘 완료한 작업 (2026-07-28)

### 코드 정비 (전체 파이프라인 재설계)

#### ① folder_id + week_tag + publish_order 파일명 체계 (slug 불일치 근본 해결)
- **문제**: cluster_name 기반 slug가 각 단계마다 달라서 파일을 못 찾음
- **해결**: `get_file_id()` 함수 추가
  ```
  파일명 형식: {order:03d}_{week_tag}_{folder_id}_{CT}
  예시: 001_2026-W30_05-android-auto_GUIDE
  ```
- **수정 파일**: `write.py`, `gemini_api.py`, `gemini_review_api.py`, `step3_write.yml`

#### ② publish_order 기반 FIFO (발행 순서 Step 2에서 결정)
- **문제**: 알파벳 순 발행이 의도한 순서를 보장 못함
- **해결**: Step 2에서 Grade/트렌드/타입 기준으로 정렬 후 publish_order 부여
  ```
  정렬 기준:
    1순위: Grade A → B
    2순위: RISING > STABLE > FALLING
    3순위: COMPARISON > EXPLAINER > GUIDE > LISTICLE > HUB (맨 마지막)
  ```
- **수정 파일**: `research_gemini.py`, `pipeline.py`, `publish_one.py`

#### ③ hub_keyword fallback (소스 수집 실패 시 cluster_name 재시도)
- **문제**: hub_keyword가 cluster_name과 무관하게 생성돼 소스 수집 실패
- **해결**: 소스 수집 전부 실패 시 cluster_name으로 자동 재시도
- **수정 파일**: `write.py`

#### ④ 중복 클러스터 자동 필터 (folder 기준)
- **문제**: Step 2마다 같은 folder에 클러스터 여러 개 생성
- **해결**: `dedup_by_folder()` — 같은 folder+content_type 조합 중 Grade 최고 1개만 유지
- **수정 파일**: `research_gemini.py`

#### ⑤ Step 2→3 자동 연쇄
- **문제**: workflow_run이 수동 dispatch를 감지 못함
- **해결**: step2_plan.yml에 github-script dispatch 추가
- **수정 파일**: `step2_plan.yml`

#### ⑥ published URL 정상화
- **문제**: content_pipeline.json의 published[] URL이 /drafts/ 상태
- **해결**: posts.json 기준으로 8개 URL 실제 URL로 교체

#### ⑦ venv/ .gitignore 추가
- venv/, __pycache__/, *.pyc, drafts/, prompts/ 추가

#### ⑧ Samsung Health backup 글 front matter 수정
- \--- 백슬래시, ## layout 오류 수정
- permalink 추가

#### ⑨ portable-gaming_COMPARISON 글 전체 수정
- 서론 보일러플레이트 제거
- tags 구체적 롱테일 키워드로 교체
- permalink SEO 최적화
- Sources 마크다운 링크 형식으로 통일

---

## 3. 파이프라인 전체 흐름 (정비 후)

```
Step 1 (월 UTC 02:00, 자동)
  research.py → RSS 수집 → Discord "CSV 올려주세요"
  → research_data/trends/{week_tag}/ 폴더 생성

Step 2 (CSV 업로드 후 수동 트리거)
  research_gemini.py
    → 중복 클러스터 자동 필터 (dedup_by_folder)
    → Grade/트렌드/타입 기준 정렬
    → publish_order 부여 (1, 2, 3...)
  pipeline.py
    → content_pipeline.json에 publish_order + folder 저장
  → Step 3 자동 트리거

Step 3 (Step 2 완료 후 자동)
  write.py next
    → file_id 반환: "001_2026-W30_05-android-auto_GUIDE"
  write.py prep
    → hub_keyword 실패 시 cluster_name fallback
    → write_prompt_{file_id}.txt 저장
  gemini_api.py --file-id
    → 1순위: file_id 직접 매칭
    → 초안: {file_id}.md 저장
  write.py review
    → review_prompt_{file_id}.txt 저장
  gemini_review_api.py --file-id
    → 1순위: file_id 직접 매칭
    → 최종본: final/{file_id}.md 저장
  quality_check.py
    → R2/R3/R4 + Gemini G1~G4 체크 (gemini-2.5-flash)

Step 4 (평일 UTC 14:00, 자동 FIFO)
  publish_one.py
    → 파일명 앞 3자리 숫자 기준 정렬 (publish_order)
    → 숫자 없는 구버전 → 999 처리 (알파벳 순)
    → HUB: 스포크 2개 이상 발행 후에만 허용
    → _posts/ 저장 + write.py done

Step 5 (금 UTC 15:00, 자동)
  step5_audit.py → 품질 감사 → Discord 알림
```

---

## 4. 현재 남은 이슈

### 🔴 진행 중
- W30 Step 2 실행 중 (2026-07-28)
- Step 3 자동 연쇄 대기

### 🟡 추후 처리
| # | 이슈 | 파일 |
|---|------|------|
| 1 | Samsung Health HUB 발행 후 내부링크 교체 | _posts/ 07-16, 07-17 |
| 2 | Android/Fallout HUB 없음 | 다음 Step 2 때 HUB 타입 추가 |
| 3 | 발행 14편 전체 감사 (permalink, tags, sources, 서론) | 애드센스 승인 후 |
| 4 | Sources 형식 통일 자동화 | gemini_review_api.py 프롬프트 수정 |
| 5 | publish_one.py done 처리 흐름 검증 | content_pipeline status 업데이트 확인 |

### 🟢 완료
- slug 불일치 근본 해결 (folder_id + week_tag)
- publish_order FIFO
- hub_keyword fallback
- 중복 클러스터 필터
- Step 2→3 자동 연쇄
- venv/ gitignore
- published URL 정상화

---

## 5. Search Console 현황

```
색인 생성됨: 17페이지
미생성:      21페이지 (발견됨 - 대기 중 16개)
리디렉션 포함: http://frontbuffer.net, https://www.frontbuffer.net (정상 리디렉션)
리디렉션 오류: Samsung Health backup URL (permalink 수정 완료, 재크롤링 대기)

Google Organic 유입: 6명 (시작됨)
Bing 노출: Chrome MV2 키워드 2위
```

---

## 6. 다음 대화 시작 시 보낼 파일

```
Frontbuffer_프로젝트_정리_v19.md  ← 항상
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

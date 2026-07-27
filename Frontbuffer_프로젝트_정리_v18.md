# Frontbuffer Editorial 파이프라인 프로젝트 정리 v18

## 프로젝트 개요
영문 테크/게임 에버그린 블로그 AI 자동화.
- **Gemini 단일 모델** 워크플로우 (초안 + 그라운딩 팩트체크 + 서론/결론 재작성)
- 목표: 애드센스 승인 (20편 달성 후) + 제휴 마케팅으로 수익화
- 블로그: **frontbuffer.net** (Frontbuffer Editorial 브랜드)

---

## 완성된 자동화 흐름

```
[월요일 UTC 02:00] Step 1 cron
   → RSS 수집 + trends/ 폴더 자동 생성
   → 🔔 Discord "CSV 업로드 해주세요"
        ↓
[사람] Google Trends CSV를 각 폴더에 업로드
       (전부 올린 후 Step 2 수동 Run workflow)
        ↓
[수동 실행] Step 2
   → 기획안 생성 + Grade 판정
   → trends_analyzer.py 퍼지 매칭으로 폴더-클러스터 자동 연결
   → git pull --rebase 후 push (충돌 방지)
   → 🔔 Discord "기획안 N편 생성 완료"
        ↓
[Step 2 완료] Step 3 자동 연쇄 (미작동 이슈 있음 — 확인 필요)
   → 글 생성 루프 → final/ 커밋
   → quality_check.py 자동 실행
   → gemini_review_api.py 서론/결론 자동 재작성
   → 🔔 Discord "글 N편 / 스택 N편 + 품질 체크 결과"
        ↓
[평일 UTC 14:00] Step 4 cron
   → publish_one.py FIFO 발행
   → date: UTC 14:00 설정 → 한국 23:00 공개
   → 🔕 정상 발행 무알림 / 실패 시만 🔔
        ↓
[평일 UTC 16:00] Step 4 발행 확인 (step4_check.yml)
   → 오늘 날짜 _posts/ 파일 있는지 체크
   → 없으면 🔔 Discord 경고
        ↓
[금요일 UTC 15:00] Step 5 cron
   → step5_audit.py
   → audit_report.md 커밋
   → 🔔 Discord (이슈 있을 때만)
```

---

## 사람이 하는 일

```
매주 화요일:  Google Trends CSV 각 폴더에 업로드
              → 전부 올린 후 Step 2 수동 Run workflow
매일 발행 후: 1. 서론/결론 확인 + 수정
              2. git stash → git pull origin main --rebase → git stash pop
              3. python og_generator.py --file {파일명}
              4. X 수동 포스팅
              5. Reddit 워밍업 댓글 1~2개
              6. Quora 답변 (자연스럽게)
```

---

## 리포지토리 구조 (v18)

```
baek2731/frontbuffer
├── .github/workflows/
│   ├── jekyll.yml
│   ├── step1_research.yml   # trends/ git add 누락 수정 완료
│   ├── step2_plan.yml       # CSV push 자동 트리거 제거 + pull rebase 추가
│   ├── step3_write.yml      # v5 — 품질 체크 + 서론/결론 재작성
│   ├── step4_publish.yml
│   ├── step4_check.yml      # 신규 — 발행 확인 (UTC 16:00)
│   └── step5_audit.yml
├── _posts/                  # 발행된 글 (14편 + 내부 링크 추가 완료)
├── research_data/write/
│   ├── final/               # 발행 대기 스택
│   └── quality_report.json
├── write.py
├── publish_one.py
├── notify.py
├── quality_check.py
├── gemini_review_api.py     # 서론/결론 자동 재작성 포함
├── step5_audit.py           # Wikipedia 괄호 URL 오탐 수정
├── trends_analyzer.py       # 퍼지 매칭 추가 (폴더명-클러스터명 자동 매핑)
├── og_generator.py
└── content_pipeline.json
```

### GitHub Secrets
```
YOUTUBE_API_KEY      ✅
GEMINI_API_KEY       ✅
DISCORD_WEBHOOK_URL  ✅
```

---

## 블로그 현황 (2026-07-27)

### 발행된 글 (14편)
```
07-14  Steam Machine Overheating          [GAMING] ✅ 내부링크 추가
07-15  Steam Machine LED Error Codes      [GAMING] ✅ 내부링크 추가
07-16  How to Backup Samsung Health       [TECH]   ✅ 내부링크 추가
07-17  Samsung Health vs Google Health   [TECH]   ✅ 내부링크 추가
07-18  How to Check Chrome MV2           [TECH]   ✅ 내부링크 추가
07-19  Best MV3 Alternatives             [TECH]   ✅ 내부링크 추가
07-20  What is Chrome MV3                [TECH]   ✅ 내부링크 추가
07-20  Chrome MV2 HUB                    [TECH]   ✅ (기존 링크 완비)
07-21  Samsung Secure Folder vs Google   [TECH]   ✅ 내부링크 추가
07-21  Google Photos Free Storage        [TECH]   ✅ 내부링크 추가
07-22  How to Transfer Samsung Health    [TECH]   ✅ 내부링크 추가
07-23  Fallout NV vs Fallout 3 Remaster  [GAMING] ✅ 내부링크 추가
07-24  Fallout NV Endings Explained      [GAMING] ✅ 내부링크 추가
07-26  Fallout NV Modding Guide          [GAMING] ✅ 내부링크 추가
```

### final/ 스택 잔량 (약 10편)
```
Steam Machine    HUB / COMPARISON / GUIDE
Samsung Health   HUB / COMPARISON / GUIDE
Chrome           EXPLAINER / GUIDE / LISTICLE
Portable Gaming  COMPARISON / EXPLAINER / GUIDE
```

---

## 미해결 이슈 (다음 대화에서 처리)

### 🔴 긴급
```
1. Step 3 자동 연쇄 미작동
   - Step 2 성공해도 Step 3가 자동으로 안 돌아감
   - workflow_run 트리거가 수동 실행(workflow_dispatch)을
     감지 못하는 GitHub 제약일 가능성
   - 확인 필요: Step 2 성공 후 Step 3가 Skipped인지 아예 안 뜨는지
   - 현재: Step 3 수동 실행으로 임시 대응

2. W30 Step 3 글 생성 아직 안 됨
   - Step 2 수동 실행 완료 (2026-07-27)
   - Step 3 수동 실행 필요 또는 자동 연쇄 확인 필요
```

### 🟡 다음 주 전에
```
3. write.py 프롬프트 강화
   - 게임 분석 글 보일러플레이트 패턴 추가 금지
   - 데이터 더 쌓인 후 진행

4. Step 2 → Step 3 자동 연쇄 수정
   - workflow_run 트리거 문제 확인 후
   - 필요시 step3_write.yml 수정
```

---

## SEO 현황 (2026-07-27)

```
구글 색인:       14편
Search Console:  노출 93회 / 클릭 3회
                 Steam Machine LED 8.6위
                 Samsung Health vs Health Connect 5~6위
GA4:            활성 23명 / google organic 6명
Bing:           URL 12개 직접 제출 완료
내부 링크:       13편 전체 추가 완료 (클러스터별 연결)
```

---

## 소셜 현황 (2026-07-27)

```
X:      14편 포스팅 완료
Reddit: r/chrome, r/webdev, r/steammachine 댓글 누적
        업보트 1개 / 8월 31일 Chrome 데드라인 타이밍 준비 중
Quora:  답변 6개 / content views 34회
        Chrome (4개) + Samsung Health (1개) + Flash Drive (1개)
```

---

## 애드센스 신청 방침
```
20편 달성 후 신청 (현재 14편 → 약 6일 후)
Gaming/Tech 카테고리 균형 맞추기
```

---

## 수익화 로드맵

```
단기 (지금~3개월):
  1. 애드센스 승인 (20편 달성 후)
  2. Amazon Associates 시범 링크
  3. 8월 31일 Chrome 데드라인 Reddit 활용

중기 (3~6개월):
  4. 멀티 블로그 검토 (같은 주제 인접 확장)
  5. 뉴스레터 시작
  6. Mediavine 전환 준비 (월 5만 PV 목표)

장기:
  7. 유료 리포트 / 번역 블로그
```

---

## 비용

```
Gemini (편당):  약 $0.003
Step 5:         $0
월간 배치 비용: 약 $0.15~0.20
```

---

## 다음 대화 시작 방법

### 첨부할 파일 (필수)
```
Frontbuffer_프로젝트_정리_v18.md
```

### 첫 메시지
```
v18 문서 첨부했어. 오늘 할 작업은:

1. Step 3 자동 연쇄 미작동 원인 파악 및 수정
   - Step 2 수동 실행 완료된 상태
   - Step 3가 자동으로 안 돌아가는 이유 확인
   - workflow_run 트리거 문제인지 확인

2. W30 Step 3 글 생성 확인
   - Step 3 실행 결과 Discord 알림 확인

3. 오늘 발행된 글 서론/결론 확인
```

### 주의사항
```
- 말투: ~요체 고정
- MD 파일 생성 시도 ~요체 적용
- 수동으로 해결하기 전에 근본 원인 파악 먼저
```

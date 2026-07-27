# Frontbuffer Editorial 파이프라인 프로젝트 정리 v16

## 프로젝트 개요
영문 테크/게임 에버그린 블로그 AI 자동화.
- **Gemini 단일 모델** 워크플로우 (초안 + 그라운딩 팩트체크)
- 목표: 애드센스 승인 + 제휴 마케팅으로 수익화
- 블로그: **frontbuffer.net** (Frontbuffer Editorial 브랜드)

---

## 완성된 자동화 흐름

```
[월요일 UTC 02:00] Step 1 cron
   → RSS 수집
   → 🔔 Discord "CSV 업로드 해주세요"
        ↓
[사람] Trends/KP CSV를 GitHub 웹에 업로드
        ↓
[CSV push 감지] Step 2 자동 시작
   → 기획안 생성 + Grade 판정
   → 🔔 Discord "기획안 N편 생성 완료"
        ↓
[Step 2 완료] Step 3 자동 연쇄
   → 글 생성 루프 → final/ 커밋
   → quality_check.py 자동 실행 (신규 글 품질 평가)
   → quality_report.json 커밋
   → 🔔 Discord "글 N편 / 스택 N편 + 품질 체크 결과"
        ↓
[평일 UTC 14:00] Step 4 cron (매일, 실제 1~2시간 지연 있음)
   → publish_one.py
     1. final/ FIFO 1개 선택
     2. [INTERNAL LINK] → 실제 URL 주입
     3. front matter 생성
     4. _posts/ + published/ 저장
     5. content_pipeline.json spoke_urls/hub_url 업데이트
     6. write.py done --no-archive
   → 🔕 정상 발행 무알림 / 실패 시만 🔔
        ↓
[금요일 UTC 15:00] Step 5 cron
   → step5_audit.py (API 호출 없음, 비용 0)
     자동: 불필요 플레이스홀더 제거 / published/ 동기화 / HUB 역방향 링크 소급
     수동확인: [INTERNAL LINK] 잔존(_posts/) / NEEDS VERIFICATION / 단어수 미달 /
              front matter / HUB-스포크 / 404
   → audit_report.md 커밋
   → 🔔 Discord (수동 확인 0건 + 스택 3 이상이면 생략)
```

---

## 사람이 하는 일

```
매주 화요일:  Trends/KP CSV GitHub 웹에 업로드
매일 발행 후: 1. 발행된 글 서론/결론 빠르게 확인 (보일러플레이트 수정)
              2. git pull origin main
              3. python og_generator.py --file {파일명}
              4. social_output/{slug}/tweet.txt + og.png → X 수동 포스팅
              5. Quora 관련 질문 답변 1~2개
              6. Reddit 워밍업 댓글 2~3개 (링크 없이, 2주간)
```

---

## 리포지토리 구조 (v16)

```
baek2731/frontbuffer
├── .github/workflows/
│   ├── jekyll.yml
│   ├── step1_research.yml      # 월요일 UTC 02:00 cron
│   ├── step2_plan.yml          # CSV push 감지 자동 트리거
│   ├── step3_write.yml         # Step2 완료 시 자동 연쇄 (v5 — 품질 체크 추가)
│   ├── step4_publish.yml       # 평일 UTC 14:00 cron
│   └── step5_audit.yml         # 금요일 UTC 15:00 cron
├── _posts/                     # 발행된 글 (11편+)
├── _pages/
│   ├── about.md
│   ├── privacy-policy.md
│   └── disclosure.md
├── research_data/write/
│   ├── final/                  # 발행 대기 스택
│   ├── published/              # 발행 아카이브
│   ├── audit_report.md         # Step 5 감사 리포트
│   └── quality_report.json     # Step 3 품질 체크 리포트 (신규)
├── write.py
├── publish_one.py
├── notify.py                   # v2 — Step 3 품질 체크 결과 포함
├── quality_check.py            # 신규 — Step 3 완료 후 final/ 품질 평가
├── step5_audit.py              # [INTERNAL LINK] 잔존 수동 확인으로 격상
├── og_generator.py
├── social_output/              # gitignore (로컬 전용)
├── content_pipeline.json
└── posts.json
```

### GitHub Secrets
```
YOUTUBE_API_KEY      ✅
GEMINI_API_KEY       ✅
DISCORD_WEBHOOK_URL  ✅
```

---

## quality_check.py 체크 항목 (v16 신규)

```
[규칙 기반 — 코드, 100% 정확]
R2. [NEEDS VERIFICATION] 태그 잔존 (final/ 기준)
R3. 단어수 미달 (HUB: 600단어 / 스포크: 800단어)
R4. H1 제목 없음
※ R1([INTERNAL LINK])은 final/에서 정상 잔존 → Step 5(_posts/ 기준)로 이관

[Gemini YES/NO — 서론/결론 발췌 판단]
G1. 금지 서론 오프너 패턴
G2. 서론 1인칭 사용
G3. 금지 결론 패턴
G4. 결론 보일러플레이트 (주제 교체해도 통용되는 문장)
```

### Discord 알림 예시 (Step 3 완료)
```
✅ Step 3 완료 — 글 생성 + 품질 체크
8편 생성 완료. 현재 final/ 스택: 14편

⚠️ 품질 확인 필요 — 2편
• steam-machine-hub_HUB
  서론 금지 오프너 패턴 감지 / 결론 보일러플레이트
  [GitHub 직링크]

✅ 이상 없음 — 6편
```

---

## 블로그 현황 (2026-07-23)

### 발행된 글 (11편)
```
07-14  How to Troubleshoot Steam Machine Overheating     [GAMING] ✅
07-15  Steam Machine LED Error Codes                     [GAMING] ✅
07-16  How to Backup Samsung Health Data                 [TECH]   ✅
07-17  Samsung Health vs Google Health Connect           [TECH]   ✅
07-18  How to Check Chrome Extensions Manifest V2        [TECH]   ✅
07-19  Best Manifest V3 Alternatives                     [TECH]   ✅
07-20  What is Chrome Manifest V3                        [TECH]   ✅
07-20  Chrome Manifest V2 HUB                            [TECH]   ✅
07-21  Samsung Secure Folder vs Google Files             [TECH]   ✅수동수정완료
07-21  Google Photos Free Storage Policy                 [TECH]   ✅수동수정완료
07-22  How to Transfer Samsung Health Data               [TECH]   ✅수동수정완료
```

### final/ 스택 잔량 (약 14편)
```
Steam Machine    HUB / COMPARISON / GUIDE
Samsung Health   HUB / COMPARISON / GUIDE
Chrome           EXPLAINER / GUIDE / LISTICLE
Fallout Series   COMPARISON / EXPLAINER / GUIDE
Portable Gaming  COMPARISON / EXPLAINER / GUIDE
```

### quality_check.py 첫 실행 결과 (2026-07-23)
```
이상 없음:    8편 (HUB 단어수 기준 600단어 조정 후)
확인 필요:    7편
  - [INTERNAL LINK] 잔존 6편 → final/에서 정상 (publish_one.py가 처리)
  - 단어수 미달 1편: steam-machine-hardware-management_GUIDE (792단어)
```

### 글 품질 이슈
```
문제: 기존 write.py로 생성된 글에 보일러플레이트 서론/결론 패턴 있음
해결: 발행 직후 수동 확인 + 필요 시 GitHub에서 수정
      quality_check.py Discord 알림 보고 write.py 프롬프트 점진적 개선
```

---

## SEO 현황

```
구글 색인:          11편 완료
Search Console:     데이터 수집 중
                    HTTPS 경고 (www.frontbuffer.net) → 수정 요청 완료
Bing Webmaster:     등록 완료 + 사이트맵 제출
GA4:               G-D1CX22H203 연결 완료
Cloudflare DNS:    A 레코드 4개 + CNAME www + TXT 구글인증 ✅
```

---

## 소셜 미디어 현황

### X (Twitter) @FrontbufferEdit
```
포스팅: 11편 완료
팔로워: 0명 (신규 계정)
자동화: X API 유료화로 보류 (팔로워 100명+ 시 재검토)
```

### Quora @FrontBuffer
```
답변 3개 — 검색 결과 2~3위 노출 확인
```

### Reddit u/Hairy-Feedback-9550
```
상태: 워밍업 중
목표: 2주간 링크 없이 카르마 쌓기 → 8월 중순 링크 포함 댓글
```

---

## 백링크 방침 (v16 변경)

```
기존 계획 (DEV.to / Medium / tldr.tech 등) → 보류
이유:
  - AI 생성 콘텐츠 기반 백링크 → 스패미한 링크 프로파일 리스크
  - Quora/Reddit은 nofollow라 SEO 직접 효과 미미
  - 지금 최우선은 콘텐츠 품질 + 애드센스 승인

현재 방침:
  - 백링크보다 글 품질 개선에 집중
  - 애드센스 승인 후 백링크 전략 재검토
```

---

## 애드센스 신청 체크리스트

```
✅ 독립 도메인 (frontbuffer.net)
✅ About 페이지 + 연락처 (frontbuffer.editorial@gmail.com)
✅ Privacy Policy
✅ Disclosure
✅ 구글 색인 완료 (11편)
✅ HTTPS
✅ GA4 연결
✅ 홈페이지 구조 (카테고리 카드 + Recent Posts)
⬜ 글 15편+ (현재 11편 → 약 4일 후 달성)
⬜ Search Console 클릭 데이터 생기기 시작
⬜ 트래픽 소폭 발생
⬜ 발행된 글 서론/결론 수동 확인 완료
```

---

## 비용

```
Gemini (편당 글 생성): 약 $0.003
Gemini (품질 체크):    약 $0.000045/편 (사실상 무시)
12편 배치:             약 $0.04~0.05
Step 5:                $0
Discord/OG/X:          $0
백링크:                $0
```

---

## 수익화 로드맵

```
1단계 (지금):      콘텐츠 쌓기 + 글 품질 개선
2단계 (2~3주):     애드센스 신청 (15편+ 후)
3단계 (트래픽 후): Amazon Associates 제휴 추가
4단계 (월 1만PV+): VPN/소프트웨어 제휴 + X 자동 포스팅 재검토
```

---

## 다음 대화 시작 방법

### 첨부할 파일 (필수)
```
Frontbuffer_프로젝트_정리_v16.md  ← 이 파일
```

### 필요 시 첨부
```
publish_one.py / write.py / og_generator.py / step5_audit.py / quality_check.py
(수정 작업 있을 때만)
```

### 첫 메시지에 알려줄 것
```
1. Step 4 오늘 발행된 글 제목 + 서론/결론 수정 여부
2. Search Console HTTPS 경고 해결됐는지
3. 애드센스 신청 현황 (15편 달성 후)
4. quality_check.py Discord 알림 첫 실전 결과
```

### 다음 대화 우선 작업
```
1. 애드센스 신청 (15편 달성 시)
2. 발행 글 서론/결론 수동 확인 (남은 편)
3. quality_check.py 실전 결과 보고 write.py 프롬프트 점검
```

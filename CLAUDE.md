# CLAUDE.md — 라오스 국제결혼 웹사이트 구현 가이드

## 프로젝트 개요
라오스 전문 국제결혼정보회사 웹사이트. 국내 유일 라오스 현지 지사 + 어학당·기숙사 + 비자대행 직영이 핵심 차별점.
타겟: 국제결혼을 고려하는 한국 남성 30~50대. 모바일 유입 비중 높음 (카카오톡·네이버 광고 유입 가정).
핵심 전환: 회원가입 (이메일 접수) → 상담 → 화상맞선.

## 기술 스택
- Flask + Jinja2 SSR (네이버 Yeti 크롤링 대응 — SPA 금지)
- MariaDB
- 배포: Cafe24 가상서버 (기존 표준 환경)
- 프로토타입 HTML 9개를 Jinja2 템플릿으로 변환 (base.html 상속 구조로 리팩토링)

## 파일 구성 (프로토타입)
| 파일 | 페이지 | 비고 |
|---|---|---|
| index.html | 메인 | 히어로, 여성회원 미리보기(잠금), 3대 직영, 절차, 성혼 갤러리, 인증(네이비 밴드), 인삿말 티저, 오시는길 |
| greeting.html | 인삿말 | 본문은 클라이언트 직접 작성 → `.todo` 블록 교체 |
| license.html | 허가자료 | 인증 3종 스캔 이미지 교체, 클릭 시 라이트박스 확대 |
| process.html | 절차 및 비용 | 스티키 탭: 비용내역서/결혼절차/결혼일정표/준비서류 |
| video-meeting.html | 화상맞선의 장점 | 정적 페이지 |
| members.html | 여성회원 | 권한 로직 필수 (아래 참조) |
| faq.html | 고객센터 | 카테고리 필터 아코디언 |
| location.html | 찾아오시는길 | 지도 API 임베드 |
| signup.html | 회원가입 | 이메일 접수 로직 (아래 참조) |

카테고리에서 해피스토리·결혼앨범은 제외 (기획 확정).

## 디자인 시스템
- 컬러: 화이트 베이스 / 네이비 #1E3557 (primary) / 골드 #C9A05C·#B8873D (소량 액센트) / 중성 그레이 #F8F8F7 (섹션 구분)
- 폰트: Noto Serif KR (헤드라인) + Pretendard (본문)
- 아이콘: 인라인 SVG (stroke, currentColor) — 이모지 사용 금지
- 다크 밴드(네이비)는 절차 섹션·인증 섹션·page-hero·CTA 밴드에만
- 모션: IntersectionObserver 스크롤 리빌(.rv), prefers-reduced-motion 대응 유지

## 모바일 규칙 (중요)
- 메인 히어로: 이미지 먼저(order:-1) → 헤드라인 → 버튼(풀폭 2분할)
- 히어로 아래 퀵메뉴 4버튼 (여성회원/절차·비용/화상맞선/오시는길) — 모바일 전용
- 여성회원 카드·성혼 갤러리: 가로 스와이프 스냅 캐러셀 (≤700px)
- 하단 고정 CTA 바: 전화 / 카톡상담 / 회원가입 — 전 페이지 공통
- 카톡상담 링크: 오픈채팅 or 카카오채널 URL로 교체 (클라이언트 확인)

## 이미지 교체 목록 (클라이언트 제공 → 별도 전달 예정)
`.ph` placeholder를 실제 이미지로 교체. 위치별:
1. **메인 히어로 대표컷** — 전통혼례식 또는 성혼 커플 (index)
2. **여성회원 사진** — index 6장 + members 8장 (DB 연동 시 동적 처리)
3. **3대 직영 섹션** — 라오스 지사 사무실 / 어학당·기숙사 / 비자수속·입국 (index)
4. **성혼 갤러리 6장** — 전통혼례식·커플 사진 (index)
5. **인증 3종 스캔본** — 국제결혼중개업 등록증 / 보증서(보증보험증권) / 교육수료증 (index 네이비 밴드의 CSS 목업 `.paper` 3장 + license.html 3장 교체)
6. **대표 프로필 사진 + 명함** — index 인삿말 티저 + greeting.html
7. **화상맞선 진행 장면** — video-meeting.html
8. **지도** — location.html + index: 카카오맵 or 네이버지도 API 임베드

## 텍스트 placeholder (클라이언트 확인 필요)
- 상호명 "라오스결혼" → 확정 상호로 전체 치환
- 전화번호 0XX-XXX-XXXX / 010-0000-0000, 이메일, 사업자등록번호, 대표자명
- 국제결혼중개업 등록번호 / 보증보험 증권번호 (index 인증 리스트 + license + footer)
- 비용: process.html 총액 "0,000만원" + 포함항목 중 [클라이언트 확인] 표기 2곳 (화상맞선 횟수, 신부 입국 항공료)
- 인삿말 본문 (greeting.html `.todo` 블록)
- 대중교통·주차 안내 (location.html)
- 회원 수·성혼 수 등 수치 (현재 더미: 1,248명 등)
- 주소는 확정: 전남광주통합특별시 북구 하서로 421 양산빌딩 5층

## 회원가입 — 이메일 접수 구현
- POST /signup → 유효성 검증 → DB 저장 + 관리자 이메일 발송 (SMTP)
- 이메일 원문에 비밀번호 평문 포함 금지 (DB에는 bcrypt 해시 저장)
- 스팸 방지: honeypot 필드 + rate limit (IP당 시간당 제한)
- 접수 완료 페이지 → "영업일 1일 내 연락" 안내
- 수집 필드: 아이디, 비밀번호, 이름, 생년월일, 연락처, 주소, 최종학력(select), 직업, 연봉구간(select, 연말정산·소득세신고 기준), 해당사항 체크박스(기혼/재혼희망/자녀있음), 개인정보 수집·이용 동의(필수)

## 여성회원 열람 권한 (핵심 로직)
- 비로그인: members.html 잠금 화면 (블러 + 자물쇠). 프로필 상세 접근 차단
- 로그인(관리자 승인 회원): 잠금 해제, 사진·프로필 노출, 상세 라우트 /members/<id>
- 상세페이지: 대표 사진 여러 장을 상단에 크게 (베스트 리뷰 스타일), 기본 정보(나이·지역·직업·학력 등)
- 가입 즉시가 아니라 **관리자 승인 후** 열람 권한 부여 (status: pending → approved)

## DB 스키마 (초안)
```sql
users (id, login_id, pw_hash, name, birth, phone, address, education, job,
       income_range, is_married, is_remarriage, has_children,
       status ENUM('pending','approved','blocked'), created_at)

female_members (id, name_masked, age, region, job_note, is_active, sort_order, created_at)
female_photos (id, member_id FK, path, is_main, sort_order)

inquiries (id, user_id NULL, name, phone, message, created_at)  -- 상담신청 별도 받을 경우
```

## 관리자 기능 (2차)
- 가입 신청 목록 / 승인·차단
- 여성회원 CRUD + 사진 업로드 (대표컷 지정)
- FAQ 관리 (선택)

## SEO
- SSR이므로 meta title/description 페이지별 작성, OG 태그 (카톡 공유 대응 — 대표 이미지 필수)
- sitemap.xml + robots.txt, 네이버 서치어드바이저 등록
- 시맨틱 헤딩 구조 유지 (h1은 페이지당 1개)

## 작업 순서 제안
1. Flask 프로젝트 셋업 + base.html 추출 (헤더/푸터/스티키CTA 공통화)
2. 정적 페이지 라우팅 (전체 9페이지)
3. 회원가입 폼 처리 (DB + SMTP)
4. 로그인/세션 + 여성회원 권한 로직 + 상세페이지
5. 관리자 페이지
6. 이미지·텍스트 placeholder 일괄 교체 (클라이언트 자료 수급 후)
7. 지도 API, 카톡 채널 링크, OG/SEO 마무리

# apt-watch — 대상 단지 매물 모니터링

2027년 4월 잔금 기준으로 매수 후보 단지의 매매 매물·호가·실거래를 주기적으로 확인하고 조건에 맞는 신규 매물이나 가격 인하를 Telegram으로 알리는 개인용 도구입니다.

> 목표: 관심 단지의 급매 후보를 빠르게 발견한다.

## v1

GitHub Actions가 30분마다 Python 수집기를 실행하고 `data/snapshots/`의 이전 상태와 비교합니다.

- `collector/naver.py` — 네이버 부동산 매물 adapter
- `collector/molit.py` — 국토교통부 아파트 실거래 API
- `collector/parse.py` — 세입자 만기/갱신청구권/입주 키워드 파싱
- `collector/diff.py` — 신규·가격 인하·소진 이벤트 계산
- `collector/notify.py` — Telegram 알림
- `collector/run.py` — 1회 실행 entry point

## 대상 단지

| 우선순위 | 단지 | 타깃 | 상한 |
|---|---|---|---:|
| 1 | 가양6단지 | 전용 58~59㎡ | 10.5억 |
| 1 | 등촌주공10단지 | 전용 58~60㎡ | 10.5억 |
| 2 | 염창동아1차 | 전용 58~60㎡ | 10.5억 |
| 3 | 관악드림타운 | 전용 58~60㎡ | 11.5억 |

실제 설정은 `config/targets.yaml`에 두고 Git에는 커밋하지 않습니다. 템플릿은 `config/targets.example.yaml`을 사용합니다.

## 설치

```bash
git clone https://github.com/shinhyuk/house.git
cd house
cp config/targets.example.yaml config/targets.yaml
cp .env.example .env
pip install -r requirements.txt
python -m collector.run --once
```

`config/targets.yaml`의 각 `naver_complex_no`를 채우고, `.env`에는 다음 값을 설정합니다.

```text
MOLIT_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

GitHub Actions에서는 같은 이름으로 Repository Secrets를 등록합니다.

## 알림 규칙

- 🔴 타깃 평형 신규 매물 ≤ 상한
- 🔴 설명에서 세입자 만기 2027년 3~4월 감지
- 🟠 기존 매물이 가격 인하 후 상한 +5% 이내 진입
- 소진(gone)은 스냅샷 diff에서 감지하며 일간 요약 기능에 연결 예정
- 국토부 실거래 일간 요약/주간 리포트는 다음 단계

## 데이터 및 보안

`.env`, `config/targets.yaml`, `config/finance.local.yaml`은 `.gitignore` 대상입니다. API 키, Telegram 토큰, 실제 재무 수치, 전화번호 등 민감한 값은 커밋하지 않습니다.

현재 저장소는 Public이므로 스냅샷에도 개인 메모나 전화번호 등 공개하면 안 되는 데이터를 저장하지 마세요. 원래 설계처럼 원문 매물 설명을 장기 보관하려면 저장소를 Private으로 전환하는 편이 안전합니다.

## 네이버 부동산 관련 주의

`collector/naver.py`는 실험적인 adapter입니다. 인증 우회나 차단 회피를 구현하지 않습니다. 서비스 정책/접근 제한을 준수하고 낮은 빈도로 사용하세요. 엔드포인트나 응답 스키마가 바뀌면 adapter를 수정해야 합니다.

## 현재 구현 상태

v1 골격이 구성되어 있습니다. 다음 작업은 (1) complexNo 확정, (2) 네이버 실제 응답 기준 가격/면적 정규화, (3) 국토부 실거래를 run.py에 연결, (4) 일간/주간 digest, (5) 테스트 추가입니다.

# KNOU 공지 알림 봇

방송대 학사공지 + 컴퓨터과학과 공지를 크롤링해서 Slack 채널에 자동으로 알려주는 봇입니다.

## 동작 방식
- GitHub Actions가 평일 09:00~20:00, 30분마다 자동 실행
- 새 공지 발견 시 Slack Webhook으로 전송
- seen_ids.json에 이미 알림 보낸 공지 ID를 기록해 중복 방지

## 게시판 추가하는 법
crawler.py의 BOARDS 리스트에 딕셔너리 하나 추가하면 됩니다.

---
## 파일 구조
knou-notice-bot/
├── crawler.py              # 크롤링 + Slack 전송 메인 로직
├── seen_ids.json           # 이전에 본 공지 ID 기록
├── requirements.txt        # 필요한 파이썬 패키지 목록
├── README.md               
└── .github/
    └── workflows/
        └── crawl.yml       # GitHub Actions 자동 실행 설정
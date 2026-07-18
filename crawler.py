import requests
from bs4 import BeautifulSoup
import json
import os
import re

SEEN_FILE = "seen_ids.json"
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

# 여러 게시판 등록 - 여기에 원하는 게시판 추가
BOARDS = [
    {
        "name": "학사공지",
        "list_url": "https://www.knou.ac.kr/bbs/knou/51/artclList.do",
        "base_url": "https://www.knou.ac.kr",
        "emoji": "🏫",
    },
    {
        "name": "컴퓨터과학과 공지",
        "list_url": "https://cs.knou.ac.kr/bbs/cs1/2119/artclList.do",  # ⚠️ 실제 주소 재확인 필요
        "base_url": "https://cs.knou.ac.kr",
        "emoji": "💻",
    },
]

HEADERS = {"User-Agent": "Mozilla/5.0"}


def load_seen_ids():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen_ids(ids):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(ids), f, ensure_ascii=False)


def crawl_board(board):
    res = requests.get(board["list_url"], headers=HEADERS, timeout=10)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    notices = []
    # K2Web 게시판은 보통 table 안에 artclView.do 링크로 구성됨
    for a in soup.select("a[href*='artclView.do']"):
        title = a.get_text(strip=True)
        href = a.get("href")
        if not title or not href:
            continue

        # 글번호 추출: .../51/805715/artclView.do 형태
        m = re.search(r"/(\d+)/artclView\.do", href)
        if not m:
            continue
        notice_id = f"{board['name']}-{m.group(1)}"

        full_link = href if href.startswith("http") else board["base_url"] + href
        notices.append({"id": notice_id, "title": title, "link": full_link})

    # 같은 글이 목록에 여러 번(일반공지+실제글) 나올 수 있어 중복 제거
    seen_in_page = set()
    unique = []
    for n in notices:
        if n["id"] not in seen_in_page:
            seen_in_page.add(n["id"])
            unique.append(n)
    return unique


def send_to_slack(board, notice):
    payload = {
        "text": f"{board['emoji']} *[{board['name']}]* 새 공지: <{notice['link']}|{notice['title']}>"
    }
    requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)


def main():
    seen = load_seen_ids()
    first_run = len(seen) == 0

    for board in BOARDS:
        try:
            notices = crawl_board(board)
        except Exception as e:
            print(f"[{board['name']}] 크롤링 실패: {e}")
            continue

        new_notices = [n for n in notices if n["id"] not in seen]

        # 첫 실행이면 스팸 방지를 위해 알림 없이 기록만
        if not first_run:
            for n in reversed(new_notices):
                send_to_slack(board, n)

        for n in new_notices:
            seen.add(n["id"])

    save_seen_ids(seen)


if __name__ == "__main__":
    main()
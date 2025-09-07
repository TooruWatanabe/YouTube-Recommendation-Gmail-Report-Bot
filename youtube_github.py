from googleapiclient.discovery import build
from openai import OpenAI
import isodate
import re
import base64
import os.path
from email.mime.text import MIMEText
from googleapiclient.discovery import build as gmail_build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ========= 設定 =========
YOUTUBE_API_KEY = "Your API Key"
OPENAI_API_KEY = "YOur API Key"
TO_ADDRESS = "Your email address"  # 宛先（Yahooメールなど）
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
# ========================

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return gmail_build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text, "plain", "utf-8")
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    return service.users().messages().send(userId=user_id, body=message).execute()

def search_videos(query, max_results=25):
    search_request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        order="date",
        maxResults=max_results
    )
    search_response = search_request.execute()
    video_ids = [item["id"]["videoId"] for item in search_response["items"]]

    videos_request = youtube.videos().list(
        part="contentDetails,snippet",
        id=",".join(video_ids)
    )
    videos_response = videos_request.execute()

    results = []
    for item in videos_response["items"]:
        duration_str = item["contentDetails"]["duration"]
        duration = isodate.parse_duration(duration_str).total_seconds()
        if duration > 60:  # 1分以上
            results.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "video_id": item["id"],
                "publishedAt": item["snippet"]["publishedAt"]
            })
    return results

def summarize_with_gpt(title, description, query):
    prompt = f"""
    以下のYouTube動画が次の人物にどれくらい役立つかを0〜100でスコア化し、
    日本語で1行要約してください。

    --- 人物プロフィール ---
    - 職業: 自動車メーカーのアフターサービス部門の部長
    - 興味分野: EV、自動運転、海外転職、データエンジニアリング、AI、CRM
    - 使用経験: Power BI, Python, SQL, CRM分析
    - キャリア目標: データエンジニアとして海外（特にヨーロッパ）で活躍すること
    -----------------------

    --- 動画情報 ---
    タイトル: {title}
    説明文: {description}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_score(text):
    match = re.search(r"スコア[:：]\s*(\d+)", text)
    return int(match.group(1)) if match else 0

# ========== メイン処理 ==========
topics = [
    "EV cars",
    "Electric Vehicle",
    "Autonomous driving",
    "Data engineering career",
    "AI agent",
    "Overseas job searching",
    "CRM"
]

all_results = []

for query in topics:
    videos = search_videos(query, max_results=25)
    for v in videos:
        url = f"https://www.youtube.com/watch?v={v['video_id']}"
        summary = summarize_with_gpt(v["title"], v["description"], query)
        score = extract_score(summary)

        if score >= 70:  # スコア70以上のみ
            all_results.append({
                "keyword": query,
                "title": v["title"],
                "url": url,
                "publishedAt": v["publishedAt"],
                "score": score,
                "summary": summary
            })

# 本文を組み立て
body_text = "📩 今週のおすすめYouTube動画レポート（スコア70以上）\n\n"
for r in all_results:
    body_text += f"[{r['keyword']}] {r['title']} ({r['publishedAt']})\n"
    body_text += f"{r['url']}\n"
    body_text += f"{r['summary']}\n"
    body_text += f"スコア: {r['score']}\n\n"

if not all_results:
    body_text += "今回は該当するおすすめ動画は見つかりませんでした。\n"

# Gmail送信
service = gmail_authenticate()
msg = create_message("me", TO_ADDRESS, "YouTubeおすすめ動画レポート", body_text)
send_message(service, "me", msg)
print("✅ レポートメールを送信しました！")

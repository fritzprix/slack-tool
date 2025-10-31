# Slack Archive Tool

Slack 워크스페이스의 대화 히스토리를 JSON 파일로 체계적으로 아카이브하는 Python 도구입니다.

## 기능

- 📝 **모든 채널 또는 특정 채널의 메시지 히스토리 저장**
- 🧵 **스레드 메시지 포함**
- 👤 **사용자 정보 자동 매핑** (ID → 실명)
- 📅 **타임스탬프를 읽을 수 있는 형식으로 변환**
- 📑 **채널 메타데이터 저장** (주제, 목적, 멤버 수 등)
- 🗂️ **인덱스 파일 생성** (아카이브 목록 관리)
- ⚡ **Rate limiting 자동 처리**
- 🔍 **채널 목록 조회**

## 설치

### 1. 의존성 설치

```bash
pip install -r requirements.txt
# 또는
pip install slack-sdk>=3.23.0
```

### 2. Slack Bot Token 준비

[Slack API 콘솔](https://api.slack.com/apps)에서:
1. App 생성 또는 선택
2. OAuth & Permissions에서 Bot User OAuth Token 생성
3. 필요한 scopes 추가:
   - `channels:history` - 채널 메시지 읽기
   - `conversations:list` - 채널 목록 조회
   - `users:list` - 사용자 정보 조회

## 사용법

### 환경변수 설정 (권장)

```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
```

### 1. 모든 채널 아카이브

```bash
python main.py --all
```

### 2. 특정 채널 아카이브

```bash
# 채널 ID로
python main.py --channel C123456789

# 채널 이름으로
python main.py --channel general
```

### 3. 여러 채널 아카이브

```bash
python main.py --channels C123456789 C987654321 general
```

### 4. 사용 가능한 채널 목록 보기

```bash
python main.py --list
```

### 5. 아카이브 인덱스 생성

```bash
python main.py --all --index
```

이미 아카이브된 채널들의 목록을 `archives/INDEX.json`에 생성합니다.

## 옵션

| 옵션 | 설명 |
|------|------|
| `--token TOKEN` | Slack Bot Token (또는 SLACK_BOT_TOKEN 환경변수) |
| `--archive-dir DIR` | 아카이브 디렉토리 (기본값: `archives`) |
| `--all` | 모든 채널 아카이브 |
| `--channel CH` | 특정 채널 아카이브 |
| `--channels CH1 CH2 ...` | 여러 채널 아카이브 |
| `--list` | 채널 목록 출력 |
| `--no-threads` | 스레드 메시지 제외 |
| `--include-archived` | 아카이브된 채널도 포함 |
| `--index` | 인덱스 파일 생성 |
| `-v, --verbose` | 상세 로그 출력 |

## 예제

### 예제 1: 모든 채널 아카이브

```bash
python main.py --token xoxb-xxxx --all
```

아카이브 디렉토리 구조:
```
archives/
├── general_20251031_143022.json
├── marketing_20251031_143045.json
├── engineering_20251031_143108.json
└── INDEX.json
```

### 예제 2: 특정 채널만 아카이브

```bash
python main.py --channel general --no-threads
```

### 예제 3: 아카이브된 채널 포함

```bash
python main.py --list --include-archived
```

## 아카이브 파일 구조

생성된 JSON 파일의 구조:

```json
{
  "metadata": {
    "archived_at": "2025-10-31T14:30:22.123456",
    "channel_id": "C123456789",
    "channel_name": "general",
    "channel_topic": "Company announcements",
    "channel_purpose": "General discussion",
    "is_private": false,
    "created": 1609459200,
    "member_count": 45
  },
  "messages": [
    {
      "type": "message",
      "user": "U123456789",
      "user_name": "John Doe",
      "text": "Hello everyone!",
      "ts": "1609459200.000100",
      "timestamp_readable": "2021-01-01T00:00:00",
      "reply_count": 2,
      "thread_messages": [
        {
          "type": "message",
          "user": "U987654321",
          "user_name": "Jane Smith",
          "text": "Hi John!",
          "ts": "1609459211.000200",
          "timestamp_readable": "2021-01-01T00:00:11"
        }
      ]
    }
  ],
  "message_count": 1250
}
```

## INDEX.json 구조

`--index` 옵션으로 생성된 인덱스 파일:

```json
{
  "created_at": "2025-10-31T14:35:00.123456",
  "archives": [
    {
      "filename": "general_20251031_143022.json",
      "channel_name": "general",
      "channel_id": "C123456789",
      "message_count": 1250,
      "archived_at": "2025-10-31T14:30:22.123456",
      "file_path": "/path/to/archives/general_20251031_143022.json"
    }
  ]
}
```

## 로그

프로그램 실행 중 상세한 로그가 출력됩니다:

```
2025-10-31 14:30:22 - slack_archiver - INFO - SlackArchiver initialized with archive directory: archives
2025-10-31 14:30:23 - slack_archiver - INFO - Loaded 45 users into cache
2025-10-31 14:30:24 - slack_archiver - INFO - Retrieved 15 channels
2025-10-31 14:30:25 - slack_archiver - INFO - [1/15] Processing channel: #general
2025-10-31 14:30:26 - slack_archiver - INFO - Archived 1250 messages to archives/general_20251031_143022.json
```

## 주의사항

⚠️ **Rate Limiting**: Slack API는 분당 요청 제한이 있습니다. 프로그램이 자동으로 대기합니다.

⚠️ **대용량 데이터**: 메시지가 많은 채널은 처리 시간이 오래 걸릴 수 있습니다.

⚠️ **토큰 보안**: Bot Token을 절대 버전 관리 시스템에 커밋하지 마세요.

## 트러블슈팅

### "토큰이 필요합니다" 오류

```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
python main.py --all
```

### "권한 부족" 오류

Bot에 필요한 scopes이 있는지 확인:
- `channels:history`
- `conversations:list`
- `users:list`

### 특정 채널을 찾을 수 없음

먼저 채널 목록을 확인:
```bash
python main.py --list
```

## 저작권

MIT License

## 기여

버그 리포트 및 개선 제안은 이슈를 통해 주세요!

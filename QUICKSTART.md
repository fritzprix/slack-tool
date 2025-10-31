# 빠른 시작 가이드

## 1단계: 설치

### 1.1 의존성 설치

```bash
pip install -r requirements.txt
```

### 1.2 환경변수 설정

```bash
# .env 파일 생성 (또는 환경변수 직접 설정)
cp .env.example .env

# .env 파일에서 SLACK_BOT_TOKEN 값 입력
# 또는 명령줄에서 설정:
export SLACK_BOT_TOKEN="xoxb-your-token-here"
```

## 2단계: Slack Bot Token 준비

1. [Slack API 콘솔](https://api.slack.com/apps)에 접속
2. 기존 앱을 선택하거나 새로 생성
3. **OAuth & Permissions** 클릭
4. **Scopes** 섹션에서 Bot Token Scopes 추가:
   - `channels:history`
   - `conversations:list`
   - `users:list`
5. **Install to Workspace** 클릭
6. Bot User OAuth Token 복사

## 3단계: 실행

### 3.1 사용 가능한 채널 보기

```bash
python main.py --list
```

### 3.2 모든 채널 아카이브

```bash
python main.py --all
```

### 3.3 특정 채널만 아카이브

```bash
python main.py --channel general
```

### 3.4 결과 확인

`archives/` 디렉토리에 JSON 파일들이 생성됩니다:

```
archives/
├── general_20251031_143022.json
├── marketing_20251031_143045.json
└── INDEX.json
```

## 4단계: 데이터 분석

### 4.1 Python에서 데이터 검색

```python
from src.reader import ArchiveReader

reader = ArchiveReader()
stats = reader.get_statistics('archives/general_20251031_143022.json')
print(f"총 메시지: {stats['total_messages']}")
```

### 4.2 CSV로 내보내기

```python
reader.export_to_csv(
    'archives/general_20251031_143022.json',
    'archives/general.csv'
)
```

## 자주 사용되는 명령어

| 명령 | 설명 |
|------|------|
| `python main.py --list` | 채널 목록 보기 |
| `python main.py --all` | 모든 채널 아카이브 |
| `python main.py --channel general` | general 채널만 아카이브 |
| `python main.py --all --no-threads` | 스레드 제외하고 아카이브 |
| `python main.py --all --index` | 아카이브 후 인덱스 생성 |
| `python main.py --all -v` | 상세 로그와 함께 실행 |

## 트러블슈팅

### Token 오류

```bash
# 환경변수 확인
echo $SLACK_BOT_TOKEN

# 또는 직접 전달
python main.py --token xoxb-xxxx --list
```

### 권한 부족 오류

Bot에 필요한 scopes이 설정되어 있는지 확인:
- [Slack API 콘솔](https://api.slack.com/apps)에서 확인
- 필요한 scopes를 추가한 후 **Reinstall to Workspace**

### 채널을 찾을 수 없음

먼저 채널 목록을 확인:

```bash
python main.py --list
```

정확한 채널 이름이나 ID를 사용하세요.

## 다음 단계

- 예제 코드 참고: `examples/` 디렉토리
- 상세 문서: `README.md`
- API 문서: [Python Slack SDK](https://slack.dev/python-slack-sdk/)

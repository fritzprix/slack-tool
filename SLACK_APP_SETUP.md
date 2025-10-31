# Slack App 생성 및 설정 가이드

## 1. Slack 앱 생성

1. [Slack API 웹사이트](https://api.slack.com/apps)에 접속합니다.
2. **"Create New App"** 버튼을 클릭합니다.
3. **"From an app manifest"** 옵션을 선택합니다.
4. 워크스페이스를 선택합니다.
5. 아래 manifest 내용을 복사해서 붙여넣습니다:
   - JSON 형식: `slack-app-manifest.json` 파일 내용
   - YAML 형식: `slack-app-manifest.yaml` 파일 내용

## 2. 앱 설정 완료

1. manifest를 붙여넣은 후 **"Next"** 버튼을 클릭합니다.
2. 앱 정보를 검토하고 **"Create"** 버튼을 클릭합니다.
3. **"Install to Workspace"** 버튼을 클릭하여 워크스페이스에 앱을 설치합니다.

## 3. Bot Token 획득

1. 앱이 설치된 후, 왼쪽 메뉴에서 **"OAuth & Permissions"**를 클릭합니다.
2. **"Bot User OAuth Token"** (xoxb-로 시작)을 복사합니다.
3. `.env` 파일에 토큰을 설정합니다:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token-here
   ```

## 4. 권한 설명

이 앱에 부여되는 권한들:

### Bot Token Scopes:
- **channels:history**: 공개 채널의 메시지 히스토리 읽기
- **channels:read**: 공개 채널 정보 읽기
- **groups:history**: 비공개 채널의 메시지 히스토리 읽기
- **groups:read**: 비공개 채널 정보 읽기
- **im:history**: 다이렉트 메시지 히스토리 읽기
- **im:read**: 다이렉트 메시지 정보 읽기
- **mpim:history**: 그룹 다이렉트 메시지 히스토리 읽기
- **mpim:read**: 그룹 다이렉트 메시지 정보 읽기
- **users:read**: 사용자 정보 읽기 (사용자명 매핑용)

## 5. 주의사항

- 이 앱은 **읽기 전용** 권한만을 요청합니다.
- 메시지를 수정하거나 삭제할 수 없습니다.
- 새로운 메시지를 보낼 수 없습니다.
- 비공개 채널의 경우, 봇이 해당 채널에 초대되어야 합니다.

## 6. 사용법

앱 설치가 완료되면 다음과 같이 사용할 수 있습니다:

```bash
# 모든 채널 아카이브
python main.py --all

# 특정 채널 아카이브
python main.py --channel C123456789

# 채널 목록 확인
python main.py --list
```

자세한 사용법은 `QUICKSTART.md` 파일을 참조하세요.
"""
예제 1: Python 코드에서 직접 사용하기
"""

from src.archiver import SlackArchiver
import os

# 토큰 설정
token = os.getenv('SLACK_BOT_TOKEN')
if not token:
    raise ValueError("SLACK_BOT_TOKEN 환경변수를 설정해주세요")

# Archiver 초기화
archiver = SlackArchiver(token=token, archive_dir='archives')

# 1. 모든 채널 아카이브
# saved_files = archiver.archive_all_channels()
# print(f"아카이브된 파일: {saved_files}")

# 2. 특정 채널 아카이브
# filepath = archiver.archive_channel('C123456789', 'general')
# print(f"저장된 파일: {filepath}")

# 3. 사용 가능한 채널 목록 가져오기
channels = archiver.get_all_channels()
print(f"사용 가능한 채널 ({len(channels)}개):")
for ch in channels[:5]:  # 처음 5개만 출력
    print(f"  - #{ch['name']} ({ch['id']})")

# 4. 특정 채널의 메시지 가져오기
# messages = archiver.get_channel_history('C123456789')
# print(f"메시지 개수: {len(messages)}")

# 5. 인덱스 파일 생성
# index_file = archiver.create_index()
# print(f"인덱스 파일 생성: {index_file}")

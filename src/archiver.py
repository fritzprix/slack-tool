"""
Slack Conversation History Archiver

이 모듈은 Slack 워크스페이스의 대화 내역을 JSON 파일로 저장하는 기능을 제공합니다.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlackArchiver:
    """Slack 대화 히스토리를 archive하는 클래스"""
    
    def __init__(self, token: str, archive_dir: str = "archives"):
        """
        SlackArchiver 초기화
        
        Args:
            token: Slack Bot Token (SLACK_BOT_TOKEN 환경변수에서도 가져올 수 있음)
            archive_dir: 아카이브 파일을 저장할 디렉토리
        """
        self.client = WebClient(token=token)
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(exist_ok=True)
        
        # 사용자 정보 캐시
        self.users_cache: Dict[str, str] = {}
        self._load_users_cache()
        
        logger.info(f"SlackArchiver initialized with archive directory: {self.archive_dir}")
    
    def _load_users_cache(self) -> None:
        """사용자 정보를 캐시에 로드"""
        try:
            cursor = None
            while True:
                response = self.client.users_list(cursor=cursor, limit=200)
                
                for user in response.get('members', []):
                    user_id = user.get('id')
                    user_name = user.get('real_name') or user.get('name', 'Unknown')
                    self.users_cache[user_id] = user_name
                
                # 다음 페이지 확인
                if not response.get('response_metadata', {}).get('next_cursor'):
                    break
                cursor = response['response_metadata']['next_cursor']
                
            logger.info(f"Loaded {len(self.users_cache)} users into cache")
        except SlackApiError as e:
            logger.warning(f"Failed to load users cache: {e}")
    
    def _get_user_name(self, user_id: str) -> str:
        """사용자 ID를 사용자 이름으로 변환"""
        return self.users_cache.get(user_id, user_id)
    
    def get_all_channels(self, exclude_archived: bool = True) -> List[Dict[str, Any]]:
        """
        워크스페이스의 모든 채널 목록 가져오기
        
        Args:
            exclude_archived: 아카이브된 채널 제외 여부
            
        Returns:
            채널 정보 딕셔너리 리스트
        """
        all_channels = []
        cursor = None
        
        try:
            while True:
                response = self.client.conversations_list(
                    types="public_channel,private_channel",
                    exclude_archived=exclude_archived,
                    cursor=cursor,
                    limit=200
                )
                
                channels = response.get('channels', [])
                all_channels.extend(channels)
                
                logger.info(f"Retrieved {len(channels)} channels")
                
                # 다음 페이지 확인
                if not response.get('response_metadata', {}).get('next_cursor'):
                    break
                cursor = response['response_metadata']['next_cursor']
                time.sleep(0.5)  # Rate limiting
                
        except SlackApiError as e:
            logger.error(f"Error retrieving channels: {e}")
        
        return all_channels
    
    def get_channel_history(
        self,
        channel_id: str,
        oldest: Optional[str] = None,
        latest: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        특정 채널의 메시지 히스토리 가져오기
        
        Args:
            channel_id: 채널 ID
            oldest: 가장 오래된 메시지의 Unix timestamp (문자열)
            latest: 가장 최신 메시지의 Unix timestamp (문자열)
            
        Returns:
            메시지 딕셔너리 리스트 (시간순 정렬)
        """
        all_messages = []
        cursor = None
        
        try:
            while True:
                response = self.client.conversations_history(
                    channel=channel_id,
                    oldest=oldest,
                    latest=latest,
                    cursor=cursor,
                    limit=100
                )
                
                messages = response.get('messages', [])
                all_messages.extend(messages)
                
                logger.debug(f"Retrieved {len(messages)} messages from {channel_id}")
                
                # 다음 페이지 확인
                if not response.get('has_more'):
                    break
                cursor = response.get('response_metadata', {}).get('next_cursor')
                time.sleep(0.5)  # Rate limiting
                
        except SlackApiError as e:
            logger.error(f"Error retrieving history for channel {channel_id}: {e}")
        
        # 메시지를 시간순으로 정렬 (오래된 것부터)
        all_messages.sort(key=lambda m: float(m.get('ts', 0)))
        
        return all_messages
    
    def get_thread_messages(self, channel_id: str, thread_ts: str) -> List[Dict[str, Any]]:
        """
        특정 스레드의 메시지 가져오기
        
        Args:
            channel_id: 채널 ID
            thread_ts: 스레드 타임스탬프
            
        Returns:
            스레드 메시지 딕셔너리 리스트
        """
        all_messages = []
        cursor = None
        
        try:
            while True:
                response = self.client.conversations_replies(
                    channel=channel_id,
                    ts=thread_ts,
                    cursor=cursor,
                    limit=100
                )
                
                messages = response.get('messages', [])
                all_messages.extend(messages)
                
                logger.debug(f"Retrieved {len(messages)} thread messages")
                
                # 다음 페이지 확인
                if not response.get('has_more'):
                    break
                cursor = response.get('response_metadata', {}).get('next_cursor')
                time.sleep(0.5)  # Rate limiting
                
        except SlackApiError as e:
            logger.error(f"Error retrieving thread messages: {e}")
        
        return all_messages
    
    def _enrich_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """메시지에 사용자 이름 등의 추가 정보를 포함"""
        if 'user' in message:
            message['user_name'] = self._get_user_name(message['user'])
        
        # 스레드 정보 추가
        if 'reply_count' in message and message['reply_count'] > 0:
            message['_has_thread'] = True
        
        # 타임스탬프를 읽을 수 있는 날짜로 변환
        if 'ts' in message:
            try:
                ts = float(message['ts'])
                message['timestamp_readable'] = datetime.fromtimestamp(ts).isoformat()
            except (ValueError, OSError) as e:
                logger.debug(f"Failed to convert timestamp: {e}")
        
        return message
    
    def get_archive_stats(self) -> Dict[str, Any]:
        """
        아카이브 디렉토리의 통계 정보 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        stats = {
            'total_archives': 0,
            'total_messages': 0,
            'total_size_bytes': 0,
            'channels': []
        }
        
        for filepath in self.archive_dir.glob('*.json'):
            if filepath.name == 'INDEX.json':
                continue
                
            try:
                stats['total_archives'] += 1
                stats['total_size_bytes'] += filepath.stat().st_size
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    message_count = data.get('message_count', 0)
                    stats['total_messages'] += message_count
                    stats['channels'].append({
                        'name': data.get('metadata', {}).get('channel_name'),
                        'messages': message_count
                    })
            except Exception as e:
                logger.warning(f"Failed to read {filepath}: {e}")
        
        stats['total_size_mb'] = round(stats['total_size_bytes'] / 1024 / 1024, 2)
        return stats
    
    def archive_channel(
        self,
        channel_id: str,
        channel_name: str,
        include_threads: bool = True
    ) -> Optional[str]:
        """
        특정 채널을 아카이브
        
        Args:
            channel_id: 채널 ID
            channel_name: 채널 이름
            include_threads: 스레드 메시지 포함 여부
            
        Returns:
            저장된 파일 경로
        """
        logger.info(f"Archiving channel: #{channel_name} ({channel_id})")
        
        # 채널 정보 가져오기
        try:
            channel_info = self.client.conversations_info(channel=channel_id)
            channel_data = channel_info['channel']
        except SlackApiError as e:
            logger.error(f"Failed to get channel info for {channel_id}: {e}")
            return None
        
        # 메시지 가져오기
        messages = self.get_channel_history(channel_id)
        
        # 스레드 메시지 포함
        if include_threads:
            for i, message in enumerate(messages):
                if message.get('reply_count', 0) > 0:
                    thread_messages = self.get_thread_messages(channel_id, message['ts'])
                    messages[i]['thread_messages'] = thread_messages
        
        # 메시지 정보 강화
        enriched_messages = [self._enrich_message(msg) for msg in messages]
        
        # 아카이브 데이터 구성
        archive_data = {
            'metadata': {
                'archived_at': datetime.now().isoformat(),
                'channel_id': channel_id,
                'channel_name': channel_name,
                'channel_topic': channel_data.get('topic', {}).get('value', ''),
                'channel_purpose': channel_data.get('purpose', {}).get('value', ''),
                'is_private': channel_data.get('is_private', False),
                'created': channel_data.get('created'),
                'member_count': channel_data.get('num_members', 0),
            },
            'messages': enriched_messages,
            'message_count': len(enriched_messages),
        }
        
        # 파일명 생성
        safe_channel_name = channel_name.replace('/', '-').replace('\\', '-')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_channel_name}_{timestamp}.json"
        filepath = self.archive_dir / filename
        
        # 파일 저장
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Archived {len(enriched_messages)} messages to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save archive file: {e}")
            return None
    
    def archive_all_channels(
        self,
        exclude_archived: bool = True,
        include_threads: bool = True
    ) -> List[str]:
        """
        모든 채널을 아카이브
        
        Args:
            exclude_archived: 아카이브된 채널 제외 여부
            include_threads: 스레드 메시지 포함 여부
            
        Returns:
            저장된 파일 경로 리스트
        """
        channels = self.get_all_channels(exclude_archived=exclude_archived)
        saved_files = []
        failed_channels = []
        
        total = len(channels)
        logger.info(f"Starting to archive {total} channels")
        
        for i, channel in enumerate(channels, 1):
            channel_id = channel['id']
            channel_name = channel['name']
            
            try:
                logger.info(f"[{i}/{total}] ({i*100//total}%) Processing channel: #{channel_name}")
                
                filepath = self.archive_channel(channel_id, channel_name, include_threads)
                if filepath:
                    saved_files.append(filepath)
                else:
                    failed_channels.append(channel_name)
                    
            except Exception as e:
                logger.error(f"Failed to archive channel #{channel_name}: {e}")
                failed_channels.append(channel_name)
                continue  # 다음 채널로 계속 진행
            
            # Rate limiting
            time.sleep(1)
        
        logger.info(f"Archiving completed. {len(saved_files)}/{total} channels archived.")
        if failed_channels:
            logger.warning(f"Failed channels ({len(failed_channels)}): {', '.join(failed_channels)}")
        
        return saved_files
    
    def create_index(self) -> Optional[str]:
        """
        아카이브 디렉토리의 인덱스 파일 생성
        
        Returns:
            생성된 인덱스 파일 경로
        """
        index_data = {
            'created_at': datetime.now().isoformat(),
            'archives': []
        }
        
        for filepath in sorted(self.archive_dir.glob('*.json')):
            # INDEX.json 자체는 제외
            if filepath.name == 'INDEX.json':
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    index_data['archives'].append({
                        'filename': filepath.name,
                        'channel_name': metadata.get('channel_name'),
                        'channel_id': metadata.get('channel_id'),
                        'message_count': data.get('message_count', 0),
                        'archived_at': metadata.get('archived_at'),
                        'file_path': str(filepath),
                    })
            except Exception as e:
                logger.warning(f"Failed to read {filepath}: {e}")
        
        index_filepath = self.archive_dir / 'INDEX.json'
        try:
            with open(index_filepath, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Created index file: {index_filepath}")
            return str(index_filepath)
        except Exception as e:
            logger.error(f"Failed to create index file: {e}")
            return None

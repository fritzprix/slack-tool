"""
아카이브된 데이터를 검색하고 분석하는 유틸리티
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ArchiveReader:
    """아카이브 파일을 읽고 분석"""
    
    def __init__(self, archive_dir: str = "archives"):
        self.archive_dir = Path(archive_dir)
    
    def load_archive(self, filepath: str) -> Optional[Dict[str, Any]]:
        """아카이브 파일 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load archive: {e}")
            return None
    
    def search_messages(
        self,
        filepath: str,
        keyword: str,
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        아카이브에서 키워드로 메시지 검색
        
        Args:
            filepath: 아카이브 파일 경로
            keyword: 검색 키워드
            case_sensitive: 대소문자 구분 여부
            
        Returns:
            매칭된 메시지 리스트
        """
        archive = self.load_archive(filepath)
        if not archive:
            return []
        
        messages = archive.get('messages', [])
        results = []
        
        search_text = keyword if case_sensitive else keyword.lower()
        
        for msg in messages:
            text = msg.get('text', '')
            compare_text = text if case_sensitive else text.lower()
            
            if search_text in compare_text:
                results.append(msg)
        
        return results
    
    def search_by_user(
        self,
        filepath: str,
        user_name: str
    ) -> List[Dict[str, Any]]:
        """사용자가 작성한 메시지 검색"""
        archive = self.load_archive(filepath)
        if not archive:
            return []
        
        messages = archive.get('messages', [])
        return [msg for msg in messages if msg.get('user_name') == user_name]
    
    def get_message_count(self, filepath: str) -> int:
        """메시지 개수 조회"""
        archive = self.load_archive(filepath)
        return archive.get('message_count', 0) if archive else 0
    
    def get_channel_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """채널 메타데이터 조회"""
        archive = self.load_archive(filepath)
        return archive.get('metadata') if archive else None
    
    def list_archives(self) -> List[Dict[str, Any]]:
        """아카이브 목록 조회"""
        archives = []
        
        for filepath in sorted(self.archive_dir.glob('*.json')):
            if filepath.name == 'INDEX.json':
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    archives.append({
                        'filename': filepath.name,
                        'channel_name': metadata.get('channel_name'),
                        'message_count': data.get('message_count', 0),
                        'archived_at': metadata.get('archived_at'),
                    })
            except Exception as e:
                logger.warning(f"Failed to read {filepath}: {e}")
        
        return archives
    
    def export_to_csv(
        self,
        filepath: str,
        output_filepath: str
    ) -> bool:
        """
        아카이브를 CSV 파일로 내보내기
        
        Args:
            filepath: 아카이브 파일 경로
            output_filepath: 출력 CSV 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            import csv
            
            archive = self.load_archive(filepath)
            if not archive:
                return False
            
            messages = archive.get('messages', [])
            
            with open(output_filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'user_name', 'text', 'reply_count']
                )
                writer.writeheader()
                
                for msg in messages:
                    writer.writerow({
                        'timestamp': msg.get('timestamp_readable', ''),
                        'user_name': msg.get('user_name', ''),
                        'text': msg.get('text', ''),
                        'reply_count': msg.get('reply_count', 0),
                    })
            
            logger.info(f"Exported {len(messages)} messages to {output_filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False
    
    def get_statistics(self, filepath: str) -> Optional[Dict[str, Any]]:
        """아카이브 통계 계산"""
        archive = self.load_archive(filepath)
        if not archive:
            return None
        
        messages = archive.get('messages', [])
        metadata = archive.get('metadata', {})
        
        user_message_count = {}
        total_threads = 0
        
        for msg in messages:
            user_name = msg.get('user_name', 'Unknown')
            user_message_count[user_name] = user_message_count.get(user_name, 0) + 1
            
            if msg.get('thread_messages'):
                total_threads += 1
        
        # 상위 사용자
        top_users = sorted(
            user_message_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'channel_name': metadata.get('channel_name'),
            'total_messages': len(messages),
            'unique_users': len(user_message_count),
            'total_threads': total_threads,
            'member_count': metadata.get('member_count'),
            'top_users': top_users,
            'archived_at': metadata.get('archived_at'),
        }

#!/usr/bin/env python3
"""
Slack Archive Tool 테스트 스크립트

이 스크립트는 토큰이 유효한지, 기본 기능이 작동하는지 테스트합니다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.archiver import SlackArchiver


def test_connection(token: str) -> bool:
    """Slack API 연결 테스트"""
    print("🔍 Slack API 연결 테스트 중...")
    try:
        archiver = SlackArchiver(token=token, archive_dir='test_archives')
        print(f"✅ 연결 성공! {len(archiver.users_cache)}명의 사용자 정보 로드됨")
        return True
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False


def test_channel_list(token: str) -> bool:
    """채널 목록 조회 테스트"""
    print("\n🔍 채널 목록 조회 테스트 중...")
    try:
        archiver = SlackArchiver(token=token, archive_dir='test_archives')
        channels = archiver.get_all_channels()
        
        if channels:
            print(f"✅ {len(channels)}개 채널 조회 성공")
            print("\n처음 5개 채널:")
            for ch in channels[:5]:
                print(f"  - #{ch['name']} ({ch.get('num_members', 0)}명)")
            return True
        else:
            print("⚠️  채널이 없거나 권한이 부족합니다")
            return False
    except Exception as e:
        print(f"❌ 채널 목록 조회 실패: {e}")
        return False


def test_archive_stats(token: str) -> bool:
    """아카이브 통계 테스트"""
    print("\n🔍 아카이브 통계 기능 테스트 중...")
    try:
        archiver = SlackArchiver(token=token, archive_dir='archives')
        stats = archiver.get_archive_stats()
        
        print(f"✅ 통계 조회 성공")
        print(f"  - 총 아카이브: {stats['total_archives']}개")
        print(f"  - 총 메시지: {stats['total_messages']}개")
        print(f"  - 총 크기: {stats['total_size_mb']} MB")
        return True
    except Exception as e:
        print(f"❌ 통계 조회 실패: {e}")
        return False


def main():
    print("=" * 60)
    print("Slack Archive Tool - 테스트 스크립트")
    print("=" * 60)
    
    # 토큰 확인
    token = os.getenv('SLACK_BOT_TOKEN')
    if not token:
        print("\n❌ SLACK_BOT_TOKEN 환경변수가 설정되지 않았습니다.")
        print("   다음 명령으로 설정하세요:")
        print("   export SLACK_BOT_TOKEN='xoxb-your-token'")
        return 1
    
    print(f"\n✅ 토큰 발견: {token[:20]}...")
    
    # 테스트 실행
    results = []
    
    results.append(("API 연결", test_connection(token)))
    results.append(("채널 목록", test_channel_list(token)))
    results.append(("아카이브 통계", test_archive_stats(token)))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status} - {test_name}")
    
    print(f"\n총 {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("\n🎉 모든 테스트가 통과했습니다!")
        return 0
    else:
        print("\n⚠️  일부 테스트가 실패했습니다.")
        print("   README.md의 트러블슈팅 섹션을 참고하세요.")
        return 1


if __name__ == '__main__':
    exit(main())

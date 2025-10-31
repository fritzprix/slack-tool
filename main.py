"""
Slack Archive Tool - 메인 실행 파일

사용법:
    python -m slack_tool.main --token YOUR_TOKEN --all
    python -m slack_tool.main --token YOUR_TOKEN --channel CHANNEL_ID
"""

import os
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

from src.archiver import SlackArchiver
from src.converter import SlackArchiveConverter

# .env 파일 로드
load_dotenv()


def setup_logging(verbose: bool = False) -> None:
    """로깅 설정"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    parser = argparse.ArgumentParser(
        description='Slack 대화 히스토리를 JSON 파일로 아카이브합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 모든 채널 아카이브
  python main.py --token xoxb-xxxx --all
  
  # 봇이 속한 채널만 아카이브
  python main.py --token xoxb-xxxx --all --only-joined
  
  # 특정 채널 아카이브
  python main.py --token xoxb-xxxx --channel C123456789
  
  # 여러 채널 아카이브
  python main.py --token xoxb-xxxx --channels C123456789 C987654321
  
  # 봇이 속한 채널 목록 확인
  python main.py --list --only-joined
  
  # JSON 아카이브를 HTML로 변환
  python main.py --convert archive.json
  
  # JSON 아카이브를 모든 형식으로 변환
  python main.py --convert archive.json --convert-format all
  
  # 환경변수에서 토큰 읽기
  export SLACK_BOT_TOKEN=xoxb-xxxx
  python main.py --all --only-joined
        """
    )
    
    # 토큰 옵션
    parser.add_argument(
        '--token',
        help='Slack Bot Token (또는 SLACK_BOT_TOKEN 환경변수 사용)',
        default=os.getenv('SLACK_BOT_TOKEN')
    )
    
    # 아카이브 디렉토리
    parser.add_argument(
        '--archive-dir',
        help='아카이브 파일을 저장할 디렉토리',
        default='archives'
    )
    
    # 모드 선택 (상호배타적)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--all',
        action='store_true',
        help='모든 채널 아카이브'
    )
    mode_group.add_argument(
        '--channel',
        help='특정 채널 아카이브 (채널 ID 또는 이름)'
    )
    mode_group.add_argument(
        '--channels',
        nargs='+',
        help='여러 채널 아카이브'
    )
    mode_group.add_argument(
        '--list',
        action='store_true',
        help='사용 가능한 채널 목록 출력'
    )
    mode_group.add_argument(
        '--convert',
        help='JSON 아카이브 파일을 읽기 쉬운 형태로 변환'
    )
    
    # 추가 옵션
    parser.add_argument(
        '--no-threads',
        action='store_true',
        help='스레드 메시지 제외'
    )
    parser.add_argument(
        '--include-archived',
        action='store_true',
        help='아카이브된 채널도 포함'
    )
    parser.add_argument(
        '--only-joined',
        action='store_true',
        help='봇이 속한 채널만 포함'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='상세 로그 출력'
    )
    parser.add_argument(
        '--index',
        action='store_true',
        help='아카이브 인덱스 생성'
    )
    parser.add_argument(
        '--convert-format',
        choices=['html', 'markdown', 'text', 'all'],
        default='html',
        help='변환 형식 (기본값: html)'
    )
    
    args = parser.parse_args()
    
    # 로깅 설정
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # 토큰 확인
    if not args.token:
        parser.error('토큰이 필요합니다. --token을 사용하거나 SLACK_BOT_TOKEN 환경변수를 설정하세요.')
    
    # Archiver 초기화
    archiver = SlackArchiver(token=args.token, archive_dir=args.archive_dir)
    
    try:
        # 모든 채널 목록
        if args.list:
            channels = archiver.get_all_channels(
                exclude_archived=not args.include_archived,
                only_joined=args.only_joined
            )
            channel_type = "봇이 속한 채널" if args.only_joined else "사용 가능한 채널"
            print(f"\n{channel_type} ({len(channels)}개):")
            print("-" * 60)
            for ch in sorted(channels, key=lambda x: x['name']):
                archived = " [ARCHIVED]" if ch.get('is_archived') else ""
                members = ch.get('num_members', 0)
                print(f"  {ch['name']:30} ({ch['id']:12})  {members}명{archived}")
            print("-" * 60)
        
        # 모든 채널 아카이브
        elif args.all:
            saved_files = archiver.archive_all_channels(
                exclude_archived=not args.include_archived,
                include_threads=not args.no_threads,
                only_joined=args.only_joined
            )
            print(f"\n✓ {len(saved_files)}개 채널을 아카이브했습니다.")
            for filepath in saved_files:
                print(f"  - {filepath}")
        
        # 특정 채널 아카이브
        elif args.channel:
            channels = archiver.get_all_channels(
                exclude_archived=not args.include_archived,
                only_joined=args.only_joined
            )
            
            # 채널 이름이나 ID로 채널 찾기
            channel = None
            for ch in channels:
                if ch['id'] == args.channel or ch['name'] == args.channel:
                    channel = ch
                    break
            
            if not channel:
                print(f"✗ 채널을 찾을 수 없습니다: {args.channel}")
                return 1
            
            filepath = archiver.archive_channel(
                channel['id'],
                channel['name'],
                include_threads=not args.no_threads
            )
            if filepath:
                print(f"✓ 채널 '#{channel['name']}'을 아카이브했습니다: {filepath}")
            else:
                return 1
        
        # 여러 채널 아카이브
        elif args.channels:
            channels = archiver.get_all_channels(
                exclude_archived=not args.include_archived,
                only_joined=args.only_joined
            )
            channel_map = {ch['id']: ch for ch in channels}
            channel_map.update({ch['name']: ch for ch in channels})
            
            saved_files = []
            for i, channel_id in enumerate(args.channels, 1):
                channel = channel_map.get(channel_id)
                if not channel:
                    print(f"✗ 채널을 찾을 수 없습니다: {channel_id}")
                    continue
                
                print(f"[{i}/{len(args.channels)}] 처리 중: #{channel['name']}")
                filepath = archiver.archive_channel(
                    channel['id'],
                    channel['name'],
                    include_threads=not args.no_threads
                )
                if filepath:
                    saved_files.append(filepath)
            
            print(f"\n✓ {len(saved_files)}개 채널을 아카이브했습니다.")
        
        # JSON 아카이브 변환
        elif args.convert:
            if not os.path.exists(args.convert):
                print(f"✗ 파일을 찾을 수 없습니다: {args.convert}")
                return 1
            
            converter = SlackArchiveConverter()
            archive_data = converter.load_archive(args.convert)
            
            input_path = Path(args.convert)
            output_base = input_path.stem
            
            if args.convert_format == 'html' or args.convert_format == 'all':
                output_path = f"{output_base}.html"
                converter.convert_to_html(archive_data, output_path)
                print(f"✓ HTML 파일 생성: {output_path}")
            
            if args.convert_format == 'markdown' or args.convert_format == 'all':
                output_path = f"{output_base}.md"
                converter.convert_to_markdown(archive_data, output_path)
                print(f"✓ Markdown 파일 생성: {output_path}")
            
            if args.convert_format == 'text' or args.convert_format == 'all':
                output_path = f"{output_base}.txt"
                converter.convert_to_text(archive_data, output_path)
                print(f"✓ Text 파일 생성: {output_path}")
        
        # 인덱스 생성
        if args.index:
            index_file = archiver.create_index()
            if index_file:
                print(f"\n✓ 인덱스 파일을 생성했습니다: {index_file}")
    
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
        return 130
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=args.verbose)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

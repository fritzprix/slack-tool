"""
예제 2: 아카이브된 데이터 검색 및 분석
"""

from src.reader import ArchiveReader

# Reader 초기화
reader = ArchiveReader(archive_dir='archives')

# 1. 아카이브 목록 조회
archives = reader.list_archives()
print("아카이브된 채널:")
for archive in archives:
    print(f"  - {archive['channel_name']}: {archive['message_count']}개 메시지")

# 2. 특정 아카이브에서 통계 조회
if archives:
    filepath = archives[0]['filename']
    stats = reader.get_statistics(f'archives/{filepath}')
    if stats:
        print(f"\n채널 '{stats['channel_name']}' 통계:")
        print(f"  - 총 메시지: {stats['total_messages']}")
        print(f"  - 사용자 수: {stats['unique_users']}")
        print(f"  - 스레드 수: {stats['total_threads']}")
        print(f"\n  상위 사용자:")
        for user, count in stats['top_users'][:5]:
            print(f"    - {user}: {count}개 메시지")

# 3. 메시지 검색
# keyword = "meeting"
# results = reader.search_messages(f'archives/{filepath}', keyword)
# print(f"\n'{keyword}'를 포함한 메시지 ({len(results)}개):")
# for msg in results[:3]:
#     print(f"  - {msg['user_name']}: {msg['text'][:50]}...")

# 4. 특정 사용자의 메시지 검색
# user_messages = reader.search_by_user(f'archives/{filepath}', 'John Doe')
# print(f"\nJohn Doe의 메시지 ({len(user_messages)}개)")

# 5. CSV로 내보내기
# reader.export_to_csv(f'archives/{filepath}', f'archives/{filepath.replace(".json", ".csv")}')
# print("\nCSV 파일로 내보냈습니다!")

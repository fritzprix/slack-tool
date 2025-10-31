"""
Slack Archive JSON을 읽기 쉬운 형태로 변환하는 모듈

지원 형식:
- HTML: 웹브라우저에서 볼 수 있는 채팅 형태
- Markdown: GitHub, 노션 등에서 읽기 쉬운 형태  
- Text: 단순한 채팅 로그 형태
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import unquote


class SlackArchiveConverter:
    """Slack 아카이브 JSON을 다양한 형식으로 변환하는 클래스"""
    
    def __init__(self):
        self.emoji_pattern = re.compile(r':([a-zA-Z0-9_+-]+):')
        self.user_mention_pattern = re.compile(r'<@([A-Z0-9]+)(\|[^>]+)?>')
        self.channel_mention_pattern = re.compile(r'<#([A-Z0-9]+)(\|[^>]+)?>')
        self.url_pattern = re.compile(r'<(https?://[^|>]+)(\|([^>]+))?>')
    
    def load_archive(self, json_path: str) -> Dict[str, Any]:
        """JSON 아카이브 파일 로드"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def format_text(self, text: str, format_type: str = 'html') -> str:
        """Slack 텍스트 포맷팅 변환"""
        if not text:
            return ""
        
        # URL 링크 변환
        if format_type == 'html':
            text = self.url_pattern.sub(r'<a href="\1" target="_blank">\3</a>', text)
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        elif format_type == 'markdown':
            text = self.url_pattern.sub(r'[\3](\1)', text)
        
        # 사용자 멘션 변환
        text = self.user_mention_pattern.sub(r'@\1', text)
        
        # 채널 멘션 변환  
        text = self.channel_mention_pattern.sub(r'#\1', text)
        
        # 이모지는 그대로 유지
        
        # 볼드/이탤릭 변환
        if format_type == 'html':
            text = re.sub(r'\*([^*]+)\*', r'<strong>\1</strong>', text)
            text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
            text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        elif format_type == 'markdown':
            # 마크다운은 그대로 유지
            pass
        
        return text
    
    def convert_to_html(self, archive_data: Dict[str, Any], output_path: str) -> None:
        """HTML 형식으로 변환"""
        metadata = archive_data['metadata']
        messages = archive_data['messages']
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>#{metadata['channel_name']} - Slack Archive</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .message {{
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .message-header {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        .username {{
            font-weight: bold;
            color: #1264a3;
            margin-right: 10px;
        }}
        .timestamp {{
            color: #616061;
            font-size: 12px;
        }}
        .message-text {{
            line-height: 1.4;
        }}
        .system-message {{
            background: #f1f2f3;
            font-style: italic;
            color: #616061;
        }}
        .thread-reply {{
            margin-left: 20px;
            border-left: 3px solid #1264a3;
            padding-left: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>#{metadata['channel_name']}</h1>
        <p><strong>아카이브 생성일:</strong> {metadata['archived_at']}</p>
        <p><strong>채널 ID:</strong> {metadata['channel_id']}</p>
        <p><strong>메시지 수:</strong> {len(messages)}개</p>
        {f"<p><strong>채널 설명:</strong> {metadata.get('channel_topic', '')}</p>" if metadata.get('channel_topic') else ""}
    </div>
"""
        
        for msg in messages:
            css_class = "message"
            if msg.get('subtype') in ['channel_join', 'channel_leave', 'bot_add']:
                css_class += " system-message"
            
            username = msg.get('user_name', msg.get('user', 'Unknown'))
            timestamp = msg.get('timestamp_readable', msg.get('ts', ''))
            text = self.format_text(msg.get('text', ''), 'html')
            
            html_content += f"""
    <div class="{css_class}">
        <div class="message-header">
            <span class="username">{username}</span>
            <span class="timestamp">{timestamp}</span>
        </div>
        <div class="message-text">{text}</div>
"""
            
            # 스레드 답글 처리
            if 'replies' in msg and msg['replies']:
                for reply in msg['replies']:
                    reply_username = reply.get('user_name', reply.get('user', 'Unknown'))
                    reply_timestamp = reply.get('timestamp_readable', reply.get('ts', ''))
                    reply_text = self.format_text(reply.get('text', ''), 'html')
                    
                    html_content += f"""
        <div class="thread-reply">
            <div class="message-header">
                <span class="username">{reply_username}</span>
                <span class="timestamp">{reply_timestamp}</span>
            </div>
            <div class="message-text">{reply_text}</div>
        </div>
"""
            
            html_content += "    </div>\n"
        
        html_content += """
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def convert_to_markdown(self, archive_data: Dict[str, Any], output_path: str) -> None:
        """마크다운 형식으로 변환"""
        metadata = archive_data['metadata']
        messages = archive_data['messages']
        
        md_content = f"""# #{metadata['channel_name']}

**아카이브 정보:**
- 생성일: {metadata['archived_at']}
- 채널 ID: {metadata['channel_id']}
- 메시지 수: {len(messages)}개
- 프라이빗 채널: {'예' if metadata.get('is_private') else '아니오'}

---

"""
        
        for msg in messages:
            username = msg.get('user_name', msg.get('user', 'Unknown'))
            timestamp = msg.get('timestamp_readable', msg.get('ts', ''))
            text = self.format_text(msg.get('text', ''), 'markdown')
            
            # 시스템 메시지 처리
            if msg.get('subtype') in ['channel_join', 'channel_leave', 'bot_add']:
                md_content += f"*{timestamp}* - _{text}_\n\n"
            else:
                md_content += f"**{username}** _{timestamp}_\n\n{text}\n\n"
                
                # 스레드 답글 처리
                if 'replies' in msg and msg['replies']:
                    md_content += "**스레드 답글:**\n\n"
                    for reply in msg['replies']:
                        reply_username = reply.get('user_name', reply.get('user', 'Unknown'))
                        reply_timestamp = reply.get('timestamp_readable', reply.get('ts', ''))
                        reply_text = self.format_text(reply.get('text', ''), 'markdown')
                        
                        md_content += f"> **{reply_username}** _{reply_timestamp}_\n> \n> {reply_text}\n\n"
                
            md_content += "---\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def convert_to_text(self, archive_data: Dict[str, Any], output_path: str) -> None:
        """텍스트 형식으로 변환"""
        metadata = archive_data['metadata']
        messages = archive_data['messages']
        
        text_content = f"""Slack Archive - #{metadata['channel_name']}
아카이브 생성일: {metadata['archived_at']}
채널 ID: {metadata['channel_id']}
메시지 수: {len(messages)}개

{'='*60}

"""
        
        for msg in messages:
            username = msg.get('user_name', msg.get('user', 'Unknown'))
            timestamp = msg.get('timestamp_readable', msg.get('ts', ''))
            text = msg.get('text', '')
            
            # 텍스트 포맷 정리
            text = self.user_mention_pattern.sub(r'@\1', text)
            text = self.channel_mention_pattern.sub(r'#\1', text)
            text = self.url_pattern.sub(r'\1', text)
            
            if msg.get('subtype') in ['channel_join', 'channel_leave', 'bot_add']:
                text_content += f"[{timestamp}] {text}\n"
            else:
                text_content += f"[{timestamp}] {username}: {text}\n"
                
                # 스레드 답글 처리
                if 'replies' in msg and msg['replies']:
                    for reply in msg['replies']:
                        reply_username = reply.get('user_name', reply.get('user', 'Unknown'))
                        reply_timestamp = reply.get('timestamp_readable', reply.get('ts', ''))
                        reply_text = reply.get('text', '')
                        reply_text = self.user_mention_pattern.sub(r'@\1', reply_text)
                        reply_text = self.channel_mention_pattern.sub(r'#\1', reply_text)
                        
                        text_content += f"    └─ [{reply_timestamp}] {reply_username}: {reply_text}\n"
            
            text_content += "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)


def main():
    """CLI 인터페이스"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Slack 아카이브를 읽기 쉬운 형태로 변환')
    parser.add_argument('input_file', help='입력 JSON 파일 경로')
    parser.add_argument('-f', '--format', choices=['html', 'markdown', 'text', 'all'], 
                       default='html', help='출력 형식 (기본값: html)')
    parser.add_argument('-o', '--output', help='출력 파일 경로 (확장자 제외)')
    
    args = parser.parse_args()
    
    converter = SlackArchiveConverter()
    archive_data = converter.load_archive(args.input_file)
    
    input_path = Path(args.input_file)
    if args.output:
        output_base = args.output
    else:
        output_base = input_path.stem
    
    if args.format == 'html' or args.format == 'all':
        output_path = f"{output_base}.html"
        converter.convert_to_html(archive_data, output_path)
        print(f"HTML 파일 생성: {output_path}")
    
    if args.format == 'markdown' or args.format == 'all':
        output_path = f"{output_base}.md"
        converter.convert_to_markdown(archive_data, output_path)
        print(f"Markdown 파일 생성: {output_path}")
    
    if args.format == 'text' or args.format == 'all':
        output_path = f"{output_base}.txt"
        converter.convert_to_text(archive_data, output_path)
        print(f"Text 파일 생성: {output_path}")


if __name__ == "__main__":
    main()
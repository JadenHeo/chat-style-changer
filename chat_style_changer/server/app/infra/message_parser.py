import csv
import os
from datetime import datetime, timedelta
from io import StringIO
from typing import List, Optional

from app.models.message import Message
from fastapi import UploadFile


class MessageParser:
    """Parser for converting various formats into Message objects."""
    
    @staticmethod
    def from_csv(file_name: str, size: int = None, merge: bool = True) -> List[Message]:
        print(f"Parsing {file_name} with size {size} and merge {merge}")

        original_messages = []  # 원본 메시지 리스트
        merged_messages = []    # 병합된 메시지 리스트
        file_path = os.path.join("chat_style_changer", "server", "app", "resources", file_name)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                required_fields = {'timestamp', 'content', 'sender'}
                if not all(field in reader.fieldnames for field in required_fields):
                    raise ValueError(f"CSV must contain these columns: {required_fields}")
                
                merged_message: Optional[Message] = None
                merged_count = 0  # 현재 병합 중인 메시지 그룹의 메시지 수
                row_count = 0     # 처리한 전체 row 수
                
                for row in reader:
                    try:
                        row_count += 1
                        current_timestamp = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
                        
                        # 원본 메시지 추가
                        original_message = Message(
                            chatroom_id=1,
                            timestamp=current_timestamp,
                            sender=row['sender'],
                            content=row['content']
                        )
                        original_messages.append(original_message)
                        
                        if merged_message is None:
                            # First message
                            merged_message = original_message.model_copy()
                            merged_count = 1
                        else:
                            time_diff = current_timestamp - merged_message.timestamp
                            
                            if time_diff < timedelta(seconds=10):
                                # Merge content if within 10 seconds
                                merged_message.content += f"\n{row['content']}"
                                merged_message.timestamp = current_timestamp
                                merged_count += 1
                            else:
                                # Time gap is 10 seconds or more
                                if merged_count > 1:  # 2개 이상의 메시지가 병합된 경우만 추가
                                    merged_messages.append(merged_message.model_copy())
                                # Start new merged_message
                                merged_message = original_message.model_copy()
                                merged_count = 1
                        
                        # Check if we've reached the size limit
                        if size is not None and row_count >= size:
                            # 마지막 병합된 메시지 처리
                            if merged_message is not None and merged_count > 1:
                                merged_messages.append(merged_message.model_copy())
                            break
                            
                    except ValueError as e:
                        print(f"Warning: Skipping invalid row: {row}. Error: {str(e)}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

        # 최종 결과 반환
        return original_messages + merged_messages if merge else original_messages
    
    @staticmethod
    def from_str(str: str) -> List[Message]:
        try:
            context_messages = []
            reader = csv.reader(StringIO(str))

            for row in reader:
                context_messages.append(
                    Message(
                        chatroom_id=1,
                        timestamp=datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"),
                        sender=row[1],
                        content=row[2]
                    )
                )
            
            return context_messages
        
        except Exception as e:
            raise ValueError(f"Failed to parse string: {str}")
    
    @staticmethod
    async def extract_user_messages(self, file_: UploadFile, user_name: str) -> List[Message]:
        try:
            chatroom_id = file_.filename.split("_")[2]
            contents = await file_.read()
            reader = csv.reader(StringIO(contents.decode('utf-8')))
            user_messages = []
            for timestamp, sender, content in reader:
                if sender == user_name:
                    user_messages.append(
                        Message(
                            chatroom_id=chatroom_id,
                            timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                            sender=sender,
                            content=content
                        )
                    )
            return user_messages
        
        except Exception as e:
            raise ValueError(f"Failed to extract user messages: {str(e)}")

import json
import textwrap
from typing import List

from app.infra.llm import LLMService
from app.models.message import Message


class SpeechStyleConverter:
    def __init__(self, llm_service: LLMService):
        PROMPT_1 = textwrap.dedent(
            """\
            당신은 유저의 평소 말투를 반영해 주어진 문장을 유저의 말투대로 변경해주는 서비스입니다.
            유저가 여태까지 발화한 내용 중에 주어진 문장과 유사도가 높은 여러 표현들이 제공되고, 유저가 발화하기 전 어떤 대화의 맥락이 있었는지 역시 제공됩니다.
            유사도가 높은 여러 표현들은 줄바꿈을 포함하고 있을 수 있습니다. 따라서 구분 가능하도록 표현 사이에 공백의 줄을 하나씩 추가했습니다.
            이것을 기반으로, 주어진 문장을 유저의 말투대로 변경해주세요.
            대화의 맥락을 파악하고, 대화의 분위기로 부터 세 가지의 정도의 분위기를 자체적으로 선정하여 그 분위기를 기반으로 변경해주세요.

            주의사항:
            - 최종 결과는 json 형식으로 출력해주세요. 분위기를 key, 변경된 문장을 value로 출력해주세요.
            - 주어진 문장의 뜻을 변경하는 것이 아니라, 유저의 말투를 반영하는 것입니다. 절대 문장의 뜻은 변경하지 마세요.
            - 반드시 제공된 유저의 평소 표현들을 참고하여 변경해주세요.
            - 말투 변경을 할 떄, 줄바꿈이 필요하다고 생각하면 이를 추가해주세요. 연속된 여러 개의 말풍선으로 구성할 예정입니다.
            """
        )

        PROMPT_2 = textwrap.dedent(
            """\
            당신은 유저의 평소 말투를 반영해 주어진 문장을 유저의 말투대로 변경해주는 시스템입니다.

            당신에게 주어지는 정보는 다음과 같습니다.
            1. 유저가 여태까지 평소에 발화한 내용 중에 주어진 문장과 유사도가 높은 여러 표현들
            2. 유저가 발화하기 전 대화의 맥락을 보여주는 이전 채팅 메시지 리스트
            3. 말투를 반영하여 변경하고싶은 문장

            말투 변경 시 다음 지침을 반드시 지켜야 하며, 어느 것도 어겨서는 안 됩니다.

            [💡 지켜야 할 규칙]
            1. 문장의 "뜻"은 절대 변경하지 마세요.
            2. 유저의 말투(어미, 감정, 구어체)를 최대한 그대로 반영해야 합니다.
            3. 제공된 유사 표현을 반드시 참고하여 스타일을 따라야 합니다.
            4. 대화의 맥락을 파악하고, 대화의 분위기로 부터 세 가지의 정도의 분위기를 자체적으로 선정하여 그 분위기를 기반으로 변경해야합니다.
            5. 결과는 반드시 JSON 형식으로 출력해야 하며, 각 분위기를 key로, 문장을 value로 작성하세요.

            [🚫 금지사항]
            - 새로운 정보 추가 절대 금지
            - 문장의 내용 순서를 바꾸지 말 것


            [예시]
            입력: "오늘 회의는 없어요"
            출력: {
                "즐거운": "오늘 회의 없어요~",
                "가벼운": "오늘 회의 없어요ㅋㅋㅋ",
                "딱딱한": "오늘 회의는 없습니다."
            }

            ‼️ 이 지침은 절대 무시하거나 재해석해서는 안 됩니다. 어기는 경우 응답은 무효입니다.
            ‼️ 예시는 예시일 뿐, 말투 변경의 기준이 되는 세 가지 분위기는 이전 대화 문맥을 보고 스스로 판단하세요.
            """
        )

        self.llm_service = llm_service
        self.prompt = PROMPT_2
    
    def _create_input(self,
                      context_messages: List[Message],
                      target_sentence: str,
                      similar_utterances: List[str]) -> str:
        # 1. 대화 문맥 포맷
        formatted_context = "\n".join(
            f"{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {msg.sender}: {msg.content}"
            for msg in context_messages
        )

        # 2. 유사 발화 content만 추출
        formatted_similars = "\n\n".join(similar_utterances)
        return textwrap.dedent(
            f"""\
            이전 대화 문맥:
            {formatted_context}

            주어진 문장:
            {target_sentence}

            유사도가 높은 유저의 평소 발화 목록:
            {formatted_similars}
            """
        )
    
    def convert(self,
                context_messages: List[Message],
                target_sentence: str,
                similar_utterances: List[str]) -> dict:
        """
        주어진 문장을 유저의 말투로 변환합니다.
        
        Args:
            context_messages: 이전 대화 문맥
            target_sentence: 변환할 대상 문장
            similar_utterances: 유사도가 높은 유저의 평소 발화 목록
            
        Returns:
            str: 변환된 문장
        """
        input_ = self._create_input(
            context_messages=context_messages,
            target_sentence=target_sentence,
            similar_utterances=similar_utterances
        )

        print(f"Prompt: {self.prompt}")
        print(f"Input: {input_}")
        
        response = self.llm_service.generate_response(self.prompt, input_)
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as e:
            print("❌ JSON 파싱 실패:", e)
            print("응답 원문:", response)
            raise ValueError("LLM 응답을 JSON으로 파싱할 수 없습니다.")

        return parsed
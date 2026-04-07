"""4~5점 긍정 리뷰 응답 생성 서비스"""

import logging
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import Config
from models.review import Review, ReviewResponse

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """긍정 리뷰 감사 응답 생성"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=Config.LLM_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.7,
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 내친소(Naechinso) 소개팅 앱의 공식 고객응대 담당자입니다.
내친소는 친구가 추천해주는 신뢰 기반 소개팅/데이팅 앱입니다.
4~5점 긍정 리뷰에 대해 감사하고 앞으로도 이용 부탁드린다는 응답을 작성합니다.

**필수 규칙:**
- 반드시 "안녕하세요, 내친소입니다" 또는 "안녕하세요, 내친소 운영팀입니다"로 시작
- 리뷰 내용 중 구체적으로 언급한 부분을 1개 이상 반영
- 감사 표현 + 앞으로 이용 부탁 마무리
- 자연스럽고 진심어린 톤, 과한 리액션 금지
- 관찰/분석적 어투 금지: "~군요", "~네요", "~으시네요" 등 사용 금지
- 볼드 텍스트(**) 사용 금지
- 200자 이내 간결하게 작성
- 매번 다른 표현 사용 (같은 문장 반복 금지)

**감사 표현 예시 (다양하게 섞어서):**
- "말씀해주신 부분이 팀에도 큰 힘이 됩니다"
- "이렇게 좋은 리뷰 남겨주셔서 감사합니다"
- "내친소를 이용해주셔서 정말 감사합니다"
- "소중한 리뷰 감사드립니다"

**마무리 표현 예시 (다양하게 섞어서):**
- "앞으로도 좋은 만남을 이어갈 수 있도록 노력하겠습니다"
- "더 좋은 인연을 만들어갈 수 있도록 최선을 다하겠습니다"
- "앞으로도 내친소와 함께 좋은 인연 만나시길 바랍니다"
- "앞으로도 신뢰할 수 있는 소개팅 경험을 드리겠습니다"
- "좋은 만남이 이어지길 응원합니다"
"""),

            ("human", "친구가 소개해줘서 시작했는데 진짜 좋은 사람 만났어요!"),
            ("assistant", "안녕하세요, 내친소입니다. 친구 소개를 통해 좋은 만남으로 이어지셨다니 정말 감사합니다! 앞으로도 신뢰할 수 있는 소개팅 경험을 드릴 수 있도록 노력하겠습니다."),

            ("human", "다른 소개팅 앱보다 훨씬 믿음이 가요. 추천합니다"),
            ("assistant", "안녕하세요, 내친소 운영팀입니다. 내친소의 신뢰 기반 매칭에 만족해주셔서 감사합니다! 앞으로도 좋은 인연을 만들어갈 수 있도록 최선을 다하겠습니다."),

            ("human", "UI도 깔끔하고 매칭 퀄리티가 좋아요"),
            ("assistant", "안녕하세요, 내친소입니다. UI와 매칭 퀄리티에 대해 좋게 평가해주셔서 팀에도 큰 힘이 됩니다. 앞으로도 더 나은 서비스로 보답하겠습니다."),

            ("human", "리뷰 내용: {review_content}"),
        ])

    def generate_response(self, review: Review, category: str = "칭찬") -> ReviewResponse:
        """긍정 리뷰 응답 생성"""
        try:
            chain = self.prompt | self.llm
            result = chain.invoke({"review_content": review.content})
            response_text = result.content.strip()

            # 마크다운 제거
            response_text = response_text.replace("**", "")

            # 길이 제한
            max_length = Config.MAX_RESPONSE_LENGTH.get(review.platform, 350)
            if len(response_text) > max_length:
                response_text = self._truncate(response_text, max_length)

            return ReviewResponse(
                review_id=review.id,
                response_text=response_text,
                generated_at=datetime.now(),
                country=review.country,
                platform=review.platform,
                used_sources=[],
            )

        except Exception as e:
            logger.error(f"응답 생성 오류: {e}")
            return ReviewResponse(
                review_id=review.id,
                response_text="안녕하세요, 내친소입니다. 소중한 리뷰 감사드립니다! 앞으로도 좋은 만남을 이어갈 수 있도록 노력하겠습니다.",
                generated_at=datetime.now(),
                country=review.country,
                platform=review.platform,
                used_sources=[],
            )

    def _truncate(self, text: str, max_length: int) -> str:
        """문장 단위로 자르기"""
        sentences = text.split(".")
        result = ""
        for s in sentences:
            if len(result + s + ".") <= max_length - 5:
                result += s + "."
            else:
                break
        return result.strip() if result else text[:max_length - 3] + "..."

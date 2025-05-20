from openai import OpenAI
import re
import ast

client = OpenAI(
    base_url="https://router.huggingface.co/nebius/v1",
    api_key="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",
)

def sentence_to_gloss(sentence: str):
    prompt = f"""
    아래 문장을 수어 번역용 글로스(gloss) 리스트로 변환해줘.

    아래 조건을 반드시 지켜줘:
    1. 출력은 반드시 Python 리스트 형식으로 해줘. (예: ["화장실", "어디", "있다"])
    2. 글로스는 한글 그대로 출력해줘. 영어로 번역하지 마.
    3. 형태소 단위 또는 의미 단위로 분해해서 리스트를 만들어줘.
    4. 단어가 하나일 경우에는 형태소 단위로 나누지 말고 그대로 출력해줘.
    5. 조사(예: "을", "는")는 보통 생략하고, 핵심 의미어 위주로 추출해줘.
    6. 생략어, 비문법적 표현도 최대한 의미 기준으로 분리해서 글로스로 만들어줘.
    7. 절대 설명하지 말고, 결과만 리스트로 출력해줘. 불필요한 설명 없이 리스트만 출력해줘. 설명이나 태그(<think> 등)는 포함하지 마.

문장: "{sentence}"
글로스:
"""

    response = client.chat.completions.create(
        model="Qwen/Qwen3-4B-fast",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    match = re.search(r'</think>\s*(\[[^\]]*\])', response.choices[0].message.content.strip(), re.MULTILINE)
    list_literal = match.group(1)
    result_list = ast.literal_eval(list_literal)  # 문자열→리스트
    return result_list

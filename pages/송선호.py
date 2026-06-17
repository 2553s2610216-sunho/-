import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌")
st.title("💌 달콤살벌 연애상담소")
st.caption("연애 고민이 있나요? Gemini가 진심 어린 조언을 해드려요.")

# 2. Streamlit Secrets에서 API 키 불러오기 및 클라이언트 초기화
try:
    # Streamlit Secrets에 저장된 키 사용
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 설정 후 다시 시도해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. 사용자 입력 받기
if prompt := st.chat_input("고민을 이야기해주세요... (예: 썸남이 선톡을 안 해요)"):
    # 사용자 메시지를 화면에 표시 및 세션에 저장
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 6. Gemini API 호출 및 응답 생성
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("답변을 생각 중이에요... 💬"):
            try:
                # 대화 맥락 유지를 위해 이전 기록을 Gemini 형식으로 변환
                # (단, 2.5 모델의 효율성을 위해 최근 대화 위주로 구성하는 것이 좋습니다)
                contents = []
                for msg in st.session_state.messages:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    ))

                # 시스템 지시문 설정 (챗봇의 페르소나 부여)
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "당신은 공감 능력이 뛰어나고 위트 있는 전문 연애 상담사입니다. "
                        "사용자의 연애 고민에 대해 따뜻하게 공감해주면서도, 때로는 객관적이고 현실적인 조언을 해주세요. "
                        "이모지를 적절히 섞어서 친근한 말투로 답변하세요."
                    ),
                    temperature=0.7,
                )

                # gemini-2.5-flash-lite 모델 호출
                response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=contents,
                    config=config
                )
                
                # 결과 출력
                ai_response = response.text
                response_placeholder.write(ai_response)
                
                # AI 메시지를 세션에 저장
                st.session_state.messages.append({"role": "assistant", "content": ai_response})

            except APIError as e:
                # Gemini API 관련 오류 처리
                error_msg = f"Gemini API 오류가 발생했습니다: {e.message}"
                response_placeholder.error(error_msg)
            except Exception as e:
                # 기타 일반 오류 처리
                error_msg = f"예기치 못한 오류가 발생했습니다: {str(e)}"
                response_placeholder.error(error_msg)

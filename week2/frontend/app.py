import streamlit as st
from state import get_state, set_state
import requests
import json
import httpx

st.set_page_config(page_title="MCP Chat", layout="wide")

st.title("🛠️ MCP Tool Calling Chat")

menu = st.sidebar.radio("메뉴", ["MCP 서버 설정", "헬스체크/Tools", "Chat"])

if menu == "MCP 서버 설정":
    st.header("MCP 서버 설정")
    mcp_url = st.text_input("MCP 서버 URL", value=get_state("mcp_url", ""))
    if st.button("저장"):
        set_state("mcp_url", mcp_url)
        st.success("저장되었습니다.")

elif menu == "헬스체크/Tools":
    st.header("MCP 서버 헬스체크 및 Tools 확인")
    mcp_url = get_state("mcp_url", "")
    if not mcp_url:
        st.warning("먼저 MCP 서버 URL을 설정하세요.")
    else:
        if st.button("헬스체크"):
            resp = requests.get(f"{mcp_url}/health")
            try:
                st.write(resp.json())
            except json.decoder.JSONDecodeError:
                st.error("서버에서 올바른 JSON이 반환되지 않았습니다.")
        if st.button("Tools 확인"):
            resp = requests.get(f"{mcp_url}/tools")
            try:
                st.write(resp.json())
            except json.decoder.JSONDecodeError:
                st.error("서버에서 올바른 JSON이 반환되지 않았습니다.")

elif menu == "Chat":
    st.header("MCP Tool Calling Chat")
    mcp_backend_url = st.text_input("백엔드 API URL", value=get_state("backend_url", "http://localhost:8000"))
    set_state("backend_url", mcp_backend_url)
    question = st.text_input("질문을 입력하세요", key="chat_input")
    if st.button("전송") and question:
        with st.spinner("Tool calling 및 답변 생성 중..."):
            try:
                resp = requests.post(f"{mcp_backend_url}/chat", json={"question": question}, timeout=30)
                data = resp.json()
                tool_calls = data.get("tool_calls", [])
                final_answer = data.get("final_answer", "")
                # tool call trace 시각화
                for tool in tool_calls:
                    from components import tool_call_status
                    tool_call_status(tool.get("tool"), tool.get("status"), result=tool.get("output"))
                st.markdown("---")
                st.subheader(":speech_balloon: 최종 답변")
                st.success(final_answer)
            except Exception as e:
                st.error(f"오류 발생: {e}")
    else:
        st.info("질문을 입력하고 전송을 눌러주세요.") 

def mcp_chat(question: str):
    url = get_state("mcp_url", "http://localhost:8000") # MCP 서버 URL을 state에서 가져옴
    payload = {"question": question}
    resp = httpx.post(url, json=payload, timeout=30)
    return resp.json() 
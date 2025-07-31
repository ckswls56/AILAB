import streamlit as st

def tool_call_status(tool_name, status, result=None):
    st.info(f"현재 호출 중인 Tool: {tool_name} (상태: {status})")
    if result is not None:
        with st.expander("Tool 호출 결과 보기", expanded=False):
            st.write(result) 
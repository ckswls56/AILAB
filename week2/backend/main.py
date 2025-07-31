from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
import week2.backend.config as config
import week2.backend.mcp_client as mcp_client
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/mcp/health")
def mcp_health():
    return mcp_client.mcp_health()

@app.get("/mcp/tools")
def mcp_tools():
    return mcp_client.mcp_tools()

@app.post("/mcp/config")
def set_mcp_config(cfg: dict):
    config.save_config(cfg)
    return {"status": "saved"}

@app.get("/mcp/config")
def get_mcp_config():
    return config.load_config()

@app.post("/chat")
def chat_api(payload: Dict = Body(...)):
    question = payload.get("question", "")
    # 1. tool calling LLM (mock)
    tool_trace = {
        "tool": "search_tool",
        "status": "called",
        "input": question,
        "output": f"'{question}'에 대한 검색 결과입니다.",
        "trace": "search_tool 호출됨"
    }
    # 2. 최종 답변 LLM (mock)
    final_answer = f"'{question}'에 대해 MCP tool을 호출하고, 결과를 종합한 최종 답변입니다."
    return {
        "tool_calls": [tool_trace],
        "final_answer": final_answer
    } 
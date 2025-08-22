from __future__ import annotations

import os
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi_mcp import FastApiMCP

app = FastAPI(title="FastAPI + fastapi_mcp", version="0.2.0")


# 기본 헬스엔드포인트(일반 API)
@app.get("/health", operation_id="health_check", tags=["public"])  # 명시적 operation_id 권장
async def health():
    return {"status": "ok"}


# 예시 도구가 될 엔드포인트들(명시적 operation_id 설정)
@app.get("/echo", operation_id="echo_text", tags=["tools"])
async def echo(text: Annotated[str, Query(description="반환할 텍스트")]):
    return {"text": text}


class AddIn(BaseModel):
    a: float
    b: float


@app.post("/add", operation_id="add_numbers", tags=["tools"])
async def add(payload: AddIn):
    return {"sum": payload.a + payload.b}


# fastapi_mcp 설정 및 마운트
# - include_operations로 노출할 도구를 선택 (또는 include_tags=["tools"]) 가능
mcp = FastApiMCP(
    app,
    name="My API MCP",
    description="Expose selected FastAPI endpoints as MCP tools",
    describe_all_responses=True,
    describe_full_response_schema=True,
    include_operations=["echo_text", "add_numbers"],
)

# default로 현재 앱(app)에 마운트. MCP UI/엔드포인트는 /mcp 하위에 생성됨
mcp.mount()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run(app, host="127.0.0.1", port=port)

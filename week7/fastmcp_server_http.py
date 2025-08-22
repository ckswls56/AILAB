from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP(name="Lab FastMCP Server (HTTP)")


@mcp.tool
def health() -> dict:
    """상태 점검 도구."""
    return {"status": "ok"}


if __name__ == "__main__":
    # 권장: streamable-http (문서에 따라 sse는 deprecated일 수 있음)
    # 사용 가능한 옵션: host, port, path 등
    mcp.run(transport="streamable-http", host="127.0.0.1", port=4200)
    # 또는 SSE(환경/버전에 따라 지원): mcp.run(transport="sse", host="127.0.0.1", port=4200)

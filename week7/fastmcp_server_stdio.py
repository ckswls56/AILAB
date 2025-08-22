from __future__ import annotations

from fastmcp import FastMCP, Context

mcp = FastMCP(name="Lab FastMCP Server (STDIO)")


# ---------- Tools ----------
@mcp.tool
def add(a: int, b: int) -> int:
    """두 정수를 더합니다."""
    return a + b


@mcp.tool
def echo(text: str) -> str:
    """입력 텍스트를 그대로 반환합니다."""
    return text


@mcp.tool
async def summarize_resource(uri: str, ctx: Context) -> dict:
    """주어진 리소스 URI를 읽어서 길이와 앞부분 요약을 반환합니다."""
    await ctx.info(f"Reading resource: {uri}")
    resources = await ctx.read_resource(uri)
    if not resources:
        return {"length": 0, "preview": ""}
    content = resources[0].content or ""
    text = content if isinstance(content, str) else str(content)
    preview = text[:120]
    return {"length": len(text), "preview": preview}


# ---------- Resources ----------
@mcp.resource("resource://config")
def app_config() -> dict:
    """애플리케이션 설정 값을 제공합니다."""
    return {"version": "1.0", "env": "dev"}


@mcp.resource("greet://{name}")
def greet_resource(name: str) -> str:
    """이름이 포함된 인사말을 리소스로 제공합니다."""
    return f"Hello, {name}!"


# ---------- Prompts ----------
@mcp.prompt
def analyze_numbers(numbers: list[float]) -> str:
    """숫자 리스트를 분석하도록 LLM에 지시하는 프롬프트를 생성합니다."""
    joined = ", ".join(str(n) for n in numbers)
    return f"다음 숫자들을 요약/분석해 주세요: {joined}"


if __name__ == "__main__":
    # 기본 전송: stdio (Claude Desktop 등에서 권장)
    mcp.run()  # or mcp.run(transport="stdio")

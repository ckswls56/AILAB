import httpx
import week2.backend.config as config


def get_base_url():
    cfg = config.load_config()
    return cfg.get('mcp_server_url', '')

def mcp_health():
    url = get_base_url() + '/health'
    try:
        resp = httpx.get(url, timeout=5)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def mcp_tools():
    url = get_base_url() + '/tools'
    try:
        resp = httpx.get(url, timeout=5)
        return resp.json()
    except Exception as e:
        return {"error": str(e)} 
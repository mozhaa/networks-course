import argparse
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from aiohttp import web

Headers = Dict[str, Any]


def filter_headers(headers: Headers, keys: List[str]) -> Headers:
    """Filter header, keep only selected keys"""
    return {key: headers[key] for key in keys if key in headers}


def build_request_headers(request_headers: Headers) -> Headers:
    required_keys = [
        "User-Agent",
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "Cookie",
    ]
    return filter_headers(request_headers, required_keys)


def build_response_headers(response_headers: Headers) -> Headers:
    required_keys = [
        "Date",
        "Content-Type",
        "Content-Encoding",
        "Server",
        "X-XSS-Protection",
        "X-Frame-Options",
        "Set-Cookie",
    ]
    return filter_headers(response_headers, required_keys)


def prepare_url(url: str) -> str:
    """Add https:// to URL if no scheme provided"""
    if url.startswith("/"):
        url = url[1:]
    schemes = ("http://", "https://")
    if not url.startswith(schemes):
        url = "http://" + url
    return url


def get_path_and_query(url):
    """Trim scheme and netloc info from URL"""
    parsed_url = urlparse(url)
    return parsed_url.path + ("?" + parsed_url.query if parsed_url.query else "")


def get_base_url(req: web.Request) -> Optional[str]:
    """Try to obtain original website url, so we can fix relative paths"""
    return get_path_and_query(req.headers["Referer"]) if "Referer" in req.headers else None


def get_requested_url(req: web.Request) -> str:
    """Get URL, requested by client"""
    return prepare_url(str(req.rel_url))


def get_fixed_relative_url(req: web.Request) -> str:
    """When client's browser requests relative url, try to add original base URL to it"""
    base_url = get_base_url(req)
    if base_url is not None:
        parsed_url = urlparse(prepare_url(base_url))
        return parsed_url.scheme + "://" + parsed_url.netloc + str(req.rel_url)


async def handle(req: web.Request) -> web.Response:
    headers = build_request_headers(req.headers)

    body = await req.json() if req.method == "POST" else None
    print(body)

    final_response = web.Response(body=f"Invalid url: {req.rel_url}", status=400)
    for url in filter(None, (get_requested_url(req), get_fixed_relative_url(req))):
        # try two possible URLs, and return successive if possible
        try:
            async with aiohttp.ClientSession(headers=headers, auto_decompress=False) as session:
                async with session.request(req.method, url, json=body) as response:
                    logger.info(f"{url}; STATUS_CODE={response.status}")
                    final_response = web.Response(
                        body=await response.read(),
                        status=response.status,
                        headers=build_response_headers(response.headers),
                    )
                    if response.ok:
                        return final_response
        except (
            aiohttp.ClientError,
            aiohttp.ClientConnectionError,
            aiohttp.InvalidURL,
        ) as e:
            logger.info(f"{url}; ERROR: {e}")
            final_response = web.Response(body=str(e), status=400)
            continue
    return final_response


def setup_logger() -> None:
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("server.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    return parser.parse_args()


app = web.Application()
app.router.add_get("/{target_url:.*}", handle)
app.router.add_post("/{target_url:.*}", handle)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    setup_logger()
    args = parse_arguments()
    web.run_app(app, host=args.host, port=args.port)

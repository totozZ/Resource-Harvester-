import logging
import re
from email.message import Message
from email.utils import collapse_rfc2231_value
from pathlib import Path
from urllib.parse import unquote, urlparse


AUTH_FILE = "auth.json"
DOWNLOAD_DIR = "downloads"

DOWNLOAD_KEYWORDS = [
    "下载",
    "download",
    "附件",
    "file",
    "export",
    "导出",
    "资料",
    "downloadfile",
]

DOWNLOAD_EXTENSIONS = {
    ".zip",
    ".rar",
    ".7z",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".csv",
    ".txt",
    ".exe",
    ".msi",
}

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def ensure_auth_file() -> None:
    if not Path(AUTH_FILE).exists():
        raise FileNotFoundError(
            f"未找到 {AUTH_FILE}。请先运行：python main.py login"
        )


def ensure_download_dir() -> Path:
    path = Path(DOWNLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(name: str, fallback: str = "download") -> str:
    """Return a Windows-safe filename while preserving readable Unicode names."""
    name = unquote(name or "").strip().strip('"').strip("'")
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    name = name.rstrip(" .")

    if not name:
        name = fallback

    stem = name.split(".", 1)[0].upper()
    if stem in WINDOWS_RESERVED_NAMES:
        name = f"_{name}"

    return name[:180]


def unique_path(directory: Path, filename: str) -> Path:
    path = directory / safe_filename(filename)
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    for index in range(1, 10000):
        candidate = directory / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate

    raise RuntimeError(f"无法生成不重复文件名：{filename}")


def _filename_from_content_disposition(header: str) -> str | None:
    if not header:
        return None

    message = Message()
    message["content-disposition"] = header

    filename_star = message.get_param("filename*", header="content-disposition")
    if filename_star:
        return collapse_rfc2231_value(filename_star)

    filename = message.get_filename()
    if filename:
        return filename

    filename = message.get_param("filename", header="content-disposition")
    if filename:
        return collapse_rfc2231_value(filename)

    return None


def get_filename_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if not name:
        return None
    return unquote(name)


def get_filename_from_response(response, url: str | None = None, fallback: str = "download") -> str:
    headers = getattr(response, "headers", {}) or {}
    content_disposition = (
        headers.get("content-disposition")
        or headers.get("Content-Disposition")
        or ""
    )

    filename = _filename_from_content_disposition(content_disposition)
    if not filename and url:
        filename = get_filename_from_url(url)
    if not filename:
        filename = fallback

    return safe_filename(filename, fallback=fallback)


def looks_like_download(text: str | None, href: str | None) -> bool:
    text = text or ""
    href = href or ""
    combined = f"{text} {href}".lower()

    if any(keyword.lower() in combined for keyword in DOWNLOAD_KEYWORDS):
        return True

    path = urlparse(href).path.lower()
    return any(path.endswith(ext) for ext in DOWNLOAD_EXTENSIONS)


def collect_links(page) -> list[dict]:
    return page.eval_on_selector_all(
        "a",
        """
        elements => elements.map((el, index) => ({
            index,
            text: (el.innerText || el.textContent || el.getAttribute("title") || "").trim(),
            href: el.href || el.getAttribute("href") || ""
        }))
        """,
    )


def collect_button_like_elements(page) -> list[dict]:
    return page.eval_on_selector_all(
        'button, [role="button"], [onclick], input[type="button"], input[type="submit"]',
        """
        elements => elements.map((el, index) => ({
            index,
            tag: el.tagName.toLowerCase(),
            text: (
                el.innerText ||
                el.textContent ||
                el.value ||
                el.getAttribute("aria-label") ||
                el.getAttribute("title") ||
                ""
            ).trim(),
            onclick: el.getAttribute("onclick") || ""
        }))
        """,
    )


def print_auth_warning() -> None:
    logging.warning(
        "%s 可能包含敏感 cookie。不要上传到 GitHub，也不要分享给别人。",
        AUTH_FILE,
    )

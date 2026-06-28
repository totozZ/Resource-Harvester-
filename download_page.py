import logging

from playwright.sync_api import sync_playwright

from utils import (
    AUTH_FILE,
    collect_links,
    ensure_auth_file,
    ensure_download_dir,
    get_filename_from_response,
    looks_like_download,
    setup_logging,
    unique_path,
)


def download_page() -> None:
    setup_logging()

    try:
        ensure_auth_file()
    except FileNotFoundError as exc:
        logging.error(str(exc))
        return

    target_url = input("请输入目标页面 URL：").strip()
    if not target_url:
        logging.error("URL 不能为空。")
        return

    download_dir = ensure_download_dir()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_FILE, accept_downloads=True)
        page = context.new_page()

        try:
            logging.info("正在打开页面：%s", target_url)
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception as exc:
            logging.warning("页面加载等待未完全成功，但会继续扫描：%s", exc)

        links = collect_links(page)
        candidates = [
            link
            for link in links
            if link.get("href") and looks_like_download(link.get("text"), link.get("href"))
        ]

        if not candidates:
            logging.info("没有找到疑似下载链接。可先运行 python main.py list 观察页面结构。")
            browser.close()
            return

        print("\n=== 疑似下载链接 ===")
        for i, link in enumerate(candidates, start=1):
            text = link.get("text") or "(无文本)"
            href = link.get("href") or ""
            print(f"[{i}] {text}\n    {href}")

        confirm = input("\n确认下载以上文件？输入 y 继续：").strip().lower()
        if confirm != "y":
            logging.info("已取消下载。")
            browser.close()
            return

        for i, link in enumerate(candidates, start=1):
            href = link.get("href")
            text = link.get("text") or f"download_{i}"
            try:
                logging.info("正在下载 [%s/%s] %s", i, len(candidates), href)
                response = context.request.get(href, timeout=60000)
                if not response.ok:
                    logging.error("下载失败：HTTP %s - %s", response.status, href)
                    continue

                content_type = (response.headers.get("content-type") or "").lower()
                if "text/html" in content_type:
                    logging.warning("可能下载到的是网页而不是文件：%s", href)

                filename = get_filename_from_response(
                    response,
                    url=href,
                    fallback=f"{text}_{i}",
                )
                path = unique_path(download_dir, filename)
                path.write_bytes(response.body())
                logging.info("下载成功：%s", path)
            except Exception as exc:
                logging.exception("下载失败：%s，原因：%s", href, exc)

        browser.close()


if __name__ == "__main__":
    download_page()

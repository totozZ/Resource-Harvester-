import logging

from playwright.sync_api import sync_playwright

from utils import (
    AUTH_FILE,
    collect_button_like_elements,
    collect_links,
    ensure_auth_file,
    setup_logging,
)


def list_links() -> None:
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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_FILE)
        page = context.new_page()

        try:
            logging.info("正在打开页面：%s", target_url)
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception as exc:
            logging.warning("页面加载等待未完全成功，但会继续扫描：%s", exc)

        print("\n=== a 标签链接 ===")
        links = collect_links(page)
        for i, link in enumerate(links, start=1):
            text = link.get("text") or "(无文本)"
            href = link.get("href") or "(无 href)"
            print(f"[{i}] {text}\n    {href}")

        print("\n=== 按钮 / role=button / onclick 元素 ===")
        buttons = collect_button_like_elements(page)
        for i, button in enumerate(buttons, start=1):
            text = button.get("text") or "(无文本)"
            tag = button.get("tag") or "unknown"
            onclick = button.get("onclick") or ""
            print(f"[{i}] <{tag}> {text}")
            if onclick:
                print(f"    onclick: {onclick[:160]}")

        logging.info("扫描完成：链接 %s 个，按钮类元素 %s 个。", len(links), len(buttons))
        browser.close()


if __name__ == "__main__":
    list_links()

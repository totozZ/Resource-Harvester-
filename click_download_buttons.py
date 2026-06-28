import logging
import re

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from utils import AUTH_FILE, ensure_auth_file, ensure_download_dir, setup_logging, unique_path


BUTTON_TEXT_PATTERN = re.compile(
    r"下载|Download|download|附件|导出|Export|export|资料"
)


def click_download_buttons() -> None:
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
            logging.warning("页面加载等待未完全成功，但会继续查找按钮：%s", exc)

        selector = (
            'button, [role="button"], [onclick], a, input[type="button"], '
            'input[type="submit"]'
        )
        element_infos = page.eval_on_selector_all(
            selector,
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
                ).trim()
            }))
            """,
        )
        candidates = [
            item
            for item in element_infos
            if item.get("text") and BUTTON_TEXT_PATTERN.search(item["text"])
        ]

        if not candidates:
            logging.info("没有找到疑似下载按钮。")
            browser.close()
            return

        logging.info("找到 %s 个疑似下载按钮/元素。", len(candidates))

        for candidate in candidates:
            text = candidate.get("text") or "(无文本)"
            index = candidate["index"]
            logging.info("正在尝试按钮：%s", text)

            try:
                locator = page.locator(selector).nth(index)
                locator.scroll_into_view_if_needed(timeout=5000)

                try:
                    with page.expect_download(timeout=10000) as download_info:
                        locator.click(timeout=10000)
                    download = download_info.value
                except PlaywrightTimeoutError:
                    logging.info("未触发下载，跳过：%s", text)
                    continue

                filename = download.suggested_filename or f"download_{index + 1}"
                path = unique_path(download_dir, filename)
                download.save_as(path)
                logging.info("下载成功：%s", path)

                try:
                    page.wait_for_load_state("domcontentloaded", timeout=3000)
                except Exception:
                    pass
            except Exception as exc:
                logging.exception("按钮处理失败，继续下一个：%s，原因：%s", text, exc)
                try:
                    if page.is_closed():
                        page = context.new_page()
                        page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                except Exception as recover_exc:
                    logging.warning("页面恢复失败：%s", recover_exc)

        browser.close()


if __name__ == "__main__":
    click_download_buttons()

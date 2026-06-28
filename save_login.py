import logging

from playwright.sync_api import sync_playwright

from utils import AUTH_FILE, print_auth_warning, setup_logging


def save_login() -> None:
    setup_logging()
    login_url = input("请输入登录页 URL：").strip()
    if not login_url:
        logging.error("URL 不能为空。")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        logging.info("正在打开登录页：%s", login_url)
        page.goto(login_url, wait_until="domcontentloaded")

        input("请在浏览器中手动完成登录。登录完成后按回车保存登录态...")
        context.storage_state(path=AUTH_FILE)
        logging.info("登录态已保存到 %s", AUTH_FILE)
        print_auth_warning()

        browser.close()


if __name__ == "__main__":
    save_login()

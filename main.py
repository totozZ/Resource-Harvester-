import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Resource Harvester")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("login", help="手动登录并保存 auth.json")
    subparsers.add_parser("list", help="列出页面链接和按钮")
    subparsers.add_parser("download", help="扫描并下载普通链接")
    subparsers.add_parser("click-download", help="尝试点击按钮触发下载")
    subparsers.add_parser("smartedu", help="按小源逻辑下载智慧教育平台四类资源")
    subparsers.add_parser("smartedu-grade", help="按教材目录整册下载智慧教育平台四类资源")

    args = parser.parse_args()

    if args.command == "login":
        from save_login import save_login

        save_login()
    elif args.command == "list":
        from list_links import list_links

        list_links()
    elif args.command == "download":
        from download_page import download_page

        download_page()
    elif args.command == "click-download":
        from click_download_buttons import click_download_buttons

        click_download_buttons()
    elif args.command == "smartedu":
        from smartedu_xiaoyuan_download import main as smartedu_download

        smartedu_download()
    elif args.command == "smartedu-grade":
        from smartedu_grade_download import main as smartedu_grade_download

        smartedu_grade_download()


if __name__ == "__main__":
    main()

# SmartEdu Resource Harvester

中文名：智慧教育资源采集器。

这是一个 Windows + Python + Playwright 的本地网页下载自动化项目。它最初用于登录后网页资源下载，现在已经内置国家中小学智慧教育平台专项下载能力，可以按教材目录批量下载：

- 课件
- 教学设计
- 学习任务单
- 课后练习

项目不会保存账号密码。登录由你在浏览器中手动完成，工具只保存 Playwright 的 `auth.json` 登录态。

重要提醒：`auth.json` 可能包含敏感 cookie 和 token，等同于部分网站的登录凭据。不要上传 GitHub，不要发给别人。

## 功能

- 手动登录一次并保存登录态到 `auth.json`
- 复用登录态访问需要登录的网站
- 扫描普通网页中的链接和按钮
- 下载普通 `a` 标签文件链接
- 尝试点击按钮触发下载
- 针对国家中小学智慧教育平台，按“小源教材下载助手”的公开逻辑下载课程资源
- 支持单课下载和整册下载
- 整册下载会按教材章节逐层创建文件夹
- 下载文件保存到 `downloads/`

## 安装

进入项目目录：

```powershell
cd C:\Users\95833\Desktop\1
```

创建并启用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
pip install -r requirements.txt
```

安装 Playwright Chromium：

```powershell
playwright install chromium
```

## 快速开始

完整快速流程见 [QUICKSTART.md](./QUICKSTART.md)。

最常用流程如下：

```powershell
python main.py login
python main.py smartedu-grade
```

第一次命令用于手动登录并保存 `auth.json`。第二个命令用于粘贴智慧教育平台整册导航页 URL，然后自动下载整册资源。

## 命令

### 登录

```powershell
python main.py login
```

输入登录页 URL，在打开的浏览器中手动登录。登录完成后回到命令行按回车，工具会保存 `auth.json`。

### 查看普通网页链接和按钮

```powershell
python main.py list
```

用于观察登录后页面里的 `a` 标签、按钮、`role=button`、`onclick` 元素。不下载文件。

### 下载普通链接

```powershell
python main.py download
```

扫描疑似下载链接，列出结果，输入 `y` 后下载到 `downloads/`。

### 点击按钮下载

```powershell
python main.py click-download
```

查找“下载 / Download / 附件 / 导出 / Export / 资料”等按钮并尝试点击，用 Playwright 捕获下载事件。

### 智慧教育平台单课下载

```powershell
python main.py smartedu
```

粘贴类似 `https://basic.smartedu.cn/syncClassroom/classActivity?...` 的课程页面 URL，工具会下载当前课程的四类 PDF 资源。

### 智慧教育平台整册下载

```powershell
python main.py smartedu-grade
```

粘贴类似 `https://basic.smartedu.cn/syncClassroom/prepare?defaultTag=...` 的整册导航页 URL，工具会：

- 自动识别教材
- 拉取教材目录树
- 创建章节文件夹
- 逐个解析课程包
- 下载课件、教学设计、学习任务单、课后练习

示例输出目录：

```text
downloads/
  smartedu/
    小学数学人教版四年级下册/
      1 四则运算/
      2 观察物体（二）/
      3 运算律/
      4 小数的意义和性质/
      ...
```

## 项目结构

```text
.
├─ main.py                         # 统一命令入口
├─ save_login.py                   # 手动登录并保存 auth.json
├─ list_links.py                   # 扫描页面链接和按钮
├─ download_page.py                # 下载普通链接
├─ click_download_buttons.py       # 尝试点击按钮下载
├─ smartedu_xiaoyuan_download.py   # 智慧教育平台单课下载
├─ smartedu_grade_download.py      # 智慧教育平台整册下载
├─ utils.py                        # 公共函数
├─ requirements.txt
├─ README.md
└─ QUICKSTART.md
```

## Git 忽略

`.gitignore` 已忽略：

```text
auth.json
downloads/
__pycache__/
*.pyc
xiaoyuandownload-resource/
```

其中 `auth.json` 和 `downloads/` 不应上传仓库。

## 常见问题

### auth.json 失效怎么办？

重新运行：

```powershell
python main.py login
```

手动登录后再次保存登录态。

### 下载到的是 HTML 怎么办？

通常说明登录态失效、权限不足、接口需要额外 token，或网站返回了错误页。先重新登录，再重试下载。

### 找不到下载链接怎么办？

普通网页先运行：

```powershell
python main.py list
```

智慧教育平台页面优先使用：

```powershell
python main.py smartedu
python main.py smartedu-grade
```

### 为什么整册目录里有空文件夹？

脚本会按教材目录完整建文件夹。有些目录在平台资源索引里没有对应课程包，目录会保留但没有 PDF。

### 为什么不能上传 auth.json？

`auth.json` 保存了 cookie、localStorage token 等登录态数据。别人拿到后可能复用你的登录状态访问网站。

## 来源说明

智慧教育平台专项下载逻辑参考了“小源教材下载助手”的公开实现思路：读取课程详情 JSON，从资源 `ti_items` 中寻找 PDF 链接，并结合登录态访问下载地址。

- 小源页面：https://www.yuanstudy.com/pages/7/
- 公开仓库：https://github.com/MaxXiaoChen/xiaoyuandownload-resource

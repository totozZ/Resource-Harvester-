# Quickstart

这个文档只写最快使用路径。项目名：`SmartEdu Resource Harvester`，中文名“智慧教育资源采集器”。

## 1. 安装

```powershell
cd C:\Users\95833\Desktop\1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

如果你已经安装过依赖，可以跳过这一步。

## 2. 登录一次

```powershell
python main.py login
```

输入国家中小学智慧教育平台登录页或首页 URL：

```text
https://basic.smartedu.cn/
```

浏览器打开后手动登录。确认登录成功后，回到命令行按回车保存登录态。

保存成功后会生成：

```text
auth.json
```

不要上传或分享这个文件。

## 3. 下载单课资源

适合这种页面：

```text
https://basic.smartedu.cn/syncClassroom/classActivity?activityId=...
```

运行：

```powershell
python main.py smartedu
```

粘贴课程页面 URL，确认后自动下载：

- 课件
- 教学设计
- 学习任务单
- 课后练习

输出目录：

```text
downloads/smartedu/
```

## 4. 下载整册资源

适合这种页面：

```text
https://basic.smartedu.cn/syncClassroom/prepare?defaultTag=...
```

运行：

```powershell
python main.py smartedu-grade
```

粘贴整册导航页 URL。脚本会自动识别教材并按章节建文件夹。

示例目录：

```text
downloads/
  smartedu/
    小学数学人教版四年级下册/
      1 四则运算/
      2 观察物体（二）/
      3 运算律/
      ...
```

## 5. 普通网页下载

先观察页面：

```powershell
python main.py list
```

下载普通链接：

```powershell
python main.py download
```

尝试按钮下载：

```powershell
python main.py click-download
```

## 常用命令速查

```powershell
python main.py login
python main.py smartedu
python main.py smartedu-grade
python main.py list
python main.py download
python main.py click-download
```

## 结果在哪里？

所有下载文件都在：

```text
downloads/
```

智慧教育平台资源通常在：

```text
downloads/smartedu/
```

## 出错时先试什么？

1. 重新登录：

```powershell
python main.py login
```

2. 再重新下载：

```powershell
python main.py smartedu-grade
```

3. 如果仍然失败，把终端报错和目标页面 URL 发给维护者排查。不要发送 `auth.json`。

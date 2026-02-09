# ✨ Prompt Packager Pro

基于Python的可视化GUI工具，可以将多个指定文件/文件夹合并为一个 **Markdown** 或 **XML** 文件，非常适合将代码上下文喂给 LLM（如 ChatGPT、Claude、Gemini）进行分析。

## 📸 Features

* **Material Design 3 主题** 非常好看现代化的UI设计:
* **多线程异步处理**: 扫描大文件夹或生成大文件时保持前台流畅
* **灵活的输出格式**: 支持 Markdown 和 XML 

## 🚀 快速开始

### 运行源码

1.  克隆仓库或下载代码。
2.  安装依赖:
    ```bash
    pip install -r requirements.txt
    ```
3.  运行程序:
    ```bash
    python main.py
    ```

### 编译为 EXE (Windows)

只需双击根目录下的 `build_exe.bat` 脚本即可。
编译成功后，可执行文件将位于 `dist/PromptPackager.exe`

## 🛠️ 技术栈

* **Python 3.x**
* **CustomTkinter**
* **Tkinter**
* **ThreadPoolExecutor**

## 📝 使用指南

1.  **导航**: 使用顶部的地址栏或按钮选择项目根目录
2.  **选择文件**: 在右侧文件树中勾选需要打包的文件或文件夹（支持双击进入文件夹）
3.  **配置**:
    * 在左侧栏设置输出文件名和格式 (MD/XML)
    * 勾选“写入相对路径”以保持文件结构清晰（不勾选只写入文件名不写入路径）
    * 如果有需要忽略的文件（如 `.pyc`），在忽略规则框中添加
4.  **生成**: 点击右下角的按钮，文件将保存到指定目录

---
*Created by Afkeru*
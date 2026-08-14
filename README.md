# CryptTalk

**基于 RSA + DES 混合加密的即时加密通信工具**，支持 CLI 和 GUI 双模式。

## 项目简介

CryptTalk 是一个端到端加密的即时通信演示项目，采用 **RSA 非对称加密** 与 **DES 对称加密** 混合方案：
- 通信双方通过 RSA 安全协商临时 DES 会话密钥
- 所有消息使用 DES 加密，并附带 MD5 摘要验证完整性

适合作为网络安全或密码学课程的实践项目。

## 功能特性

- 🔐 混合加密（RSA 密钥协商 + DES 消息加密）
- ✅ MD5 完整性校验，防篡改
- 🖥️ 双模式：CLI（client.py / server.py）和 GUI（crypttalk_*.py）
- 💬 实时双向聊天
- 🎨 美观的 Tkinter GUI 界面

## 技术架构

### 加密流程

1. 服务端生成 RSA 密钥对，发送公钥给客户端
2. 客户端生成 DES 密钥，用 RSA 公钥加密后发送给服务端
3. 服务端用 RSA 私钥解密，获得 DES 会话密钥
4. 双方使用 DES 加密消息，并附加 MD5 摘要

### 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3 |
| 非对称加密 | RSA (2048位) |
| 对称加密 | DES (ECB模式, PKCS7填充) |
| 哈希校验 | MD5 |
| 网络通信 | Socket |
| GUI框架 | Tkinter |
| 加密库 | `cryptography` |

## 安装与使用

### 环境要求

- Python 3.6+
- pip

### 安装依赖

```bash
pip install cryptography

|如缺少 Tkinter，Ubuntu 执行 sudo apt-get install python3-tk，Windows/macOS 通常自带

命令行模式（CLI）
服务端：

bash
python server.py

客户端：

bash
python client.py

默认连接 127.0.0.1:12345，跨机通信请修改代码中 HOST 变量。

图形界面模式（GUI）
服务端 GUI：

bash
python crypttalk_server.py
客户端 GUI：

bash
python crypttalk_client.py
聊天操作
输入消息按回车发送

输入 exit 退出

项目文件结构
text
CryptTalk/
├── client.py                 # CLI 客户端
├── server.py                 # CLI 服务端
├── crypttalk_client.py       # GUI 客户端
├── crypttalk_server.py       # GUI 服务端
├── crypto_utils.py           # 加密工具模块
├── CryptTalk_Client.spec     # PyInstaller 打包配置
├── CryptTalk_Server.spec
├── .gitignore
└── README.md

核心模块说明
crypto_utils.py
提供：

RSA 密钥生成、加解密

DES 密钥生成、加解密（ECB + PKCS7）

MD5 哈希计算

Base64 编解码辅助函数

通信协议
消息格式：{密文Base64}|{摘要Base64}
接收方解密密文并验证 MD5，确保完整性。

打包为可执行文件
bash
pyinstaller CryptTalk_Client.spec   # 打包客户端
pyinstaller CryptTalk_Server.spec   # 打包服务端
可执行文件位于 dist/ 目录。

注意事项
⚠️ 教学演示用途，勿用于生产环境

DES 和 ECB 模式强度较低，生产环境建议使用 AES + CBC/GCM

默认绑定 127.0.0.1，跨机需修改 HOST

贡献指南
欢迎提交 Issue 和 PR：

Fork 仓库

创建特性分支 (git checkout -b feature/AmazingFeature)

提交更改 (git commit -m 'Add feature')

推送分支 (git push origin feature/AmazingFeature)

打开 Pull Request

许可证
本项目仅供学习交流使用
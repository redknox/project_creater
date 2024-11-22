# Project Creator

一个强大的Python项目结构生成器，支持日志系统和配置管理。

## 特性

- 创建标准的Python项目结构
- 支持Git初始化
- 自动创建和管理虚拟环境
- 可选的日志系统（文件和控制台输出）
- 可选的配置系统（支持YAML/JSON/INI）
- 生成详细的使用文档

## 安装

```bash
# 克隆仓库
git clone https://github.com/redknox/project_creater.git
cd project_creater

# 或者直接通过pip安装
pip install git+https://github.com/redknox/project_creater.git

# 如果你想要开发此项目，可以按照以下步骤操作：
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

## 使用方法

```bash
# 直接运行
python main.py

# 或使用安装后的命令
create-project
```

程序会交互式地询问以下信息：
- 项目名称
- 项目路径
- 作者信息
- 项目描述
- Python版本要求
- 是否使用Git
- 是否创建虚拟环境
- 是否需要日志系统
- 是否需要配置系统

## 项目结构

生成的项目结构如下：

```
项目名称/
├── src/
│   └── 项目名称/
│       ├── __init__.py
│       ├── main.py
│       ├── utils/
│       │   ├── __init__.py
│       │   └── log.py  # 如果选择使用日志系统
│       └── config/     # 如果选择使用配置系统
│           ├── __init__.py
│           ├── config.py
│           ├── default.yaml
│           └── production.yaml
├── tests/
│   └── test_main.py
├── docs/
│   └── helper.md      # 如果使用了日志或配置系统
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py
```

## 配置系统

支持三种配置格式：
- YAML（推荐，人类可读性强）
- JSON（通用性强）
- INI（简单配置适用）

配置系统特性：
- 分层配置（默认/环境/本地）
- 环境变量支持
- 使用Pydantic进行配置验证

## 日志系统

日志系统特性：
- 同时输出到文件和终端
- 文件日志级别为INFO
- 终端日志级别为DEBUG
- 支持日志轮转
- 详细的日志格式

## 开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest

# 代码格式化
black .
isort .

# 代码检查
pylint main.py
```

## 贡献

欢迎提交Issue和Pull Request！

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的修改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

你也可以通过以下方式贡献：
- 报告Bug：https://github.com/redknox/project_creater/issues
- 提出新功能：https://github.com/redknox/project_creater/issues
- 完善文档：直接提交PR

## 许可证

MIT License

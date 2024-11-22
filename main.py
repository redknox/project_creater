#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path
import re
import glob
import json

class ProjectInfo:
    def __init__(self):
        self.project_name = ""
        self.project_path = ""
        self.author = ""
        self.email = ""
        self.description = ""
        self.version = "0.1.0"
        self.python_version = ">=3.7"
        self.license = "MIT"
        self.use_git = True
        self.use_venv = True
        self.use_logging = True
        self.use_config = True
        self.config_format = "yaml"  # 可选：yaml, json, ini

    def get_installed_pythons(self):
        """获取系统中已安装的Python版本"""
        python_versions = []
        try:
            # 在macOS中查找Python版本
            python_paths = glob.glob("/usr/local/bin/python3*") + \
                         glob.glob("/usr/bin/python3*") + \
                         glob.glob(os.path.expanduser("~/Library/Python/*/bin/python3*"))
            
            for path in python_paths:
                try:
                    # 获取Python版本
                    result = subprocess.run([path, '--version'], 
                                         capture_output=True, 
                                         text=True, 
                                         check=True)
                    version = result.stdout.strip()
                    python_versions.append((path, version))
                except subprocess.CalledProcessError:
                    continue
            
            # 如果找到了Homebrew安装的Python
            brew_pythons = subprocess.run(['brew', 'list', '--versions', 'python@3*'],
                                        capture_output=True,
                                        text=True)
            if brew_pythons.returncode == 0:
                for line in brew_pythons.stdout.splitlines():
                    if line.startswith('python@3'):
                        brew_version = line.split()[1]
                        brew_path = f"/usr/local/opt/python@{brew_version}/bin/python3"
                        if os.path.exists(brew_path):
                            python_versions.append((brew_path, f"Python {brew_version} (Homebrew)"))

        except Exception as e:
            print(f"警告：获取Python版本时出错：{str(e)}")
        
        return sorted(list(set(python_versions)), key=lambda x: x[1])

    def collect_info(self):
        """通过交互式问答收集项目信息"""
        print("\n=== 欢迎使用Python项目创建向导 ===\n")
        
        # 项目名称
        while True:
            self.project_name = input("请输入项目名称: ").strip()
            if re.match("^[a-zA-Z][a-zA-Z0-9_-]*$", self.project_name):
                break
            print("错误：项目名称必须以字母开头，只能包含字母、数字、下划线和连字符")

        # 项目路径
        default_path = os.getcwd()
        path_input = input(f"请输入项目路径 (直接回车使用当前目录 {default_path}): ").strip()
        self.project_path = path_input if path_input else default_path

        # 作者信息
        self.author = input("请输入作者姓名: ").strip()
        while True:
            self.email = input("请输入作者邮箱: ").strip()
            if not self.email or '@' in self.email:
                break
            print("错误：请输入有效的邮箱地址")

        # 项目描述
        self.description = input("请输入项目描述: ").strip()

        # Python版本
        python_version = input("请输入所需的Python最低版本 (直接回车使用 3.7): ").strip()
        if python_version:
            self.python_version = f">={python_version}"

        # Git管理
        while True:
            git_choice = input("是否使用Git管理项目? (y/n) [y]: ").strip().lower()
            if git_choice in ['y', 'n']:
                self.use_git = (git_choice == 'y')
                break
            print("错误：请输入 y 或 n")

        # 虚拟环境
        while True:
            venv_choice = input("是否创建虚拟环境? (y/n) [y]: ").strip().lower()
            if venv_choice in ['y', 'n']:
                self.use_venv = (venv_choice == 'y')
                break
            print("错误：请输入 y 或 n")

        # 日志系统
        while True:
            logging_choice = input("是否需要日志系统？(y/n) [y]: ").strip().lower()
            if logging_choice in ['y', 'n']:
                self.use_logging = (logging_choice == 'y')
                break
            print("错误：请输入 y 或 n")

        # 配置系统
        while True:
            config_choice = input("是否需要配置系统？(y/n) [y]: ").strip().lower()
            if config_choice in ['y', 'n']:
                self.use_config = (config_choice != 'n')
                break
            print("错误：请输入 y 或 n")

        if self.use_config:
            while True:
                format_choice = input("选择配置文件格式 (1: YAML, 2: JSON, 3: INI) [1]: ").strip()
                if not format_choice:
                    format_choice = "1"
                if format_choice in ['1', '2', '3']:
                    self.config_format = {
                        '1': 'yaml',
                        '2': 'json',
                        '3': 'ini'
                    }[format_choice]
                    break
                print("错误：请输入 1、2 或 3")

        if self.use_venv:
            python_versions = self.get_installed_pythons()
            if not python_versions:
                print("警告：未找到可用的Python版本，将跳过虚拟环境创建")
                self.use_venv = False
            else:
                print("\n可用的Python版本：")
                for i, (path, version) in enumerate(python_versions, 1):
                    print(f"{i}. {version} ({path})")
                
                while True:
                    choice = input(f"\n请选择Python版本 (1-{len(python_versions)}): ").strip()
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(python_versions):
                            self.venv_python = python_versions[index][0]
                            break
                        else:
                            print(f"错误：请输入1到{len(python_versions)}之间的数字")
                    except ValueError:
                        print("错误：请输入有效的数字")

        # 确认信息
        print("\n=== 项目信息确认 ===")
        print(f"项目名称: {self.project_name}")
        print(f"项目路径: {self.project_path}")
        print(f"作者: {self.author}")
        print(f"邮箱: {self.email}")
        print(f"描述: {self.description}")
        print(f"Python版本: {self.python_version}")
        print(f"开源协议: {self.license}")
        print(f"使用Git管理: {'是' if self.use_git else '否'}")
        print(f"创建虚拟环境: {'是' if self.use_venv else '否'}")
        print(f"使用日志系统: {'是' if self.use_logging else '否'}")
        print(f"使用配置系统: {'是' if self.use_config else '否'}")
        if self.use_config:
            print(f"配置文件格式: {self.config_format}")
        if self.use_venv:
            print(f"虚拟环境Python版本: {self.venv_python}")

        confirm = input("\n确认创建项目? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消项目创建")
            sys.exit(0)

class ProjectCreator:
    def __init__(self, project_info: ProjectInfo):
        self.info = project_info
        self.project_dir = os.path.join(self.info.project_path, self.info.project_name)

    def create_project_structure(self):
        """创建项目基本结构"""
        # 创建主项目目录
        os.makedirs(self.project_dir, exist_ok=True)

        # 创建项目子目录
        directories = [
            '',  # 项目根目录
            'src',  # 源代码目录
            f'src/{self.info.project_name}',  # 项目包目录
            'tests',  # 测试目录
            'docs',  # 文档目录
            'config',  # 配置文件目录
        ]

        # 创建所有目录
        for directory in directories:
            dir_path = os.path.join(self.project_dir, directory)
            os.makedirs(dir_path, exist_ok=True)

    def create_basic_files(self):
        """创建基本的项目文件"""
        # 创建 README.md
        readme_content = f"""# {self.info.project_name}

## 描述
{self.info.description}

## 安装
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发模式
pip install -e .
```

## 使用方法
```python
from {self.info.project_name} import main

main()
```

## 开发者
- {self.info.author} ({self.info.email})

## 开源协议
{self.info.license} License
"""
        with open(os.path.join(self.project_dir, 'README.md'), 'w') as f:
            f.write(readme_content)

        # 创建 requirements.txt
        with open(os.path.join(self.project_dir, 'requirements.txt'), 'w') as f:
            f.write('# 项目依赖\n')
            f.write('# 每行一个依赖，例如：\n')
            f.write('# requests>=2.28.0\n')
            f.write('# pandas>=1.5.0\n')

        # 创建 setup.py
        setup_content = f'''from setuptools import setup, find_packages

def read_requirements(filename):
    """读取requirements.txt文件内容."""
    with open(filename, 'r', encoding='utf-8') as f:
        # 过滤掉注释和空行
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="{self.info.project_name}",
    version="{self.info.version}",
    package_dir={{"": "src"}},
    packages=find_packages(where="src"),
    install_requires=read_requirements('requirements.txt'),
    author="{self.info.author}",
    author_email="{self.info.email}",
    description="{self.info.description}",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/{self.info.author}/{self.info.project_name}",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: {self.info.license} License",
        "Operating System :: OS Independent",
    ],
    python_requires="{self.info.python_version}",
)
'''
        with open(os.path.join(self.project_dir, 'setup.py'), 'w') as f:
            f.write(setup_content)

        # 创建包的 __init__.py
        init_path = os.path.join(self.project_dir, 'src', self.info.project_name, '__init__.py')
        init_content = f'''"""
{self.info.project_name} package.

{self.info.description}
"""

__version__ = "{self.info.version}"
__author__ = "{self.info.author}"
__email__ = "{self.info.email}"
'''
        with open(init_path, 'w') as f:
            f.write(init_content)

        # 创建 main.py
        main_content = '''"""Main module."""

def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
        main_path = os.path.join(self.project_dir, 'src', self.info.project_name, 'main.py')
        with open(main_path, 'w') as f:
            f.write(main_content)

        # 创建测试文件
        test_content = f'''"""Test module."""
import unittest
from {self.info.project_name}.main import main

class TestMain(unittest.TestCase):
    """Test cases for main module."""
    
    def test_main(self):
        """Test main function."""
        # Add your test cases here
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
'''
        with open(os.path.join(self.project_dir, 'tests', 'test_main.py'), 'w') as f:
            f.write(test_content)

        # 创建utils目录和日志模块
        if self.info.use_logging:
            utils_dir = os.path.join(self.project_dir, 'src', self.info.project_name, 'utils')
            os.makedirs(utils_dir, exist_ok=True)
            self._create_logging_module(utils_dir)

        # 创建配置系统
        if self.info.use_config:
            self._create_config_module()

    def _create_logging_module(self, utils_dir):
        """创建日志模块"""
        log_content = '''"""
日志模块，提供统一的日志记录功能。

特性：
1. 同时输出到文件和终端
2. 文件日志级别为INFO
3. 终端日志级别为DEBUG
4. 终端输出包含详细的模块位置信息
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(name, log_dir='logs'):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件存储目录
    
    Returns:
        logger: 配置好的日志记录器
    """
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建文件处理器
    log_file = os.path.join(log_dir, f'{name}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # 添加处理器到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 示例用法
if __name__ == '__main__':
    logger = setup_logger('test_logger')
    logger.debug('这是一条调试信息')
    logger.info('这是一条信息')
    logger.warning('这是一条警告')
    logger.error('这是一条错误信息')
'''
        
        # 创建日志模块文件
        log_file = os.path.join(utils_dir, 'log.py')
        with open(log_file, 'w') as f:
            f.write(log_content)
            
        # 创建utils包的__init__.py
        init_file = os.path.join(utils_dir, '__init__.py')
        with open(init_file, 'w') as f:
            f.write('"""工具模块包"""\n\n')
            f.write('from .log import setup_logger\n\n')
            f.write('__all__ = ["setup_logger"]\n')

    def _create_config_module(self):
        """创建配置模块"""
        config_dir = os.path.join(self.project_dir, 'src', self.info.project_name, 'config')
        os.makedirs(config_dir, exist_ok=True)

        # 创建配置处理模块
        config_content = '''"""
配置管理模块，提供统一的配置加载和处理功能。

特性：
1. 多格式支持 (YAML/JSON/INI)
2. 分层配置 (默认/环境/本地)
3. 环境变量支持
4. 配置验证
"""
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
try:
    import yaml
except ImportError:
    yaml = None
try:
    import tomli
except ImportError:
    tomli = None
from configparser import ConfigParser

class ConfigError(Exception):
    """配置相关错误"""
    pass

class AppConfig(BaseModel):
    """应用配置模型"""
    # 在这里定义你的配置项
    app_name: str = Field(default="", description="应用名称")
    debug: bool = Field(default=False, description="是否开启调试模式")
    host: str = Field(default="127.0.0.1", description="服务主机地址")
    port: int = Field(default=8000, description="服务端口")
    
    class Config:
        extra = "allow"  # 允许额外字段

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_format = "{}"  # 由具体项目设置
        self._config: Dict[str, Any] = {}
        
    def load_config(self, env: str = None) -> AppConfig:
        """
        加载配置
        
        Args:
            env: 环境名称 (development/production)
        
        Returns:
            AppConfig: 配置对象
        """
        # 1. 加载默认配置
        default_config = self._load_file("default")
        self._config.update(default_config or {})
        
        # 2. 加载环境配置
        if env:
            env_config = self._load_file(env)
            self._config.update(env_config or {})
        
        # 3. 加载本地配置
        local_config = self._load_file("local")
        self._config.update(local_config or {})
        
        # 4. 环境变量覆盖
        self._load_from_env()
        
        return AppConfig(**self._config)
    
    def _load_file(self, name: str) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        file_path = self.config_dir / f"{name}.{self.config_format}"
        if not file_path.exists():
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            if self.config_format == 'yaml':
                if yaml is None:
                    raise ConfigError("PyYAML is required for yaml config")
                return yaml.safe_load(f)
            elif self.config_format == 'json':
                return json.load(f)
            elif self.config_format == 'ini':
                parser = ConfigParser()
                parser.read_file(f)
                return {s: dict(parser.items(s)) for s in parser.sections()}
            
        return None
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        prefix = f"{self.info.project_name.upper()}_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # 处理嵌套键
                keys = config_key.split('_')
                current = self._config
                for k in keys[:-1]:
                    current = current.setdefault(k, {})
                current[keys[-1]] = value

# 使用示例
if __name__ == '__main__':
    loader = ConfigLoader()
    loader.config_format = 'yaml'  # 或 'json' 或 'ini'
    config = loader.load_config(env='development')
    print(f"应用名称: {config.app_name}")
    print(f"调试模式: {config.debug}")
'''
        
        # 创建配置模块文件
        config_file = os.path.join(config_dir, 'config.py')
        with open(config_file, 'w') as f:
            f.write(config_content)
            
        # 创建配置文件示例
        self._create_config_examples(config_dir)
        
        # 创建config包的__init__.py
        init_file = os.path.join(config_dir, '__init__.py')
        with open(init_file, 'w') as f:
            f.write('"""配置管理包"""\n\n')
            f.write('from .config import ConfigLoader, AppConfig, ConfigError\n\n')
            f.write('__all__ = ["ConfigLoader", "AppConfig", "ConfigError"]\n')
            
    def _create_config_examples(self, config_dir):
        """创建配置文件示例"""
        example_config = {
            'app_name': self.info.project_name,
            'debug': True,
            'host': '127.0.0.1',
            'port': 8000,
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'mydb'
            }
        }
        
        if self.info.config_format == 'yaml':
            try:
                import yaml
                ext = 'yaml'
                def write_config(f, data):
                    yaml.safe_dump(data, f, default_flow_style=False)
            except ImportError:
                print("警告：未安装PyYAML，将使用JSON格式替代")
                self.info.config_format = 'json'
                
        if self.info.config_format == 'json':
            ext = 'json'
            def write_config(f, data):
                json.dump(data, f, indent=2)
        else:  # ini
            ext = 'ini'
            from configparser import ConfigParser
            def write_config(f, data):
                config = ConfigParser()
                config['DEFAULT'] = {
                    'app_name': data['app_name'],
                    'debug': str(data['debug']),
                    'host': data['host'],
                    'port': str(data['port'])
                }
                config['database'] = {
                    'host': data['database']['host'],
                    'port': str(data['database']['port']),
                    'name': data['database']['name']
                }
                config.write(f)
        
        # 创建默认配置
        with open(os.path.join(config_dir, f'default.{ext}'), 'w') as f:
            write_config(f, example_config)
            
        # 创建环境配置示例
        example_config['debug'] = False
        with open(os.path.join(config_dir, f'production.{ext}'), 'w') as f:
            write_config(f, example_config)
            
        # 创建本地配置示例
        example_config['database']['host'] = 'dev.local'
        with open(os.path.join(config_dir, f'local.{ext}.example'), 'w') as f:
            write_config(f, example_config)
            
        # 更新 .gitignore
        gitignore_path = os.path.join(self.project_dir, '.gitignore')
        with open(gitignore_path, 'a') as f:
            f.write(f'\n# Local config\nconfig/local.{ext}\n')

    def _create_helper_docs(self):
        """创建帮助文档"""
        docs_dir = os.path.join(self.project_dir, 'docs')
        helper_content = f"""# {self.info.project_name} 使用指南

本文档提供了项目中各个功能模块的使用方法和示例。

"""
        if self.info.use_logging:
            helper_content += """## 日志系统使用指南

### 1. 基本用法

```python
from utils.log import setup_logger

# 创建日志记录器
logger = setup_logger('my_module')

# 使用日志记录器
logger.debug('调试信息')    # 只会显示在终端
logger.info('普通信息')     # 同时记录到文件和终端
logger.warning('警告信息')  # 同时记录到文件和终端
logger.error('错误信息')    # 同时记录到文件和终端
```

### 2. 日志配置说明

- 日志文件位置：`logs/{logger_name}.log`
- 日志文件大小：最大 10MB，超过后自动轮转
- 保留文件数：最多保留 5 个历史文件

### 3. 日志级别

- 终端输出：DEBUG 及以上级别
- 文件记录：INFO 及以上级别

### 4. 日志格式

#### 终端输出格式
```
时间戳 - 模块名 - 日志级别 - [文件名:行号] - 消息内容
```

#### 文件记录格式
```
时间戳 - 模块名 - 日志级别 - 消息内容
```

### 5. 最佳实践

- 在模块级别创建日志记录器
- 使用有意义的日志记录器名称
- 适当使用不同的日志级别
- DEBUG：详细的调试信息
- INFO：重要的程序状态信息
- WARNING：需要注意但不是错误的情况
- ERROR：错误信息

### 6. 示例代码

```python
from utils.log import setup_logger

# 创建模块级别的日志记录器
logger = setup_logger(__name__)

class MyClass:
    def __init__(self):
        logger.debug('初始化 MyClass 实例')
        
    def process_data(self, data):
        logger.info(f'开始处理数据，数据大小：{len(data)}')
        try:
            # 处理数据
            result = self._process(data)
            logger.debug(f'数据处理结果：{result}')
            return result
        except Exception as e:
            logger.error(f'数据处理失败：{str(e)}')
            raise
```
"""

        if self.info.use_config:
            helper_content += f"""## 配置系统使用指南

### 1. 基本用法

```python
from config import ConfigLoader

# 创建配置加载器
loader = ConfigLoader()
loader.config_format = '{self.info.config_format}'  # 配置文件格式

# 加载配置
config = loader.load_config(env='development')  # 或 'production'

# 使用配置
print(f"应用名称: {{config.app_name}}")
print(f"调试模式: {{config.debug}}")
print(f"数据库配置: {{config.database['host']}}")
```

### 2. 配置文件

项目使用分层配置系统，按以下优先级从高到低加载：

1. 本地配置：`config/local.{self.info.config_format}`（不提交到Git）
2. 环境配置：`config/production.{self.info.config_format}`
3. 默认配置：`config/default.{self.info.config_format}`

### 3. 配置格式

使用 {self.info.config_format.upper()} 格式存储配置，示例：

"""
            if self.info.config_format == 'yaml':
                helper_content += """```yaml
app_name: myapp
debug: true
host: 127.0.0.1
port: 8000
database:
  host: localhost
  port: 5432
  name: mydb
```
"""
            elif self.info.config_format == 'json':
                helper_content += """```json
{
  "app_name": "myapp",
  "debug": true,
  "host": "127.0.0.1",
  "port": 8000,
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "mydb"
  }
}
```
"""
            else:  # ini
                helper_content += """```ini
[DEFAULT]
app_name = myapp
debug = true
host = 127.0.0.1
port = 8000

[database]
host = localhost
port = 5432
name = mydb
```
"""

            helper_content += """
### 4. 环境变量支持

可以使用环境变量覆盖配置值，环境变量名格式：`项目名称大写_配置路径`

示例：
```bash
# 设置数据库主机
export MYAPP_DATABASE_HOST=db.example.com

# 设置端口
export MYAPP_PORT=9000
```

### 5. 配置验证

使用 Pydantic 进行配置验证，可以在 `config.py` 中的 `AppConfig` 类中定义配置项：

```python
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    app_name: str = Field(default="", description="应用名称")
    debug: bool = Field(default=False, description="是否开启调试模式")
    port: int = Field(default=8000, description="服务端口")
    
    class Config:
        extra = "allow"  # 允许额外字段
```

### 6. 最佳实践

1. 敏感信息（密码、密钥等）使用环境变量或本地配置
2. 不同环境使用不同的配置文件
3. 使用类型注解和验证确保配置正确性
4. 将默认值定义在代码中，而不是配置文件中
"""

        # 写入帮助文档
        helper_file = os.path.join(docs_dir, 'helper.md')
        with open(helper_file, 'w', encoding='utf-8') as f:
            f.write(helper_content)

    def create_project(self):
        """创建项目目录结构"""
        # 创建项目目录
        self.project_dir = os.path.join(self.info.project_path, self.info.project_name)
        src_dir = os.path.join(self.project_dir, 'src', self.info.project_name)
        os.makedirs(src_dir, exist_ok=True)
        
        # 创建其他目录
        os.makedirs(os.path.join(self.project_dir, 'tests'), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, 'docs'), exist_ok=True)
        
        # 创建基础文件
        self.create_basic_files()
        
        # 创建帮助文档
        if self.info.use_logging or self.info.use_config:
            self._create_helper_docs()

    def init_git(self):
        """初始化git仓库"""
        if not self.info.use_git:
            return

        try:
            subprocess.run(['git', 'init'], cwd=self.project_dir, check=True)
            
            # 创建 .gitignore
            gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''
            with open(os.path.join(self.project_dir, '.gitignore'), 'w') as f:
                f.write(gitignore_content)

            # 初始化git提交
            subprocess.run(['git', 'add', '.'], cwd=self.project_dir, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.project_dir, check=True)
            print("Git仓库初始化成功！")
        except subprocess.CalledProcessError:
            print("警告：Git初始化失败。请确保已安装git。")
        except Exception as e:
            print(f"警告：Git初始化失败：{str(e)}")

    def create_venv(self):
        """创建虚拟环境"""
        if not self.info.use_venv:
            return

        try:
            venv_path = os.path.join(self.project_dir, '.venv')
            print(f"\n正在创建虚拟环境...")
            subprocess.run([self.info.venv_python, '-m', 'venv', venv_path], check=True)
            print("虚拟环境创建成功！")

            # 在README中添加使用所选Python版本的说明
            readme_path = os.path.join(self.project_dir, 'README.md')
            with open(readme_path, 'r') as f:
                content = f.read()
            content = content.replace(
                "python -m venv .venv",
                f"{self.info.venv_python} -m venv .venv  # 使用 {self.info.venv_python}"
            )
            with open(readme_path, 'w') as f:
                f.write(content)

        except subprocess.CalledProcessError:
            print("警告：虚拟环境创建失败")
        except Exception as e:
            print(f"警告：虚拟环境创建失败：{str(e)}")

    def create(self):
        """执行所有项目创建步骤"""
        print(f"\n开始创建项目 '{self.info.project_name}'...")
        self.create_project()
        self.init_git()
        self.create_venv()
        print(f"\n项目 '{self.info.project_name}' 创建成功！")
        print(f"位置：{self.project_dir}")
        print("\n接下来你可以：")
        print(f"1. cd {self.project_dir}")
        if self.info.use_venv:
            print("2. source .venv/bin/activate  # 激活虚拟环境")
            print("3. pip install -r requirements.txt  # 安装依赖")
        else:
            print("2. python -m venv .venv  # 创建虚拟环境")
            print("3. source .venv/bin/activate  # 激活虚拟环境")
            print("4. pip install -r requirements.txt  # 安装依赖")

def main():
    # 收集项目信息
    project_info = ProjectInfo()
    project_info.collect_info()
    
    # 创建项目
    creator = ProjectCreator(project_info)
    creator.create()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path
import re
import glob

class ProjectInfo:
    def __init__(self):
        self.project_name = ""
        self.project_path = ""
        self.author = ""
        self.email = ""
        self.description = ""
        self.version = "0.1.0"
        self.python_version = ">=3.6"
        self.license = "MIT"
        self.use_git = False
        self.use_venv = False
        self.venv_python = ""

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
        python_version = input("请输入所需的Python最低版本 (直接回车使用 3.6): ").strip()
        if python_version:
            self.python_version = f">={python_version}"

        # Git管理
        while True:
            git_choice = input("是否使用Git管理项目? (y/n): ").strip().lower()
            if git_choice in ['y', 'n']:
                self.use_git = (git_choice == 'y')
                break
            print("错误：请输入 y 或 n")

        # 虚拟环境
        while True:
            venv_choice = input("是否创建虚拟环境? (y/n): ").strip().lower()
            if venv_choice in ['y', 'n']:
                self.use_venv = (venv_choice == 'y')
                break
            print("错误：请输入 y 或 n")

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
        self.create_project_structure()
        self.create_basic_files()
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
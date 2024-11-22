from setuptools import setup, find_packages

def read_requirements(filename):
    """读取requirements.txt文件内容."""
    with open(filename, 'r', encoding='utf-8') as f:
        # 过滤掉注释和空行
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="app",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=read_requirements('requirements.txt'),
    author="hala",
    author_email="a@b.c",
    description="asdasdfasdf",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hala/app",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

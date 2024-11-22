from setuptools import setup, find_packages

def read_requirements(filename):
    """读取requirements.txt文件内容"""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f 
                if line.strip() and not line.startswith('#')]

setup(
    name="project_creater",
    version="1.0.1",
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'create-project=main:main',
        ],
    },
    author="Kong Haifeng",
    author_email="konghaifeng@cmcm.com",
    description="A Python project structure generator with logging and configuration support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/project_creater",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

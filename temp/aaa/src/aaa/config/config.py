"""
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

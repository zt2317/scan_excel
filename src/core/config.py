"""配置存储模块

实现JSON格式的配置持久化，支持webhook URL等敏感信息的本地存储。
"""

import json
from pathlib import Path
from typing import Optional


class ConfigError(Exception):
    """配置操作错误"""
    pass


class ConfigStore:
    """配置存储类
    
    使用JSON格式持久化配置到本地文件系统。
    配置文件被.gitignore排除，不提交到版本控制。
    """
    
    DEFAULT_CONFIG_FILENAME = "webhook_config.json"
    
    def __init__(self, project_root: Optional[Path] = None):
        """初始化配置存储
        
        Args:
            project_root: 项目根目录路径，默认为当前工作目录
        """
        if project_root is None:
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(project_root)
        
        self.config_dir = self.project_root / "config"
        self.config_file = self.config_dir / self.DEFAULT_CONFIG_FILENAME
    
    def load(self) -> dict:
        """加载配置
        
        如果配置文件不存在，返回空字典。
        如果配置文件格式错误，抛出ConfigError。
        
        Returns:
            配置字典
            
        Raises:
            ConfigError: JSON解析错误
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as e:
            raise ConfigError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise ConfigError(f"配置文件读取失败: {e}")
    
    def save(self, config: dict) -> None:
        """保存配置
        
        自动创建配置目录（如不存在）。
        使用UTF-8编码，支持中文内容，格式化输出便于查看。
        
        Args:
            config: 配置字典
            
        Raises:
            ConfigError: 写入失败
        """
        try:
            # 确保配置目录存在
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # 写入JSON文件，支持中文，格式化缩进
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ConfigError(f"配置保存失败: {e}")
    
    def get_webhook_url(self) -> Optional[str]:
        """获取webhook URL
        
        Returns:
            webhook URL或None
        """
        config = self.load()
        return config.get('webhook_url')
    
    def set_webhook_url(self, url: str) -> None:
        """设置webhook URL
        
        Args:
            url: 企业微信webhook URL
        """
        config = self.load()
        config['webhook_url'] = url
        self.save(config)
    
    def get_last_folder(self) -> Optional[str]:
        """获取上次使用的文件夹路径
        
        Returns:
            文件夹路径或None
        """
        config = self.load()
        return config.get('last_folder')
    
    def set_last_folder(self, folder: str) -> None:
        """设置上次使用的文件夹路径
        
        Args:
            folder: 文件夹路径
        """
        config = self.load()
        config['last_folder'] = folder
        self.save(config)

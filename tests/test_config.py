"""ConfigStore 单元测试"""

import pytest
import json
import tempfile
from pathlib import Path
from src.core.config import ConfigStore, ConfigError


class TestConfigStore:
    """测试 ConfigStore 类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    @pytest.fixture
    def config_store(self, temp_dir):
        """创建ConfigStore实例"""
        return ConfigStore(project_root=temp_dir)

    def test_load_nonexistent(self, config_store):
        """测试加载不存在的配置文件，返回空字典"""
        result = config_store.load()
        assert result == {}

    def test_save_and_load(self, config_store):
        """测试保存和加载配置"""
        config = {'webhook_url': 'https://example.com/webhook'}
        config_store.save(config)
        
        result = config_store.load()
        assert result == config

    def test_get_set_webhook_url(self, config_store):
        """测试webhook_url的getter和setter"""
        url = 'https://qyapi.weixin.qq.com/webhook'
        config_store.set_webhook_url(url)
        
        result = config_store.get_webhook_url()
        assert result == url

    def test_get_set_last_folder(self, config_store):
        """测试last_folder的getter和setter"""
        folder = '/Users/test/Documents'
        config_store.set_last_folder(folder)
        
        result = config_store.get_last_folder()
        assert result == folder

    def test_overwrite_existing(self, config_store):
        """测试覆盖现有配置"""
        config_store.save({'webhook_url': 'old_url'})
        config_store.save({'webhook_url': 'new_url', 'last_folder': '/new/path'})
        
        result = config_store.load()
        assert result['webhook_url'] == 'new_url'
        assert result['last_folder'] == '/new/path'

    def test_invalid_json(self, config_store, temp_dir):
        """测试加载损坏的JSON文件时抛出ConfigError"""
        # 手动写入无效的JSON
        config_dir = temp_dir / "config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "webhook_config.json"
        config_file.write_text("invalid json content")
        
        with pytest.raises(ConfigError) as exc_info:
            config_store.load()
        
        assert "配置文件格式错误" in str(exc_info.value)

    def test_empty_file(self, config_store, temp_dir):
        """测试加载空文件，返回空字典"""
        config_dir = temp_dir / "config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "webhook_config.json"
        config_file.write_text("")
        
        result = config_store.load()
        assert result == {}

    def test_chinese_content(self, config_store):
        """测试中文内容处理"""
        config = {
            'webhook_url': 'https://example.com',
            'last_folder': '/用户/文档/测试文件夹'
        }
        config_store.save(config)
        
        result = config_store.load()
        assert result['last_folder'] == '/用户/文档/测试文件夹'

    def test_config_directory_auto_created(self, config_store):
        """测试配置目录自动创建"""
        config = {'webhook_url': 'test'}
        config_store.save(config)
        
        assert config_store.config_dir.exists()

    def test_multiple_config_values(self, config_store):
        """测试多个配置值"""
        config_store.set_webhook_url('url1')
        config_store.set_last_folder('/path1')
        
        result = config_store.load()
        assert result['webhook_url'] == 'url1'
        assert result['last_folder'] == '/path1'
        
        # 更新其中一个值
        config_store.set_webhook_url('url2')
        result = config_store.load()
        assert result['webhook_url'] == 'url2'
        assert result['last_folder'] == '/path1'  # last_folder应保持不变

    def test_get_unset_webhook_url(self, config_store):
        """测试获取未设置的webhook_url返回None"""
        result = config_store.get_webhook_url()
        assert result is None

    def test_get_unset_last_folder(self, config_store):
        """测试获取未设置的last_folder返回None"""
        result = config_store.get_last_folder()
        assert result is None

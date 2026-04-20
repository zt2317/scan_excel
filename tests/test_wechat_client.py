"""企业微信客户端单元测试"""

import pytest
import json
import requests
from unittest.mock import Mock, patch
from src.core.wechat_client import WeChatWorkClient
from src.core.config import ConfigStore, ConfigError
from src.core.exceptions import WeChatAPIError, NetworkError


class TestWeChatWorkClientInit:
    """测试客户端初始化"""

    def test_init_with_webhook_url(self):
        """使用提供的webhook_url初始化"""
        url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test"
        client = WeChatWorkClient(webhook_url=url)
        
        assert client.webhook_url == url
        assert client.timeout == 30
        assert client.max_retries == 3

    def test_init_loads_from_config(self, tmp_path):
        """从配置加载webhook_url"""
        url = "https://qyapi.weixin.qq.com/webhook"
        
        # 创建临时配置
        config_store = ConfigStore(project_root=tmp_path)
        config_store.set_webhook_url(url)
        
        client = WeChatWorkClient(config_store=config_store)
        
        assert client.webhook_url == url

    def test_init_raises_when_no_webhook(self, tmp_path):
        """未提供webhook且配置不存在时抛出ConfigError"""
        config_store = ConfigStore(project_root=tmp_path)
        
        with pytest.raises(ConfigError) as exc_info:
            WeChatWorkClient(config_store=config_store)
        
        assert "未配置webhook地址" in str(exc_info.value)

    def test_provided_url_overrides_config(self, tmp_path):
        """提供的webhook_url优先于配置"""
        config_url = "https://config.url"
        provided_url = "https://provided.url"
        
        config_store = ConfigStore(project_root=tmp_path)
        config_store.set_webhook_url(config_url)
        
        client = WeChatWorkClient(
            webhook_url=provided_url,
            config_store=config_store
        )
        
        assert client.webhook_url == provided_url

    def test_custom_timeout(self):
        """自定义超时时间"""
        client = WeChatWorkClient(
            webhook_url="https://test.url",
            timeout=60
        )
        
        assert client.timeout == 60

    def test_custom_max_retries(self):
        """自定义最大重试次数"""
        client = WeChatWorkClient(
            webhook_url="https://test.url",
            max_retries=5
        )
        
        assert client.max_retries == 5
        assert len(client.retry_delays) == 5


class TestWeChatWorkClientSend:
    """测试消息发送功能"""

    @pytest.fixture
    def client(self):
        """创建带mock的客户端"""
        return WeChatWorkClient(webhook_url="https://test.url")

    @patch('src.core.wechat_client.requests.post')
    def test_send_single_chunk_success(self, mock_post, client):
        """成功发送单一切片"""
        mock_post.return_value.json.return_value = {"errcode": 0, "errmsg": "ok"}
        
        result = client.send_markdown("|a|b|\n|---|---|\n|c|d|")
        
        assert len(result) == 1
        assert result[0]['success'] is True
        assert result[0]['chunk_num'] == 1
        assert result[0]['total'] == 1

    @patch('src.core.wechat_client.requests.post')
    def test_send_multiple_chunks(self, mock_post, client):
        """发送多个切片"""
        mock_post.return_value.json.return_value = {"errcode": 0, "errmsg": "ok"}
        
        # 创建超过15行的表格
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(20):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        result = client.send_markdown(markdown)
        
        # 应该分成2片
        assert len(result) == 2
        # 每片都成功
        for r in result:
            assert r['success'] is True

    @patch('src.core.wechat_client.requests.post')
    def test_empty_message(self, mock_post, client):
        """空消息返回空列表"""
        result = client.send_markdown("")
        
        assert result == []
        mock_post.assert_not_called()

    @patch('src.core.wechat_client.requests.post')
    def test_whitespace_only_message(self, mock_post, client):
        """只有空白字符的消息返回空列表"""
        result = client.send_markdown("   \n   ")
        
        assert result == []
        mock_post.assert_not_called()

    @patch('src.core.wechat_client.requests.post')
    def test_sequence_markers_added(self, mock_post, client):
        """验证序号标记被添加"""
        mock_post.return_value.json.return_value = {"errcode": 0, "errmsg": "ok"}
        
        # 创建超过15行的表格（会分成多片）
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(20):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        client.send_markdown(markdown)
        
        # 检查第二次调用（最后一片）包含（完）标记
        calls = mock_post.call_args_list
        assert len(calls) == 2
        
        # 获取最后一次调用的payload
        last_payload = calls[1][1]['json']
        content = last_payload['markdown']['content']
        assert "（第2/2片）（完）" in content


class TestWeChatWorkClientRetry:
    """测试重试机制"""

    @pytest.fixture
    def client(self):
        """创建带mock的客户端"""
        return WeChatWorkClient(webhook_url="https://test.url")

    @patch('src.core.wechat_client.requests.post')
    @patch('src.core.wechat_client.time.sleep')
    def test_retry_on_server_busy(self, mock_sleep, mock_post, client):
        """服务器繁忙时重试"""
        # 第一次返回繁忙，第二次成功
        mock_post.return_value.json.side_effect = [
            {"errcode": -1, "errmsg": "system busy"},
            {"errcode": 0, "errmsg": "ok"}
        ]
        
        result = client.send_markdown("|a|b|\n|---|---|\n|c|d|")
        
        # 应该调用两次
        assert mock_post.call_count == 2
        # 应该有重试延迟
        mock_sleep.assert_called()
        # 最终结果成功
        assert result[0]['success'] is True

    @patch('src.core.wechat_client.requests.post')
    def test_no_retry_on_invalid_key(self, mock_post, client):
        """无效key时不重试"""
        mock_post.return_value.json.return_value = {
            "errcode": 40013,
            "errmsg": "invalid key"
        }
        
        result = client.send_markdown("|a|b|\n|---|---|\n|c|d|")
        
        # 只调用一次（不重试）
        assert mock_post.call_count == 1
        # 结果失败
        assert result[0]['success'] is False
        assert "webhook地址无效" in result[0]['error']

    @patch('src.core.wechat_client.requests.post')
    def test_no_retry_on_message_too_large(self, mock_post, client):
        """消息过大时不重试"""
        mock_post.return_value.json.return_value = {
            "errcode": 40008,
            "errmsg": "message too large"
        }
        
        result = client.send_markdown("|a|b|\n|---|---|\n|c|d|")
        
        # 只调用一次（不重试）
        assert mock_post.call_count == 1
        # 结果失败
        assert result[0]['success'] is False
        assert "消息内容过长" in result[0]['error']

    @patch('src.core.wechat_client.requests.post')
    @patch('src.core.wechat_client.time.sleep')
    def test_retry_on_timeout(self, mock_sleep, mock_post, client):
        """超时时重试"""
        # 前两次超时，第三次成功
        mock_post.side_effect = [
            pytest.raises(requests.Timeout),
            pytest.raises(requests.Timeout),
            Mock(json=lambda: {"errcode": 0, "errmsg": "ok"})
        ]
        
        # 使用真正的requests.Timeout异常
        mock_post.side_effect = [
            requests.Timeout(),
            requests.Timeout(),
            Mock(json=lambda: {"errcode": 0, "errmsg": "ok"})
        ]
        
        result = client.send_markdown("|a|b|\n|---|---|\n|c|d|")
        
        # 应该调用三次（初始+2次重试）
        assert mock_post.call_count == 3
        # 最终结果成功
        assert result[0]['success'] is True

    @patch('src.core.wechat_client.requests.post')
    @patch('src.core.wechat_client.time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_post, client):
        """超过最大重试次数后失败"""
        # 所有调用都超时
        mock_post.side_effect = requests.Timeout()
        
        result = client.send_markdown("|a|b|\n|---|---|\n|c|d|")
        
        # 应该调用4次（初始+3次重试）
        assert mock_post.call_count == 4
        # 结果失败
        assert result[0]['success'] is False
        assert "超时" in result[0]['error']


class TestWeChatWorkClientPayload:
    """测试请求体格式"""

    @pytest.fixture
    def client(self):
        """创建带mock的客户端"""
        return WeChatWorkClient(webhook_url="https://test.url")

    @patch('src.core.wechat_client.requests.post')
    def test_correct_payload_format(self, mock_post, client):
        """验证请求体格式正确"""
        mock_post.return_value.json.return_value = {"errcode": 0, "errmsg": "ok"}
        
        client.send_markdown("测试内容")
        
        # 验证调用参数
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://test.url"
        
        payload = call_args[1]['json']
        assert payload['msgtype'] == 'markdown'
        assert 'content' in payload['markdown']

    @patch('src.core.wechat_client.requests.post')
    def test_timeout_parameter(self, mock_post, client):
        """验证超时参数传递"""
        mock_post.return_value.json.return_value = {"errcode": 0, "errmsg": "ok"}
        
        client.send_markdown("测试")
        
        call_args = mock_post.call_args
        assert call_args[1]['timeout'] == 30  # 默认30秒


class TestWeChatWorkClientBlocking:
    """测试阻塞式失败处理"""

    @pytest.fixture
    def client(self):
        """创建带mock的客户端"""
        return WeChatWorkClient(webhook_url="https://test.url")

    @patch('src.core.wechat_client.requests.post')
    def test_stop_on_first_failure(self, mock_post, client):
        """第一片失败时停止发送后续切片"""
        # 第一次失败，后面应该不再调用
        mock_post.return_value.json.return_value = {
            "errcode": 40013,
            "errmsg": "invalid key"
        }
        
        # 创建多片消息
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(20):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        result = client.send_markdown(markdown)
        
        # 应该只发送了第一片
        assert mock_post.call_count == 1
        # 结果只有第一片
        assert len(result) == 1
        assert result[0]['success'] is False


class TestWeChatWorkClientChunkDelay:
    """测试切片间隔"""

    @pytest.fixture
    def client(self):
        """创建带mock的客户端"""
        return WeChatWorkClient(webhook_url="https://test.url")

    @patch('src.core.wechat_client.requests.post')
    @patch('src.core.wechat_client.time.sleep')
    def test_delay_between_chunks(self, mock_sleep, mock_post, client):
        """切片之间有延迟"""
        mock_post.return_value.json.return_value = {"errcode": 0, "errmsg": "ok"}
        
        # 创建多片消息
        rows = ["| 日期 | 发货人 |", "|---|---|"]
        for i in range(20):
            rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1} |")
        
        markdown = "\n".join(rows)
        client.send_markdown(markdown)
        
        # 2片之间应该有1次延迟
        assert mock_sleep.call_count == 1
        # 延迟应该是1秒
        mock_sleep.assert_called_with(1.0)

    @patch('src.core.wechat_client.requests.post')
    @patch('src.core.wechat_client.time.sleep')
    def test_no_delay_after_last_chunk(self, mock_sleep, mock_post, client):
        """最后一片之后没有延迟"""
        mock_post.return_value.json.return_value = {"errcode": 0, "errmsg": "ok"}
        
        # 单一片消息
        client.send_markdown("|a|b|\n|---|---|\n|c|d|")
        
        # 不应该有延迟
        mock_sleep.assert_not_called()

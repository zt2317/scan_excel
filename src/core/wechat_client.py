"""企业微信客户端

实现企业微信webhook消息推送，支持消息切片、重试机制和错误处理。
"""

import time
import json
import requests
from typing import Optional, List, Dict, Any

from .config import ConfigStore, ConfigError
from .exceptions import WeChatAPIError, NetworkError


class WeChatWorkClient:
    """企业微信工作群机器人客户端
    
    支持发送Markdown格式消息，自动处理消息切片、顺序发送和重试机制。
    
    Attributes:
        webhook_url: 企业微信webhook地址
        timeout: HTTP请求超时时间（秒）
        max_retries: 最大重试次数
        retry_delays: 重试延迟列表（秒）
    """
    
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAYS = [1, 2, 4]  # 指数退避：1s, 2s, 4s
    DEFAULT_ROWS_PER_CHUNK = 15
    DEFAULT_CHUNK_DELAY = 1.0  # 切片间间隔（秒）
    
    # 企业微信错误码
    ERR_SUCCESS = 0
    ERR_BUSY = -1
    ERR_INVALID_KEY = 40013
    ERR_MESSAGE_TOO_LARGE = 40008
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        config_store: Optional[ConfigStore] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES
    ):
        """初始化企业微信客户端
        
        Args:
            webhook_url: 可选，直接指定webhook URL。如不提供，从配置加载
            config_store: 可选，ConfigStore实例。如不提供，创建默认实例
            timeout: HTTP请求超时时间（秒），默认30秒
            max_retries: 最大重试次数，默认3次
            
        Raises:
            ConfigError: 未提供webhook_url且无法从配置加载时抛出
        """
        self.timeout = timeout
        self.max_retries = max_retries
        # 根据max_retries生成退避延迟列表
        self.retry_delays = [2 ** i for i in range(max_retries)]
        
        # 优先使用直接提供的webhook_url
        if webhook_url:
            self.webhook_url = webhook_url
        else:
            # 从配置加载
            if config_store is None:
                config_store = ConfigStore()
            self.webhook_url = config_store.get_webhook_url()
            
            if not self.webhook_url:
                raise ConfigError("未配置webhook地址，请先设置企业微信机器人")
    
    def send_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """发送图片消息
        
        Args:
            image_bytes: 图片字节数据
            
        Returns:
            发送结果字典
        """
        import base64
        import hashlib
        
        # 将图片转为base64
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        md5 = hashlib.md5(image_bytes).hexdigest()
        
        # 构建请求体
        payload = {
            "msgtype": "image",
            "image": {
                "base64": base64_data,
                "md5": md5
            }
        }
        
        # 发送（带重试）
        return self._send_with_retry(payload, 1, 1)
    
    def send_markdown(self, markdown_text: str) -> List[Dict[str, Any]]:
        """发送Markdown消息
        
        自动处理消息切片，按顺序发送，支持重试机制。
        
        Args:
            markdown_text: Markdown格式消息文本
            
        Returns:
            发送结果列表，每项包含:
            - success: 是否成功（bool）
            - chunk_num: 切片序号（从1开始）
            - total: 总切片数
            - error: 错误信息（失败时）
            
        Raises:
            WeChatAPIError: API返回错误且不可重试时
            NetworkError: 网络错误超过重试次数时
        """
        # 空消息检查
        if not markdown_text or not markdown_text.strip():
            return []
        
        # 切片
        chunks = self._split_markdown_table(markdown_text)
        if not chunks:
            return []
        
        total = len(chunks)
        results = []
        
        for i, chunk in enumerate(chunks, 1):
            is_last = (i == total)
            
            try:
                result = self._send_single_chunk(chunk, i, total, is_last)
                results.append(result)
                
                # 发送失败时停止（阻塞式行为 per D-10）
                if not result['success']:
                    break
                
                # 非最后一片，添加延迟
                if not is_last:
                    time.sleep(self.DEFAULT_CHUNK_DELAY)
                    
            except (WeChatAPIError, NetworkError) as e:
                # 错误时停止发送
                results.append({
                    'success': False,
                    'chunk_num': i,
                    'total': total,
                    'error': str(e)
                })
                break
        
        return results
    
    def _split_markdown_table(
        self,
        markdown_text: str,
        rows_per_chunk: int = DEFAULT_ROWS_PER_CHUNK
    ) -> List[str]:
        """拆分Markdown表格为多个切片
        
        每片包含表头，数据行按指定数量分割。
        
        Args:
            markdown_text: Markdown表格文本
            rows_per_chunk: 每片数据行数，默认15行
            
        Returns:
            切片列表，每片是完整的Markdown表格
        """
        if not markdown_text:
            return []
        
        markdown_text = markdown_text.strip()
        
        if not markdown_text:
            return []
        
        lines = markdown_text.split('\n')
        
        if not lines:
            return []
        
        # 查找表头行（第一行包含 | 的行）
        header_idx = -1
        for i, line in enumerate(lines):
            if '|' in line:
                header_idx = i
                break
        
        if header_idx == -1:
            # 不是表格，作为单一片返回
            return [markdown_text]
        
        header_line = lines[header_idx]
        
        # 查找分隔行（下一行包含 --- ）
        separator_idx = header_idx + 1
        if separator_idx < len(lines) and '---' in lines[separator_idx]:
            separator_line = lines[separator_idx]
            data_start = separator_idx + 1
        else:
            # 没有标准分隔符，把下一行当成分隔符
            separator_line = '---'
            data_start = separator_idx
        
        # 提取数据行
        data_lines = []
        for line in lines[data_start:]:
            line = line.strip()
            if line and '|' in line:
                data_lines.append(line)
        
        if not data_lines:
            # 只有表头，返回单一片
            return [markdown_text]
        
        # 按行数切片
        chunks = []
        for i in range(0, len(data_lines), rows_per_chunk):
            chunk_data = data_lines[i:i + rows_per_chunk]
            
            # 重建表格
            chunk_lines = [header_line, separator_line] + chunk_data
            chunk_text = '\n'.join(chunk_lines)
            chunks.append(chunk_text)
        
        return chunks
    
    def _send_single_chunk(
        self,
        chunk: str,
        chunk_num: int,
        total: int,
        is_last: bool
    ) -> Dict[str, Any]:
        """发送单个切片
        
        Args:
            chunk: 切片内容
            chunk_num: 切片序号（从1开始）
            total: 总切片数
            is_last: 是否为最后一片
            
        Returns:
            发送结果字典
        """
        # 添加序号标记
        if total > 1:
            marker = f"（第{chunk_num}/{total}片）"
            if is_last:
                marker += "（完）"
            content = f"{marker}\n{chunk}"
        else:
            content = chunk
        
        # 构建请求体
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        # 发送（带重试）
        return self._send_with_retry(payload, chunk_num, total)
    
    def _send_with_retry(
        self,
        payload: Dict[str, Any],
        chunk_num: int,
        total: int
    ) -> Dict[str, Any]:
        """带重试机制的发送
        
        实现指数退避重试策略：1s → 2s → 4s
        
        Args:
            payload: 请求体
            chunk_num: 切片序号
            total: 总切片数
            
        Returns:
            发送结果字典
            
        Raises:
            WeChatAPIError: API返回不可重试错误时
            NetworkError: 网络错误超过重试次数时
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                # 解析响应
                try:
                    result = response.json()
                except json.JSONDecodeError:
                    err_msg = f"无法解析API响应: {response.text[:100]}"
                    if attempt < self.max_retries:
                        last_error = err_msg
                        time.sleep(self.retry_delays[attempt])
                        continue
                    raise WeChatAPIError(err_msg)
                
                errcode = result.get('errcode', -1)
                errmsg = result.get('errmsg', '未知错误')
                
                # 成功
                if errcode == self.ERR_SUCCESS:
                    return {
                        'success': True,
                        'chunk_num': chunk_num,
                        'total': total,
                        'attempts': attempt + 1
                    }
                
                # 可重试错误：服务器繁忙
                if errcode == self.ERR_BUSY and attempt < self.max_retries:
                    last_error = f"服务器繁忙 (errcode={errcode})"
                    time.sleep(self.retry_delays[attempt])
                    continue
                
                # 不可重试错误
                if errcode == self.ERR_INVALID_KEY:
                    raise WeChatAPIError(
                        "webhook地址无效，请检查配置",
                        errcode=errcode
                    )
                elif errcode == self.ERR_MESSAGE_TOO_LARGE:
                    raise WeChatAPIError(
                        "消息内容过长",
                        errcode=errcode
                    )
                else:
                    raise WeChatAPIError(
                        f"发送失败: {errmsg}",
                        errcode=errcode
                    )
                
            except requests.Timeout:
                err_msg = "网络连接超时，请检查网络后重试"
                if attempt < self.max_retries:
                    last_error = err_msg
                    time.sleep(self.retry_delays[attempt])
                    continue
                raise NetworkError(err_msg)
                
            except requests.ConnectionError as e:
                err_msg = "网络连接失败，请检查网络后重试"
                if attempt < self.max_retries:
                    last_error = err_msg
                    time.sleep(self.retry_delays[attempt])
                    continue
                raise NetworkError(err_msg, original_error=e)
        
        # 所有重试都失败
        return {
            'success': False,
            'chunk_num': chunk_num,
            'total': total,
            'error': last_error or "发送失败，已达到最大重试次数"
        }

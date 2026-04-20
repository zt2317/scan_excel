"""自定义异常类

定义企业微信客户端和配置模块的异常类，提供清晰的错误信息。
"""

from .config import ConfigError


class WeChatAPIError(Exception):
    """企业微信API错误
    
    当企业微信API返回非成功响应时抛出。
    包含错误码(errcode)供调用者判断错误类型。
    
    Attributes:
        message: 错误描述信息
        errcode: 企业微信错误码（可选）
    """
    
    def __init__(self, message: str, errcode: int = None):
        """初始化API错误
        
        Args:
            message: 错误描述
            errcode: 企业微信错误码（如40013表示key无效）
        """
        super().__init__(message)
        self.message = message
        self.errcode = errcode
    
    def __str__(self):
        if self.errcode is not None:
            return f"[{self.errcode}] {self.message}"
        return self.message


class NetworkError(Exception):
    """网络连接错误
    
    当HTTP请求超时或连接失败时抛出。
    通常由requests.Timeout或requests.ConnectionError转换而来。
    
    Attributes:
        message: 错误描述信息
        original_error: 原始异常对象（可选）
    """
    
    def __init__(self, message: str, original_error: Exception = None):
        """初始化网络错误
        
        Args:
            message: 错误描述
            original_error: 导致此错误的原始异常
        """
        super().__init__(message)
        self.message = message
        self.original_error = original_error


# 重新导出ConfigError以便统一导入
__all__ = [
    'WeChatAPIError',
    'NetworkError',
    'ConfigError',
]

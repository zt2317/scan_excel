# Phase 2: 企业微信集成 - Technical Research

**Researched:** 2026-04-20
**Phase:** 2 - 企业微信集成
**Goal:** 实现企业微信webhook消息推送和切片发送

---

## 1. Enterprise WeChat Webhook API

### 1.1 API Endpoint

企业微信使用固定的webhook URL格式：
```
POST https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}
```

- `webhook_key`: 在企业微信后台创建群机器人时生成
- 每个群有独立的key
- 无需access_token（机器人webhook是独立机制）

### 1.2 Request Format

```python
import requests
import json

url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

# Markdown消息
payload = {
    "msgtype": "markdown",
    "markdown": {
        "content": "# 标题\n| 列1 | 列2 |\n| --- | --- |"
    }
}

response = requests.post(url, json=payload, timeout=30)
```

### 1.3 Response Format

**成功：**
```json
{
    "errcode": 0,
    "errmsg": "ok"
}
```

**常见错误：**
| 错误码 | 含义 | 处理建议 |
|--------|------|----------|
| 0 | 成功 | - |
| -1 | 系统繁忙 | 重试 |
| 40001 | access_token无效 | 检查webhook URL |
| 40004 | 不支持的msgtype | 使用正确的msgtype |
| 40008 | 消息体过大 | 必须切片发送 |
| 40009 | 消息内容为空 | 检查content |
| 40013 | key无效 | 检查webhook配置 |
| 40014 | 消息发送频繁 | 限流，增加间隔 |
| 45009 | 接口调用超过频率限制 | 严重限流，降低频率 |

---

## 2. Message Limits & Slicing

### 2.1 硬限制

- **最大长度**: 2048 UTF-8字符（企业微信限制）
- **Markdown格式开销**: 表格每行约40-60字符
- **安全余量**: 建议每片 ≤ 1800字符

### 2.2 切片策略

**按行数切分**（推荐）：
- 15行数据/片（保守估计）
- 保留表头开销：约80字符
- 每行开销：约50-80字符
- 计算：80 + 15*70 = 1130字符（安全）

**动态计算**（可选增强）：
```python
def estimate_characters(table_rows):
    """估算Markdown表格字符数"""
    header = 80  # 表头固定开销
    per_row = 60  # 每行平均字符数
    return header + len(table_rows) * per_row
```

### 2.3 多片消息格式

```markdown
（第1/3片）
| 日期 | 发货人 | 提单号 | 入库未扫 | 出库未扫 |
|------|--------|--------|----------|----------|
| ...  | ...    | ...    | ...      | ...      |

（第2/3片）
| 日期 | 发货人 | 提单号 | 入库未扫 | 出库未扫 |
|------|--------|--------|----------|----------|
| ...  | ...    | ...    | ...      | ...      |

（第3/3片 - 完）
| 日期 | 发货人 | 提单号 | 入库未扫 | 出库未扫 |
|------|--------|--------|----------|----------|
| ...  | ...    | ...    | ...      | ...      |
```

---

## 3. Rate Limiting

### 3.1 官方限制

- **每个机器人**: 20条/秒
- **超出限制**: 返回错误码40014或45009
- **建议间隔**: 1秒（保守，留10倍余量）

### 3.2 实际策略

```python
import time

def send_with_rate_limit(chunks):
    """顺序发送，带间隔"""
    for i, chunk in enumerate(chunks):
        if i > 0:
            time.sleep(1.0)  # 1秒间隔
        send_chunk(chunk)
```

### 3.3 顺序保证

- 必须阻塞式发送（非并发）
- 失败时暂停后续发送，先处理重试
- 使用列表索引保证顺序

---

## 4. Retry Mechanism

### 4.1 可重试错误

| 错误类型 | 错误码/异常 | 重试? | 说明 |
|----------|-------------|-------|------|
| 超时 | Timeout | 是 | 网络临时问题 |
| 连接错误 | ConnectionError | 是 | 网络不稳定 |
| 系统繁忙 | -1 | 是 | 服务器端问题 |
| 限流 | 40014, 45009 | 否* | 需延长间隔后再发 |
| 无效key | 40013 | 否 | 配置错误 |
| 消息过大 | 40008 | 否 | 需切片处理 |

*注：限流错误需调整间隔后重试，不是简单重试

### 4.2 指数退避实现

```python
import time

def exponential_backoff(attempt, base_delay=1.0, max_delay=10.0):
    """
    指数退避计算
    attempt: 0-based重试次数
    返回: 延迟秒数
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    return delay

# 使用示例：
# 第0次（原始请求）：0秒
# 第1次重试：1秒
# 第2次重试：2秒
# 第3次重试：4秒（上限）
```

### 4.3 完整重试逻辑

```python
def send_with_retry(chunk, max_retries=3):
    """带重试的消息发送"""
    for attempt in range(max_retries):
        try:
            response = send_request(chunk)
            if response['errcode'] == 0:
                return {'success': True, 'attempts': attempt + 1}
            
            # 检查是否可重试
            if response['errcode'] in [-1]:  # 系统繁忙
                if attempt < max_retries - 1:
                    delay = exponential_backoff(attempt)
                    time.sleep(delay)
                    continue
            
            # 不可重试的错误
            return {
                'success': False,
                'error': response['errmsg'],
                'errcode': response['errcode']
            }
            
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt < max_retries - 1:
                delay = exponential_backoff(attempt)
                time.sleep(delay)
                continue
            return {
                'success': False,
                'error': f'网络错误: {str(e)}',
                'attempts': attempt + 1
            }
```

---

## 5. Configuration Storage

### 5.1 存储位置策略

| 方案 | 优点 | 缺点 |
|------|------|------|
| 用户目录 (~/.config/) | 标准做法，跨平台 | 用户不易找到 |
| 应用目录 (./config/) | 易于访问，备份方便 | 可能意外提交git |
| 系统注册表 (Windows) | 原生体验 | 跨平台复杂 |

**推荐**: 应用目录 + .gitignore保护（符合用户决策）

### 5.2 文件结构

```
project/
├── config/
│   └── webhook_config.json   # <-- .gitignore保护
├── src/
│   └── ...
└── ...
```

### 5.3 JSON格式

```json
{
    "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
    "last_folder": "/Users/xxx/Documents"
}
```

### 5.4 路径处理

```python
from pathlib import Path
import json
import os

class ConfigStore:
    def __init__(self, project_root=None):
        if project_root is None:
            # 自动检测项目根目录
            self.config_dir = Path(__file__).parent.parent.parent / 'config'
        else:
            self.config_dir = Path(project_root) / 'config'
        
        self.config_file = self.config_dir / 'webhook_config.json'
    
    def load(self):
        if not self.config_file.exists():
            return {}
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self, config):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
```

---

## 6. Client Architecture

### 6.1 类设计

```python
class WeChatWorkClient:
    """企业微信webhook客户端"""
    
    def __init__(self, webhook_url=None, config_store=None):
        self.config_store = config_store or ConfigStore()
        self.webhook_url = webhook_url or self._load_webhook_url()
        self.timeout = 30
        self.max_retries = 3
    
    def send_markdown(self, markdown_text):
        """发送Markdown消息（自动切片）"""
        chunks = self._split_message(markdown_text)
        results = []
        
        for i, chunk in enumerate(chunks):
            result = self._send_chunk(chunk, chunk_num=i+1, total=len(chunks))
            results.append(result)
            
            if not result['success']:
                # 失败时停止后续发送
                break
            
            if i < len(chunks) - 1:
                time.sleep(1.0)  # 间隔
        
        return results
    
    def _split_message(self, text):
        """消息切片"""
        # 按行分割，每片15行
        lines = text.split('\n')
        # 实现切片逻辑...
    
    def _send_chunk(self, chunk, chunk_num, total):
        """发送单片消息"""
        # 添加片序号
        content = f"（第{chunk_num}/{total}片）\n{chunk}"
        if chunk_num == total:
            content += "（完）"
        
        # 构造payload并发送
        # 实现重试逻辑...
```

### 6.2 异常类型

```python
class WeChatAPIError(Exception):
    """企业微信API错误"""
    def __init__(self, message, errcode=None):
        super().__init__(message)
        self.errcode = errcode

class NetworkError(Exception):
    """网络错误（可重试）"""
    pass

class ConfigError(Exception):
    """配置错误"""
    pass
```

---

## 7. Integration with Phase 1

### 7.1 输入接口

```python
# 来自Phase 1的输出
markdown_table = markdown_formatter.format(excel_data)

# 发送到企业微信
client = WeChatWorkClient()
results = client.send_markdown(markdown_table)

# 检查结果
all_success = all(r['success'] for r in results)
sent_count = sum(1 for r in results if r['success'])
```

### 7.2 状态反馈

```python
def format_send_status(results):
    """格式化发送状态为中文提示"""
    total = len(results)
    success = sum(1 for r in results if r['success'])
    failed = total - success
    
    if failed == 0:
        return f"✓ 发送成功（共{total}片）"
    else:
        return f"✗ 发送失败：成功{success}片，失败{failed}片"
```

---

## 8. Testing Strategy

### 8.1 单元测试

- 配置存储：测试读写、路径处理
- 消息切片：测试边界情况、表头重复
- 重试逻辑：测试指数退避计算
- 错误处理：测试异常分类

### 8.2 集成测试（需真实webhook）

- 完整发送流程
- 大消息切片发送
- 错误场景模拟

---

## 9. Security Considerations

### 9.1 Webhook Protection

- webhook URL包含敏感key
- 绝不提交到版本控制
- .gitignore必须包含config/

### 9.2 日志处理

- 日志中不得包含完整webhook URL
- 可以记录部分脱敏：`

---

## RESEARCH COMPLETE

This research covers:
- ✓ Enterprise WeChat webhook API details
- ✓ Message limits and slicing strategy
- ✓ Rate limiting (20 msg/sec)
- ✓ Retry mechanism with exponential backoff
- ✓ Configuration storage patterns
- ✓ Client class architecture
- ✓ Integration with Phase 1 formatter output
- ✓ Testing and security considerations

**Ready for planning.**

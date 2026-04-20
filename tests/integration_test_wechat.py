#!/usr/bin/env python3
"""企业微信集成测试脚本

用于手动测试企业微信推送功能。需要设置 WEBHOOK_URL 环境变量。

使用方法:
    export WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key"
    python tests/integration_test_wechat.py

或者:
    WEBHOOK_URL="your_url" python tests/integration_test_wechat.py
"""

import os
import sys
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.wechat_client import WeChatWorkClient
from src.core.config import ConfigStore, ConfigError
from src.core.exceptions import WeChatAPIError, NetworkError


def check_webhook_url():
    """检查webhook URL是否已设置"""
    webhook_url = os.environ.get('WEBHOOK_URL')
    
    if not webhook_url:
        print("=" * 60)
        print("错误：未设置 WEBHOOK_URL 环境变量")
        print("=" * 60)
        print()
        print("请先设置webhook URL：")
        print('  export WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key"')
        print()
        print("或者运行时使用：")
        print('  WEBHOOK_URL="your_url" python tests/integration_test_wechat.py')
        print()
        print("注意：消息将发送到真实的企业微信群组！")
        print("=" * 60)
        return None
    
    return webhook_url


def test_single_chunk(webhook_url):
    """测试单一片消息"""
    print("\n" + "=" * 60)
    print("测试 1: 单一片消息")
    print("=" * 60)
    
    client = WeChatWorkClient(webhook_url=webhook_url)
    
    markdown = """| 日期 | 发货人 | 提单号 | 入库未扫 | 出库未扫 |
|:---:|:---:|:---:|:---:|:---:|
| 2024-01-15 | 张三 | BL001 | 5 | 3 |
| 2024-01-16 | 李四 | BL002 | - | 2 |"""
    
    print(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"消息大小: {len(markdown)} 字符")
    print(f"切片数: 1")
    
    start_time = time.time()
    results = client.send_markdown(markdown)
    elapsed = time.time() - start_time
    
    print(f"\n结果:")
    for r in results:
        status = "✓ 成功" if r['success'] else f"✗ 失败: {r.get('error', '未知错误')}"
        print(f"  第 {r['chunk_num']}/{r['total']} 片: {status}")
    
    print(f"\n耗时: {elapsed:.2f} 秒")
    
    return all(r['success'] for r in results)


def test_multiple_chunks(webhook_url):
    """测试多片消息"""
    print("\n" + "=" * 60)
    print("测试 2: 多片消息（超过15行数据）")
    print("=" * 60)
    
    client = WeChatWorkClient(webhook_url=webhook_url)
    
    # 创建超过15行的数据
    rows = ["| 日期 | 发货人 | 提单号 | 入库未扫 | 出库未扫 |", "|:---:|:---:|:---:|:---:|:---:|"]
    for i in range(20):
        rows.append(f"| 2024-01-{i+1:02d} | 用户{i+1:02d} | BL{i+1:03d} | {i+1} | {20-i} |")
    
    markdown = "\n".join(rows)
    
    print(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"消息大小: {len(markdown)} 字符")
    print(f"数据行数: 20")
    print(f"预计切片数: 2")
    
    start_time = time.time()
    results = client.send_markdown(markdown)
    elapsed = time.time() - start_time
    
    print(f"\n结果:")
    for r in results:
        status = "✓ 成功" if r['success'] else f"✗ 失败: {r.get('error', '未知错误')}"
        attempts = f" (尝试 {r.get('attempts', 1)} 次)" if 'attempts' in r else ""
        print(f"  第 {r['chunk_num']}/{r['total']} 片: {status}{attempts}")
    
    print(f"\n耗时: {elapsed:.2f} 秒")
    print(f"实际切片数: {len(results)}")
    
    return all(r['success'] for r in results)


def test_with_config_store(webhook_url):
    """测试使用ConfigStore"""
    print("\n" + "=" * 60)
    print("测试 3: 通过ConfigStore加载配置")
    print("=" * 60)
    
    # 临时保存webhook到配置
    config_store = ConfigStore()
    original_url = config_store.get_webhook_url()
    config_store.set_webhook_url(webhook_url)
    
    try:
        # 创建客户端（从配置加载）
        client = WeChatWorkClient()
        
        print(f"从配置加载webhook URL: {'是' if client.webhook_url else '否'}")
        print(f"URL匹配: {'是' if client.webhook_url == webhook_url else '否'}")
        
        markdown = "| 测试 | 状态 |\n|---|---|\n| 配置加载 | ✓ 正常 |"
        results = client.send_markdown(markdown)
        
        success = all(r['success'] for r in results)
        print(f"发送结果: {'✓ 成功' if success else '✗ 失败'}")
        
        return success
        
    finally:
        # 恢复原始配置
        if original_url:
            config_store.set_webhook_url(original_url)
        else:
            # 删除webhook_url配置项
            config = config_store.load()
            if 'webhook_url' in config:
                del config['webhook_url']
                config_store.save(config)


def main():
    """主函数"""
    print("=" * 60)
    print("企业微信推送功能集成测试")
    print("=" * 60)
    print()
    print("⚠️  警告: 此测试将向真实的企业微信群组发送消息！")
    print("请确认您已经准备好接收测试消息。")
    print()
    
    webhook_url = check_webhook_url()
    if not webhook_url:
        sys.exit(1)
    
    print("按 Enter 键继续，或 Ctrl+C 取消...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(0)
    
    # 运行测试
    results = []
    
    try:
        results.append(("单一片消息", test_single_chunk(webhook_url)))
        results.append(("多片消息", test_multiple_chunks(webhook_url)))
        results.append(("配置加载", test_with_config_store(webhook_url)))
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())

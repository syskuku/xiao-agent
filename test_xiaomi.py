#!/usr/bin/env python3
"""
测试小米账号对话记录获取
"""

import asyncio
import json
import time
from aiohttp import ClientSession

LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"

async def test_conversation():
    """测试小米对话记录获取"""
    
    # 这里需要小米的cookie
    # 如果没有cookie，需要用小米账号登录获取
    
    print("=" * 50)
    print("小米对话记录测试")
    print("=" * 50)
    print()
    print("注意：小米API需要cookie认证")
    print("请提供小米cookie，格式如下：")
    print("userId=xxx; serviceToken=xxx")
    print()
    print("获取方法：")
    print("1. 登录 https://account.xiaomi.com")
    print("2. 打开浏览器开发者工具 (F12)")
    print("3. 切换到 Network 标签页")
    print("4. 刷新页面")
    print("5. 复制Cookie")
    print()
    
    cookie = input("请输入小米Cookie（直接回车跳过）：").strip()
    
    if not cookie:
        print("跳过测试")
        return
    
    # 测试API
    hardware = "L06A"
    url = LATEST_ASK_API.format(
        hardware=hardware,
        timestamp=str(int(time.time() * 1000))
    )
    
    headers = {
        "Cookie": cookie
    }
    
    try:
        async with ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"API响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if data.get("data"):
                        records = json.loads(data["data"]).get("records")
                        if records:
                            print(f"\n成功获取到 {len(records)} 条对话记录！")
                            for record in records[:3]:
                                print(f"- {record.get('query', '无内容')}")
                        else:
                            print("未获取到对话记录")
                    else:
                        print("API返回为空")
                else:
                    print(f"请求失败，状态码: {response.status}")
                    
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_conversation())
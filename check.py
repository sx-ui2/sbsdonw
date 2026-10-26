import os
import requests
import time

base_url = os.environ.get("BASE_URL")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.sbs.co.kr/"
}

if not base_url:
    print("❌ 错误：没有提供 BASE_URL")
    exit(1)

print(f"开始测试基础链接: {base_url}")

for last3 in range(1000):
    ts = f"{last3:03d}"
    # 这里只会替换 {last3}，你手动指定的倒数第4位会原封不动保留
    url = base_url.replace("{last3}", ts) 
    
    try:
        r = requests.head(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code != 404:
            print(f"\n✅ 找到非404链接！")
            print(f"最后3位: {ts}  状态码: {r.status_code}")
            print(f"完整URL: {url}")
            exit(0)
        else:
            print(f"[404] {ts}")
    except Exception as e:
        print(f"[ERR] {ts}: {e}")
    time.sleep(0.2)

print("\n遍历完毕，全是404。")

import os
import requests
import time

# 从 GitHub Actions 读取基础 URL，并做一点处理
base_url = os.environ.get("BASE_URL")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.sbs.co.kr/"
}

if not base_url:
    print("❌ 错误：没有提供 BASE_URL")
    exit(1)

print(f"开始测试基础链接: {base_url}")

# 第4位的遍历范围：以你传入的链接为基础，如果你想要前后1-2，就遍历 0,1,2,3,4
# 如果你传入的链接里已经有确切的第4位，你想只测固定的，就把下面这行改成 range(1)
p4_list = [1, 2]  

for p4 in p4_list:
    for last3 in range(1000):
        ts = f"{last3:03d}"
        # 注意这里我们把 {p4} 和 {last3} 都替换掉
        url = base_url.replace("{p4}", str(p4)).replace("{last3}", ts)
        
        try:
            r = requests.head(url, headers=headers, timeout=8, allow_redirects=True)
            if r.status_code != 404:
                print(f"\n✅ 找到非404链接！")
                print(f"状态码: {r.status_code}")
                print(f"完整URL: {url}")
                exit(0)  # 找到就立刻停止
            else:
                print(f"[404] p4={p4}, last3={ts}")
        except Exception as e:
            print(f"[ERR] p4={p4}, last3={ts}: {e}")
        
        time.sleep(0.2) # 稍微等一下，防止被限流封 IP

print("\n遍历完毕，全是404。")

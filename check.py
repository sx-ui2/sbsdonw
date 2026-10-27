import os
import requests
import time
import re

# 读取输入
raw_url = os.environ.get("RAW_URL")
specified_tail = os.environ.get("SPECIFIED_TAIL", "1") 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.sbs.co.kr/",
}

if not raw_url:
    print("❌ 错误：没有提供 RAW_URL")
    exit(1)

if not specified_tail.isdigit():
    print("❌ 错误：指定的尾部数字必须是纯数字（例如 1, 10, 25）")
    exit(1)

print(f"原始链接: {raw_url}")
print(f"手动指定的倒数第4位(及之前)的数字: {specified_tail}")

# ================= 1. 提取核心时间戳 =================
match = re.search(r'(\d{4}-\d{2}-\d{2}-)(\d{9})', raw_url)
if not match:
    print("❌ 错误：无法从链接中提取 9 位时间戳 (例如 013117572)")
    exit(1)

time_str = match.group(2)  # 提取出 9 位时间戳
print(f"提取到原始时间戳: {time_str}")

# ================= 2. 重组基础 URL =================
if ".mp4" in raw_url:
    base_url = raw_url.split('.mp4')[0] + '.mp4'
else:
    print("⚠️ 警告：链接中未找到 .mp4，尝试强制匹配")
    base_url = raw_url.split(time_str)[0] + time_str + '.mp4'

# 处理分辨率替换
base_url = base_url.replace('640X360_96000', '1920X1080_256000')
base_url = base_url.replace('640X360_96', '1920X1080_256')
base_url = base_url.replace('640_360_96', '1920_1080_256')

# 强制拼接 content_0.ts
base_url = base_url + '/content_0.ts'

# ================= 3. 计算新的时间戳前缀 =================
# 我们截取时间戳的前部分，长度 = 9 - 3(遍历位) - 指定数字的长度
# 例如 specified_tail = "10" (长度2)，则保留 9-3-2 = 4位。剩下的用 specified_tail 补上
tail_len = len(specified_tail)
prefix_len = 9 - 3 - tail_len

if prefix_len < 0:
    print("❌ 错误：指定的数字太长，超过剩余位数")
    exit(1)

time_prefix = time_str[:prefix_len]
print(f"原时间戳前缀: {time_prefix}，拼接指定尾数: {specified_tail}")

# 组合成新的前缀
new_time_prefix = time_prefix + specified_tail

# 将 base_url 中的旧时间戳替换为新前缀 + 占位符
base_url_template = base_url.replace(time_str, new_time_prefix + "{last3}")

print(f"生成的遍历链接模板: {base_url_template}\n")

# ================= 4. 开始遍历 =================
success = False
for last3 in range(1000):
    ts_suffix = f"{last3:03d}"
    url = base_url_template.replace("{last3}", ts_suffix)
    
    try:
        r = requests.head(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code != 404:
            print(f"\n✅ 找到非404链接！")
            print(f"状态码: {r.status_code}")
            print(f"完整URL: {url}")
            success = True
            exit(0) 
        else:
            if last3 % 100 == 0:
                print(f"已测试 {last3} 个... 当前尝试: {ts_suffix}")
    except Exception as e:
        print(f"[ERR] {ts_suffix}: {e}")
    
    time.sleep(0.1)

if not success:
    print("\n遍历完毕，全是 404。")

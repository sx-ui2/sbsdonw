import os
import requests
import time
import re

# 读取输入
raw_url = os.environ.get("RAW_URL")
specified_digit = os.environ.get("SPECIFIED_DIGIT", "5") 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.sbs.co.kr/",
}

if not raw_url:
    print("❌ 错误：没有提供 RAW_URL")
    exit(1)

print(f"原始链接: {raw_url}")
print(f"指定的保留位数 (倒数第): {specified_digit}")

# ================= 1. 提取核心时间戳 =================
match = re.search(r'(\d{4}-\d{2}-\d{2}-)(\d{9})', raw_url)
if not match:
    print("❌ 错误：无法从链接中提取 9 位时间戳 (例如 013117572)")
    exit(1)

time_str = match.group(2)  # 提取出 9 位时间戳
print(f"提取到时间戳: {time_str}")

# ================= 2. 重组基础 URL =================
# 核心逻辑：截断到 .mp4，去掉后面的 playlist.m3u8 和 token，强制补上 /content_0.ts
if ".mp4" in raw_url:
    # 截取从开头到 ".mp4"（包含）的部分
    base_url = raw_url.split('.mp4')[0] + '.mp4'
else:
    # 如果连 .mp4 都没有（按理说不会），尝试用正则截取到时间戳
    print("⚠️ 警告：链接中未找到 .mp4，尝试强制匹配")
    base_url = raw_url.split(time_str)[0] + time_str + '.mp4'

# 处理分辨率替换 (640X360_96000 -> 1920X1080_256000 等)
base_url = base_url.replace('640X360_96000', '1920X1080_256000')
base_url = base_url.replace('640X360_96', '1920X1080_256')
base_url = base_url.replace('640_360_96', '1920_1080_256')

# 强制拼接 content_0.ts
base_url_template = base_url + '/content_0.ts'

# ================= 3. 准备遍历 =================
# 提取固定的前缀（去掉最后3位）
fixed_prefix = time_str[:-3]
print(f"固定的时间戳前缀: {fixed_prefix}，将遍历后三位 000-999")

# 把 base_url_template 里的完整时间戳换成带占位符的形式
base_url_template = base_url_template.replace(time_str, fixed_prefix + "{last3}")

print(f"生成的遍历链接模板: {base_url_template}\n")

# ================= 4. 开始遍历 =================
success = False
for last3 in range(1000):
    ts_suffix = f"{last3:03d}"
    url = base_url_template.replace("{last3}", ts_suffix)
    
    try:
        # 使用 HEAD 请求，只拿状态码，不下载实际内容
        r = requests.head(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code != 404:
            print(f"\n✅ 找到非404链接！")
            print(f"状态码: {r.status_code}")
            print(f"完整URL: {url}")
            success = True
            exit(0) # 找到就停
        else:
            if last3 % 100 == 0:
                print(f"已测试 {last3} 个... 当前尝试: {ts_suffix}")
    except Exception as e:
        print(f"[ERR] {ts_suffix}: {e}")
    
    time.sleep(0.1)

if not success:
    print("\n遍历完毕，全是 404。")

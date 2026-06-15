"""下载几张公有领域风格图到 素材/风格图/（用于风格迁移测试/演示）。

均为公有领域画作（作者逝世逾百年，可自由使用）：
  梵高《星空》、葛饰北斋《神奈川冲浪里》。
用法：E:\\miniconda3\\envs\\ai-service\\python.exe 代码\\utils\\fetch_styles.py
"""
import os
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_DIR = os.path.join(os.path.dirname(os.path.dirname(HERE)), "素材", "风格图")

STYLES = {
    "starry_night.jpg":
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        "Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg?width=1024",
    "great_wave.jpg":
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        "The_Great_Wave_off_Kanagawa.jpg?width=1024",
}


def main():
    os.makedirs(STYLE_DIR, exist_ok=True)
    for name, url in STYLES.items():
        dst = os.path.join(STYLE_DIR, name)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            print("已存在", name)
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=90).read()
            with open(dst, "wb") as f:
                f.write(data)
            print("OK", name, f"{len(data) // 1024} KB")
        except Exception as e:
            print("FAIL", name, e)


if __name__ == "__main__":
    main()

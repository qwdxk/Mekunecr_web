#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime
from pathlib import Path

def main():
    print("开始处理登录申请...")
    
    # 创建必要的目录
    Path("pending_applications").mkdir(exist_ok=True)
    Path("processed_applications").mkdir(exist_ok=True)
    
    # 初始化状态文件
    init_status_file()
    
    print("处理完成")

def init_status_file():
    """初始化状态文件"""
    status_file = Path("login_status.json")
    if not status_file.exists():
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print("已创建状态文件")

if __name__ == "__main__":
    main()

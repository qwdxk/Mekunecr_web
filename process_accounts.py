#!/usr/bin/env python3
import re
import os
from datetime import datetime

def process_accounts():
    with open('account.mue', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    pattern = r'<account>:name<"([^"]+)">:id<([0-9]+)>:password<"([^"]+)">'
    
    print(f"找到 {len(lines)} 个账号申请")
    
    # 这里可以添加额外的处理逻辑
    # 比如：验证账号格式、去重等
    
    # 记录处理日志
    with open('processing_log.txt', 'w', encoding='utf-8') as log:
        log.write(f"处理时间: {datetime.now()}\n")
        log.write(f"找到 {len(lines)} 个申请\n")
        
        for line in lines:
            if line.strip():
                match = re.match(pattern, line)
                if match:
                    name, id, password = match.groups()
                    log.write(f"有效申请: {name} (ID: {id})\n")
                else:
                    log.write(f"无效格式: {line}\n")

if __name__ == "__main__":
    process_accounts()
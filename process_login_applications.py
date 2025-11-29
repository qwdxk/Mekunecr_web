#!/usr/bin/env python3
"""
处理登录申请的Python脚本
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

def main():
    print("=== 开始处理登录申请 ===")
    
    # 确保必要的目录存在
    Path("pending_applications").mkdir(exist_ok=True)
    Path("processed_applications").mkdir(exist_ok=True)
    Path("application_logs").mkdir(exist_ok=True)
    
    # 初始化状态文件
    init_status_file()
    
    # 处理申请
    if os.getenv('GITHUB_EVENT_NAME') == 'issues':
        process_issue_application()
    else:
        process_manual_trigger()
    
    print("=== 处理完成 ===")

def init_status_file():
    """初始化申请状态文件"""
    status_file = Path("login_status.json")
    if not status_file.exists():
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print("已创建状态文件: login_status.json")

def process_issue_application():
    """处理通过Issue提交的申请"""
    print("处理Issue提交的申请...")
    
    # 从环境变量获取Issue信息
    issue_title = os.getenv('ISSUE_TITLE', '')
    issue_body = os.getenv('ISSUE_BODY', '')
    issue_number = os.getenv('ISSUE_NUMBER', '')
    
    print(f"Issue标题: {issue_title}")
    print(f"Issue编号: {issue_number}")
    
    # 解析申请ID
    application_id = extract_application_id(issue_title)
    if not application_id:
        print("无法从Issue标题中提取申请ID")
        return
    
    print(f"申请ID: {application_id}")
    
    # 提取加密数据
    encrypted_data = extract_encrypted_data(issue_body)
    if not encrypted_data:
        print("无法从Issue内容中提取加密数据")
        return
    
    # 创建申请记录
    application_data = {
        "application_id": application_id,
        "issue_number": issue_number,
        "encrypted_data": encrypted_data,
        "received_at": datetime.now().isoformat(),
        "status": "pending",
        "type": "login_application"
    }
    
    # 保存申请文件
    save_application(application_data)
    
    # 更新状态索引
    update_status_index(application_id, "pending", "等待处理")
    
    print(f"申请已保存: {application_id}")

def extract_application_id(issue_title):
    """从Issue标题中提取申请ID"""
    # 标题格式: "登录申请:app_1700000000_1234"
    match = re.search(r'登录申请:([a-zA-Z0-9_]+)', issue_title)
    if match:
        return match.group(1)
    return None

def extract_encrypted_data(issue_body):
    """从Issue内容中提取加密数据"""
    # 查找加密数据行
    lines = issue_body.split('\n')
    for line in lines:
        if '加密数据:' in line:
            parts = line.split('加密数据:')
            if len(parts) > 1:
                return parts[1].strip()
    return None

def save_application(application_data):
    """保存申请到文件"""
    app_id = application_data["application_id"]
    filename = f"pending_applications/{app_id}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(application_data, f, ensure_ascii=False, indent=2)
    
    print(f"申请文件已保存: {filename}")

def update_status_index(application_id, status, message):
    """更新申请状态索引"""
    status_file = Path("login_status.json")
    
    # 读取现有状态
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
    else:
        status_data = {}
    
    # 更新状态
    status_data[application_id] = {
        "status": status,
        "message": message,
        "last_updated": datetime.now().isoformat(),
        "issue_number": os.getenv('ISSUE_NUMBER', '')
    }
    
    # 保存状态文件
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)
    
    print(f"状态索引已更新: {application_id} -> {status}")

def process_manual_trigger():
    """处理手动触发的工作流"""
    print("手动触发工作流处理...")
    
    # 检查待处理申请
    pending_dir = Path("pending_applications")
    if pending_dir.exists():
        pending_files = list(pending_dir.glob("*.json"))
        print(f"找到 {len(pending_files)} 个待处理申请")
        
        for app_file in pending_files:
            process_single_application(app_file)

def process_single_application(app_file):
    """处理单个申请文件"""
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            app_data = json.load(f)
        
        app_id = app_data.get("application_id")
        print(f"处理申请: {app_id}")
        
        # 这里可以添加自动验证逻辑
        # 目前只是标记为已接收
        update_status_index(app_id, "received", "申请已接收，等待处理")
        
    except Exception as e:
        print(f"处理申请文件错误 {app_file}: {e}")

if __name__ == "__main__":
    main()

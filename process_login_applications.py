#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime
from pathlib import Path

def main():
    print("开始处理登录申请...")
    
    # 确保必要的目录存在
    Path("pending_applications").mkdir(exist_ok=True)
    Path("processed_applications").mkdir(exist_ok=True)
    
    # 处理所有待处理的申请文件
    处理所有申请()
    
    print("处理完成")

def 处理所有申请():
    applications_dir = Path("pending_applications")
    
    if not applications_dir.exists():
        print("申请目录不存在")
        return
    
    # 获取所有申请文件
    application_files = list(applications_dir.glob("*.json"))
    
    if not application_files:
        print("没有找到申请文件")
        return
    
    print(f"找到 {len(application_files)} 个申请文件")
    
    # 加载账号数据
    account_data = 加载账号数据()
    
    # 加载状态文件
    status_data = 加载状态数据()
    
    for app_file in application_files:
        print(f"处理申请文件: {app_file.name}")
        处理单个申请(app_file, account_data, status_data)
    
    # 保存更新后的状态
    保存状态数据(status_data)

def 加载账号数据():
    """从account.mue文件加载账号数据"""
    account_file = Path("account.mue")
    accounts = []
    
    if account_file.exists():
        with open(account_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析account.mue格式: <account>:name<"用户名">:id<000000001>:password<"密码">
        pattern = r'<account>:name<"([^"]+)">:id<([0-9]+)>:password<"([^"]+)">'
        
        for match in re.finditer(pattern, content):
            name, account_id, password = match.groups()
            accounts.append({
                "name": name,
                "id": account_id,
                "password": password
            })
    
    print(f"加载了 {len(accounts)} 个账号")
    return accounts

def 加载状态数据():
    """加载或创建状态文件"""
    status_file = Path("login_status.json")
    
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def 处理单个申请(app_file, account_data, status_data):
    """处理单个申请文件"""
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            application = json.load(f)
        
        client_id = application.get("client_id", "")
        username = application.get("username", "")
        
        if not client_id or not username:
            print(f"无效的申请文件: {app_file.name}")
            return
        
        print(f"处理申请: {username} (ID: {client_id})")
        
        # 检查账号是否存在
        account_exists = any(acc["name"] == username for acc in account_data)
        
        if account_exists:
            # 账号存在，积压申请
            积压申请(application, status_data, client_id)
            print(f"✓ 账号 {username} 存在，申请已积压")
        else:
            # 账号不存在，拒绝申请
            拒绝申请(application, status_data, client_id, "账号不存在")
            print(f"✗ 账号 {username} 不存在，申请被拒绝")
        
        # 移动文件到已处理目录
        移动文件(app_file, client_id)
        
    except Exception as e:
        print(f"处理申请文件时出错 {app_file.name}: {e}")

def 积压申请(application, status_data, client_id):
    """积压有效申请"""
    status_data[client_id] = {
        "username": application["username"],
        "status": "pending",
        "submitted_at": application["timestamp"],
        "last_updated": datetime.now().isoformat()
    }

def 拒绝申请(application, status_data, client_id, reason):
    """拒绝无效申请"""
    status_data[client_id] = {
        "username": application["username"],
        "status": "rejected",
        "reason": reason,
        "submitted_at": application["timestamp"],
        "last_updated": datetime.now().isoformat()
    }

def 移动文件(app_file, client_id):
    """移动处理完成的文件"""
    processed_dir = Path("processed_applications")
    processed_file = processed_dir / f"{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    app_file.rename(processed_file)

def 保存状态数据(status_data):
    """保存状态数据到文件"""
    with open("login_status.json", 'w', encoding='utf-8') as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)
    
    print(f"状态文件已更新，共 {len(status_data)} 个申请记录")

if __name__ == "__main__":
    main()

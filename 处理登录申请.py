#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理登录申请的单一脚本
所有功能都集中在这个文件中
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

def 主函数():
    """主函数 - 根据触发类型执行不同操作"""
    print("=== 开始处理登录申请 ===")
    
    # 创建必要目录
    Path("待处理申请").mkdir(exist_ok=True)
    Path("已处理申请").mkdir(exist_ok=True)
    
    # 初始化状态文件
    初始化状态文件()
    
    # 根据触发类型执行不同操作
    触发类型 = os.getenv('GITHUB_EVENT_NAME', '手动触发')
    
    if 触发类型 == 'issues':
        print("检测到Issue触发")
        处理新申请()
    else:
        print("手动触发")
        处理待处理申请()
        # 清理过期申请()
    
    print("=== 处理完成 ===")

def 初始化状态文件():
    """初始化申请状态文件"""
    状态文件 = Path("登录状态.json")
    if not 状态文件.exists():
        with open(状态文件, 'w', encoding='utf-8') as 文件:
            json.dump({}, 文件, ensure_ascii=False, indent=2)
        print("已创建状态文件")

def 处理新申请():
    """处理通过Issue提交的新申请"""
    print("处理新申请...")
    
    # 从环境变量获取Issue信息
    标题 = os.getenv('GITHUB_EVENT_ISSUE_TITLE', '')
    内容 = os.getenv('GITHUB_EVENT_ISSUE_BODY', '')
    Issue编号 = os.getenv('GITHUB_EVENT_ISSUE_NUMBER', '')
    
    if not 标题 or "登录申请:" not in 标题:
        print("不是登录申请，跳过")
        return
    
    print(f"处理Issue: {标题}")
    
    # 提取申请ID
    申请ID = 提取申请ID(标题)
    if not 申请ID:
        print("无法提取申请ID")
        return
    
    # 提取加密数据
    加密数据 = 提取加密数据(内容)
    if not 加密数据:
        print("无法提取加密数据")
        return
    
    # 创建申请记录
    申请数据 = {
        "申请ID": 申请ID,
        "Issue编号": Issue编号,
        "加密数据": 加密数据,
        "提交时间": datetime.now().isoformat(),
        "状态": "待处理"
    }
    
    # 保存申请
    保存申请(申请数据)
    
    # 更新状态
    更新状态(申请ID, "待处理", "新申请已接收")
    
    print(f"申请已保存: {申请ID}")

def 处理待处理申请():
    """处理所有待处理的申请"""
    print("处理待处理申请...")
    
    待处理目录 = Path("待处理申请")
    if not 待处理目录.exists():
        print("没有待处理申请")
        return
    
    申请文件列表 = list(待处理目录.glob("*.json"))
    print(f"找到 {len(申请文件列表)} 个待处理申请")
    
    for 申请文件 in 申请文件列表:
        try:
            with open(申请文件, 'r', encoding='utf-8') as 文件:
                申请数据 = json.load(文件)
            
            申请ID = 申请数据.get("申请ID")
            print(f"处理申请: {申请ID}")
            
            # 这里可以添加自动处理逻辑
            # 目前只是标记为已处理
            
            # 移动文件到已处理目录
            新路径 = Path("已处理申请") / 申请文件.name
            申请文件.rename(新路径)
            
            更新状态(申请ID, "已处理", "申请已处理")
            
        except Exception as 错误:
            print(f"处理申请文件错误 {申请文件}: {错误}")

def 清理过期申请():
    """清理过期申请（7天前）"""
    print("清理过期申请...")
    
    截止时间 = datetime.now() - timedelta(days=7)
    
    # 清理待处理申请
    待处理目录 = Path("待处理申请")
    if 待处理目录.exists():
        过期数量 = 0
        for 申请文件 in 待处理目录.glob("*.json"):
            文件时间 = datetime.fromtimestamp(申请文件.stat().st_mtime)
            if 文件时间 < 截止时间:
                申请文件.unlink()
                过期数量 += 1
                print(f"删除过期申请: {申请文件.name}")
        
        print(f"删除了 {过期数量} 个过期申请")
    
    # 清理状态文件中的过期条目
    状态文件 = Path("登录状态.json")
    if 状态文件.exists():
        with open(状态文件, 'r', encoding='utf-8') as 文件:
            状态数据 = json.load(文件)
        
        过期申请列表 = []
        for 申请ID, 状态信息 in 状态数据.items():
            更新时间 = datetime.fromisoformat(状态信息.get("最后更新", "2020-01-01"))
            if 更新时间 < 截止时间 and 状态信息.get("状态") == "待处理":
                过期申请列表.append(申请ID)
        
        for 申请ID in 过期申请列表:
            状态数据[申请ID] = {
                "状态": "已过期",
                "最后更新": datetime.now().isoformat()
            }
            print(f"标记过期申请: {申请ID}")
        
        with open(状态文件, 'w', encoding='utf-8') as 文件:
            json.dump(状态数据, 文件, ensure_ascii=False, indent=2)
        
        print(f"标记了 {len(过期申请列表)} 个过期申请")

def 提取申请ID(标题):
    """从Issue标题提取申请ID"""
    匹配 = re.search(r'登录申请:([a-zA-Z0-9_]+)', 标题)
    return 匹配.group(1) if 匹配 else None

def 提取加密数据(内容):
    """从Issue内容提取加密数据"""
    行列表 = 内容.split('\n')
    for 行 in 行列表:
        if '加密数据:' in 行:
            部分 = 行.split('加密数据:')
            if len(部分) > 1:
                return 部分[1].strip()
    return None

def 保存申请(申请数据):
    """保存申请到文件"""
    申请ID = 申请数据["申请ID"]
    文件名 = f"待处理申请/{申请ID}.json"
    
    with open(文件名, 'w', encoding='utf-8') as 文件:
        json.dump(申请数据, 文件, ensure_ascii=False, indent=2)
    
    print(f"申请已保存: {文件名}")

def 更新状态(申请ID, 状态, 消息):
    """更新申请状态"""
    状态文件 = Path("登录状态.json")
    
    # 读取现有状态
    if 状态文件.exists():
        with open(状态文件, 'r', encoding='utf-8') as 文件:
            状态数据 = json.load(文件)
    else:
        状态数据 = {}
    
    # 更新状态
    状态数据[申请ID] = {
        "状态": 状态,
        "消息": 消息,
        "最后更新": datetime.now().isoformat()
    }
    
    # 保存状态文件
    with open(状态文件, 'w', encoding='utf-8') as 文件:
        json.dump(状态数据, 文件, ensure_ascii=False, indent=2)
    
    print(f"状态已更新: {申请ID} -> {状态}")

if __name__ == "__main__":
    主函数()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import qrcode
import os
import json
from pathlib import Path

# ================== 配置 ==================
BAIDU_AK = "YOUR_BAIDU_AK"          # 你的百度地图 API Key，如果不使用请留空
QR_FILENAME = "ip_qrcode.png"        # 生成的二维码图片文件名
INFO_FILENAME = "latest_ip.json"     # 保存最新IP信息的JSON文件（可选）
# ==========================================

def get_public_ip():
    """获取当前公网IP"""
    apis = [
        'https://api.ipify.org?format=json',
        'https://api.my-ip.io/ip.json',
        'https://ipapi.co/json/'
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=5)
            if r.status_code == 200:
                data = r.json()
                ip = data.get('ip') or data.get('ip_address')
                if ip:
                    return ip
        except:
            continue
    raise Exception("无法获取公网IP")

def query_baidu(ip):
    """使用百度地图API查询归属地"""
    if not BAIDU_AK or BAIDU_AK == "YOUR_BAIDU_AK":
        return None
    try:
        url = f"https://api.map.baidu.com/location/ip?ak={BAIDU_AK}&ip={ip}&coor=bd09ll"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get('status') == 0:
            addr = data['content']['address_detail']
            province = addr.get('province', '')
            city = addr.get('city', '')
            return f"{province} {city}".strip()
        else:
            print("百度API返回错误:", data.get('message'))
            return None
    except Exception as e:
        print("百度API请求异常:", e)
        return None

def query_ipapi(ip):
    """使用ipapi.co查询归属地（备用）"""
    try:
        url = f"https://ipapi.co/{ip}/json/?lang=zh-cn"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get('error'):
            return None
        province = data.get('region', '')
        city = data.get('city', '')
        return f"{province} {city}".strip()
    except:
        return None

def get_location(ip):
    """综合查询归属地，优先百度"""
    loc = query_baidu(ip)
    if loc:
        return loc
    loc = query_ipapi(ip)
    if loc:
        return loc
    return "未知位置"

def generate_qr(text, filename):
    """生成二维码图片"""
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"二维码已生成: {filename}")

def main():
    # 1. 获取IP
    ip = get_public_ip()
    print(f"当前IP: {ip}")

    # 2. 获取归属地
    location = get_location(ip)
    print(f"归属地: {location}")

    # 3. 判断是否南京
    is_nanjing = "南京" in location
    status = "南京IP" if is_nanjing else "非南京IP"
    print(f"判断: {status}")

    # 4. 生成二维码内容（纯文本，微信扫描后显示）
    qr_text = f"IP: {ip}\n归属地: {location}\n{status}"
    generate_qr(qr_text, QR_FILENAME)

    # 5. 保存IP信息到JSON（可选，用于其他用途）
    with open(INFO_FILENAME, 'w', encoding='utf-8') as f:
        json.dump({
            "ip": ip,
            "location": location,
            "status": status,
            "timestamp": str(datetime.now())
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    from datetime import datetime
    main()

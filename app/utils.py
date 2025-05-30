import requests
import yaml
from typing import List, Dict
import re

def sort_server_name(name: str) -> tuple:
    """Sort server names by location priority and then alphabetically"""
    priority_map = {
        "新加坡": 0,
        "日本": 1,
        "香港": 2,
        "美国": 3
    }
    
    # Check for each location in the name
    for location, priority in priority_map.items():
        if location in name:
            return (priority, name)
    
    # If no priority location found, return with lowest priority
    return (999, name)

# 定义默认规则
DEFAULT_RULES = [
    "DOMAIN-SUFFIX,local,DIRECT",
    "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve",
    "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,172.16.0.0/12,DIRECT,no-resolve",
    "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,100.64.0.0/10,DIRECT,no-resolve",
    "IP-CIDR6,::1/128,DIRECT,no-resolve",
    "IP-CIDR6,fc00::/7,DIRECT,no-resolve",
    "IP-CIDR6,fe80::/10,DIRECT,no-resolve",
    "RULE-SET,applications,DIRECT",
    "DOMAIN,clash.razord.top,DIRECT",
    "DOMAIN,yacd.haishan.me,DIRECT", 
    "DOMAIN-KEYWORD,llsite,DIRECT",
    "DOMAIN-KEYWORD,wj2015,DIRECT", 
    "DOMAIN-KEYWORD,llsops,DIRECT",
    "DOMAIN-KEYWORD,liulishuo,DIRECT",
    "DOMAIN-KEYWORD,thellsapi,DIRECT",
    "RULE-SET,private,DIRECT",
    "RULE-SET,icloud,DIRECT",
    "RULE-SET,apple,DIRECT",
    "RULE-SET,proxy,🔰 节点选择",
    "RULE-SET,direct,DIRECT",
    "RULE-SET,lancidr,DIRECT",
    "RULE-SET,cncidr,DIRECT",
    "RULE-SET,telegramcidr,🔰 节点选择",
    "GEOIP,LAN,DIRECT",
    "GEOIP,CN,DIRECT",
    "MATCH,🔰 节点选择"
]

DEFAULT_RULE_PROVIDERS = {
    "reject": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt",
        "path": "./ruleset/reject.yaml",
        "interval": 86400
    },
    "icloud": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt",
        "path": "./ruleset/icloud.yaml",
        "interval": 86400
    },
    "apple": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt",
        "path": "./ruleset/apple.yaml",
        "interval": 86400
    },
    "google": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/google.txt",
        "path": "./ruleset/google.yaml",
        "interval": 86400
    },
    "proxy": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt",
        "path": "./ruleset/proxy.yaml",
        "interval": 86400
    },
    "direct": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt",
        "path": "./ruleset/direct.yaml",
        "interval": 86400
    },
    "private": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt",
        "path": "./ruleset/private.yaml",
        "interval": 86400
    },
    "gfw": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt",
        "path": "./ruleset/gfw.yaml",
        "interval": 86400
    },
    "tld-not-cn": {
        "type": "http",
        "behavior": "domain",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt",
        "path": "./ruleset/tld-not-cn.yaml",
        "interval": 86400
    },
    "telegramcidr": {
        "type": "http",
        "behavior": "ipcidr",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt",
        "path": "./ruleset/telegramcidr.yaml",
        "interval": 86400
    },
    "cncidr": {
        "type": "http",
        "behavior": "ipcidr",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt",
        "path": "./ruleset/cncidr.yaml",
        "interval": 86400
    },
    "lancidr": {
        "type": "http",
        "behavior": "ipcidr",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt",
        "path": "./ruleset/lancidr.yaml",
        "interval": 86400
    },
    "applications": {
        "type": "http",
        "behavior": "classical",
        "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt",
        "path": "./ruleset/applications.yaml",
        "interval": 86400
    }
}

def fetch_and_transform_config(url: str) -> dict:
    """获取并转换Clash配置"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"获取配置失败: {response.status_code}")
    
    # 加载原始配置
    config = yaml.safe_load(response.text)
    
    # 保留原始代理
    proxies = config.get("proxies", [])
    
    # 按名称排序代理
    proxies.sort(key=lambda x: sort_server_name(x["name"]))
    
    # 创建新的代理组
    proxy_groups = [{
        "name": "🔰 节点选择",
        "type": "select",
        "proxies": [proxy["name"] for proxy in proxies]
    }]
    
    # 添加直连代理组
    proxy_groups.append({
        "name": "🎯 不用代理",
        "type": "select",
        "proxies": ["DIRECT"]
    })
    
    # 从配置管理器获取规则配置
    from .config import config_manager
    rules_config = config_manager.load_rules_config()
    
    # 创建新配置
    new_config = {
        "port": config.get("port", 7890),
        "socks-port": config.get("socks-port", 7891),
        "allow-lan": True,
        "mode": config.get("mode", "rule"),
        "dns": config.get("dns"),
        "log-level": config.get("log-level", "info"),
        "external-controller": config.get("external-controller", "127.0.0.1:9090"),
        "proxies": proxies,
        "proxy-groups": proxy_groups,
        "rules": rules_config["rules"],
        "rule-providers": rules_config["rule_providers"]
    }
    
    return new_config 
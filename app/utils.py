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

def fetch_and_transform_config(url: str) -> dict:
    """Fetch and transform Clash configuration"""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch configuration: {response.status_code}")
    
    # Load original config
    config = yaml.safe_load(response.text)
    
    # Keep original proxies
    proxies = config.get("proxies", [])
    
    # Sort proxies by name
    proxies.sort(key=lambda x: sort_server_name(x["name"]))
    
    # Create new proxy group
    proxy_groups = [{
        "name": "节点选择",
        "type": "select",
        "proxies": [proxy["name"] for proxy in proxies]
    }]
    
    # Add direct proxy group
    proxy_groups.append({
        "name": "🎯 不用代理",
        "type": "select",
        "proxies": ["DIRECT"]
    })
    
    # Define fixed rules
    rules = [
        "DOMAIN-SUFFIX,local,🎯 不用代理",
        "IP-CIDR,192.168.0.0/16,🎯 不用代理,no-resolve",
        "IP-CIDR,10.0.0.0/8,🎯 不用代理,no-resolve",
        "IP-CIDR,172.16.0.0/12,🎯 不用代理,no-resolve",
        "IP-CIDR,127.0.0.0/8,🎯 不用代理,no-resolve",
        "IP-CIDR,100.64.0.0/10,🎯 不用代理,no-resolve",
        "IP-CIDR6,::1/128,🎯 不用代理,no-resolve",
        "IP-CIDR6,fc00::/7,🎯 不用代理,no-resolve",
        "IP-CIDR6,fe80::/10,🎯 不用代理,no-resolve"
    ]
    
    # Create new config
    new_config = {
        "port": config.get("port", 7890),
        "socks-port": config.get("socks-port", 7891),
        "allow-lan": config.get("allow-lan", False),
        "mode": config.get("mode", "rule"),
        "log-level": config.get("log-level", "info"),
        "external-controller": config.get("external-controller", "127.0.0.1:9090"),
        "proxies": proxies,
        "proxy-groups": proxy_groups,
        "rules": rules
    }
    
    return new_config 
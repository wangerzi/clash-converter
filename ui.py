import streamlit as st
import requests
import yaml
import json
from datetime import datetime, timedelta, timezone
from app.utils import fetch_and_transform_config, DEFAULT_RULES, DEFAULT_RULE_PROVIDERS
from app.config import config_manager

def main():
    st.set_page_config(page_title="Clash 配置转换服务", layout="wide")
    st.title("Clash 配置转换服务")
    
    # 创建选项卡
    tabs = st.tabs(["基本配置", "规则配置", "规则提供者配置", "访问令牌管理"])
    
    with tabs[0]:
        show_basic_config()
    with tabs[1]:
        show_rules_config()
    with tabs[2]:
        show_rule_providers_config()
    with tabs[3]:
        show_auth_tokens_config()

def show_basic_config():
    """显示基本配置界面"""
    st.header("基本配置")
    
    # Load current configuration
    config = config_manager.load_config()
    
    with st.form("config_form"):
        new_url = st.text_input("订阅地址", value=config["url"])
        new_interval = st.number_input("更新间隔（秒）", 
                                     min_value=60, 
                                     value=config["update_interval"],
                                     step=60)
        
        submitted = st.form_submit_button("保存配置")
        if submitted:
            config["url"] = new_url
            config["update_interval"] = new_interval
            config_manager.save_config(config)
            st.success("配置已保存")
    
    # Display current status
    st.header("当前状态")
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        if config["last_update"]:
            last_update = datetime.fromtimestamp(config["last_update"])
            st.info(f"最后更新时间: {last_update.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("尚未进行过更新")
    
    with status_col2:
        if st.button("立即更新"):
            st.info(f"开始更新: {config['url']}")
            try:
                transformed_config = fetch_and_transform_config(config["url"])
                config_manager.save_cached_proxy(transformed_config)
                config_manager.update_last_update_time()
                st.success("更新成功")
            except Exception as e:
                st.error(f"更新失败: {str(e)}")
    # 在基本配置界面中调用 show_cached_proxy 函数
    show_cached_proxy()

def show_auth_tokens_config():
    """显示访问令牌管理界面"""
    st.header("访问令牌管理")
    st.markdown("""
    访问令牌用于验证和授权访问服务的请求。每个令牌都是一个唯一字符串，用于验证请求的合法性。
    """)
    
    # Load current configuration
    config = config_manager.load_config()
    auth_tokens = config.get("auth_tokens", [])
    
    # 显示现有令牌
    for i, token in enumerate(auth_tokens):
        cols = st.columns([3, 1])
        cols[0].text(token)
        if cols[1].button("删除", key=f"delete_{i}"):
            auth_tokens.pop(i)
            config["auth_tokens"] = auth_tokens
            config_manager.save_config(config)
            st.rerun()
    
    # 添加新令牌
    new_token = st.text_input("添加新令牌")
    if st.button("添加令牌"):
        if new_token.strip():
            auth_tokens.append(new_token.strip())
            config["auth_tokens"] = auth_tokens
            config_manager.save_config(config)
            st.success("令牌已添加")
            st.rerun()
        else:
            st.warning("令牌不能为空")

def show_cached_proxy():
    """显示缓存的代理配置"""
    st.header("缓存的代理配置")
    
    # Load cached proxy configuration
    cached_proxy = config_manager.load_cached_proxy()
    
    if cached_proxy:
        # Display cached configuration in a text area
        st.text_area(
            "当前缓存的代理配置（YAML 格式）",
            value=yaml.dump(cached_proxy, allow_unicode=True),
            height=400,
            help="这是当前缓存的代理配置"
        )
    else:
        st.warning("当前没有缓存的代理配置")


def show_rules_config():
    """显示规则配置界面"""
    st.header("规则配置")
    st.markdown("""
    **规则配置说明**

    在此界面，您可以管理和编辑代理规则。每条规则应以以下格式输入：

    - **类型**: 规则的类型，例如 `DOMAIN-SUFFIX`, `DOMAIN-KEYWORD`, `IP-CIDR` 等。
    - **匹配内容**: 需要匹配的域名、关键词或 IP 范围。
    - **代理方式**: 指定使用的代理方式，例如 `DIRECT`, `REJECT`, 或者某个代理组的名称。
    - **可选参数**: `no-resolve`，用于指定不进行 DNS 解析。

    示例规则：
    ```
    DOMAIN-SUFFIX,example.com,DIRECT
    DOMAIN-KEYWORD,ads,REJECT
    IP-CIDR,192.168.1.0/24,🔰 节点选择,no-resolve
    ```

    请确保每行输入一条规则，并遵循上述格式。
    """)
    
    # 加载当前规则配置
    rules_config = config_manager.load_rules_config()
    current_rules = rules_config["rules"]
    
    # 创建一个文本区域用于编辑规则
    rules_text = st.text_area(
        "规则列表（每行一条规则）",
        value="\n".join(current_rules),
        height=400,
        help="每行输入一条规则。格式：类型,匹配内容,代理方式[,no-resolve]"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("恢复默认规则"):
            rules_text = "\n".join(DEFAULT_RULES)
            st.rerun()
    
    with col2:
        if st.button("保存规则"):
            try:
                # 将文本转换为规则列表
                new_rules = [rule.strip() for rule in rules_text.split("\n") if rule.strip()]
                rules_config["rules"] = new_rules
                config_manager.save_rules_config(rules_config)
                st.success("规则已保存")
            except Exception as e:
                st.error(f"保存规则失败: {str(e)}")

def show_rule_providers_config():
    """显示规则提供者配置界面"""
    st.header("规则提供者配置")
    # 显示规则提供者说明
    st.markdown("""
    ### 规则提供者配置说明
    
    每个规则提供者需要包含以下字段：
    - type: 提供者类型（如 http）
    - behavior: 行为类型（如 domain, ipcidr, classical）
    - url: 规则文件的 URL
    - path: 本地缓存路径
    - interval: 更新间隔（秒）
    
    示例：
    ```yaml
    reject:
      type: http
      behavior: domain
      url: https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt
      path: ./ruleset/reject.yaml
      interval: 86400
    ```
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("恢复默认规则提供者"):
            providers_text = yaml.dump(DEFAULT_RULE_PROVIDERS, allow_unicode=True)
            st.rerun()
    
    with col2:
        if st.button("保存规则提供者"):
            try:
                # 将 YAML 文本转换为字典
                new_providers = yaml.safe_load(providers_text)
                rules_config["rule_providers"] = new_providers
                config_manager.save_rules_config(rules_config)
                st.success("规则提供者已保存")
            except Exception as e:
                st.error(f"保存规则提供者失败: {str(e)}")
    
    # 加载当前规则提供者配置
    rules_config = config_manager.load_rules_config()
    current_providers = rules_config["rule_providers"]
    
    # 创建一个文本区域用于编辑规则提供者
    providers_text = st.text_area(
        "规则提供者配置（YAML 格式）",
        value=yaml.dump(current_providers, allow_unicode=True),
        height=400,
        help="使用 YAML 格式配置规则提供者"
    )

if __name__ == "__main__":
    main() 
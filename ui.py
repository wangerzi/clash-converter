import streamlit as st
import requests
import yaml
import threading
from datetime import datetime, timedelta, timezone
from app.utils import fetch_and_transform_config
from app.config import config_manager

def main():
    st.set_page_config(page_title="Clash 配置转换服务", layout="wide")
    st.title("Clash 配置转换服务")
    
    # Load current configuration
    config = config_manager.load_config()
    
    # Configuration section
    st.header("配置设置")
    
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
    
    # Display configurations
    st.header("配置预览")
    cached_config = config_manager.load_cached_proxy()
    if cached_config:
        st.code(yaml.dump(cached_config, allow_unicode=True), language="yaml")
    else:
        st.info("暂无缓存的转换配置")

if __name__ == "__main__":
    main() 
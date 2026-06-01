# my_advanced_search.py
import os
from typing import Optional, List, Dict, Any
from hello_agents import ToolRegistry

class MyAdvancedSearchTool:
    """
    自定义告警搜索工具类
    展示多源整合和智能选择的设计模式
    """

    def __init__(self):
        self.name = "my_advanced_earch"
        self.description = "智能搜索工具，支持多个搜索源，自动选择最佳结果"
        self.search_soureces = []
        self._setup_search_sources()

    def _setup_search_sources(self):
        """设置可用的搜索源"""
        # 检查Tavily可用性
        if os.getenv("TAVILY_API_KEY"):
            try:
                from tavily import TavilyClient
                self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
                self.search_soureces.append("tavily")
                print("✅ Tavily搜索源已启用")
            except:
                print("⚠️ Tavily库未安装")
            
        # 检查SerApi可用性
        if os.getenv("SERPAPI_API_KEY"):
            try:
                import serpapi
                self.search_soureces.append("serpapi")
                print("✅ SerpApi搜索源已启用")
            except ImportError:
                print("⚠️ SerpApi库未安装")
        
        if self.search_soureces:
            print(f"可用搜索源：{', '.join(self.search_soureces)}")
        else:
            print("⚠️ 没有可用的搜索源，请配置API密钥")
    
    def search(self, query: str) -> str:
        """执行智能搜索"""
        if not query.strip():
            return "❌ 错误:搜索查询不能为空"
        
        #检查是否有可用的搜索源
        if not self.search_sources:
            return """❌ 没有可用的搜索源，请配置以下API密钥之一:

1. Tavily API: 设置环境变量 TAVILY_API_KEY
   获取地址: https://tavily.com/

2. SerpAPI: 设置环境变量 SERPAPI_API_KEY
   获取地址: https://serpapi.com/

配置后重新运行程序。"""

        print(f"🔍 开始智能搜索: {query}")

        #尝试多个搜索源，返回最佳结果
        for source in self.search_soureces:
            try:
                if source == "tavily":
                    result = self._search_with_tavily(query)
                    
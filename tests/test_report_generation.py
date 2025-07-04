import os
import unittest
from datetime import datetime
import jinja2
import logging

class TestReportGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('test_report.log', mode='w', encoding='utf-8')
            ]
        )
        cls.logger = logging.getLogger(__name__)
        
        # 确保目录存在
        cls.reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        cls.templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        os.makedirs(cls.reports_dir, exist_ok=True)
        os.makedirs(cls.templates_dir, exist_ok=True)

    def setUp(self):
        """每个测试用例的设置"""
        self.test_date = datetime.now().strftime("%Y-%m-%d")
        
        # 创建模拟数据
        self.mock_state = {
            "company_of_interest": "000001",
            "market_report": """
### 市场概况
- 上证指数今日上涨1.2%，成交量较前日增加15%
- 行业板块普遍上涨，其中科技板块表现最佳
- 北向资金净流入35亿元
            """,
            "fundamentals_report": """
### 基本面分析
1. 财务指标
   - 营收同比增长25%
   - 净利润增长30%
   - ROE达到15.8%
            """,
            "sentiment_report": """
### 市场情绪分析
- 投资者情绪指数: 65 (偏乐观)
- 社交媒体正面提及率: 75%
            """,
            "news_report": """
### 重要新闻
1. 公司发布新产品发布会预告
2. 获得重要行业认证
            """,
            "investment_plan": "建议买入",
            "final_trade_decision": "买入 | 目标价: 28.5元",
            "risk_debate_state": {
                "judge_decision": "风险可控"
            }
        }

    def generate_report(self, trade_date: str, state: dict) -> str:
        """生成HTML报告"""
        try:
            # 加载HTML模板
            template_loader = jinja2.FileSystemLoader(searchpath=self.templates_dir)
            template_env = jinja2.Environment(loader=template_loader)
            template = template_env.get_template("report_template.html")
            
            # 准备报告数据
            report_data = {
                "trade_date": trade_date,
                "company": state.get("company_of_interest", "Unknown Company"),
                "market_type": "A股市场",
                "market_analysis": state.get("market_report", "市场分析数据未获取"),
                "fundamental_analysis": state.get("fundamentals_report", "基本面分析数据未获取"),
                "sentiment_analysis": state.get("sentiment_report", "情绪分析数据未获取"),
                "news_analysis": state.get("news_report", "新闻分析数据未获取"),
                "investment_plan": state.get("investment_plan", "投资计划未生成"),
                "final_decision": state.get("final_trade_decision", "最终决策未生成"),
                "risk_analysis": state.get("risk_debate_state", {}).get("judge_decision", "风险分析未完成"),
            }
            
            # 生成HTML
            html_output = template.render(**report_data)
            
            # 保存报告
            report_file = os.path.join(
                self.reports_dir, 
                f"report_{state['company_of_interest']}_{trade_date}.html"
            )
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html_output)
            
            return report_file
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}", exc_info=True)
            raise

    def test_report_generation(self):
        """测试报告生成功能"""
        try:
            # 生成报告
            report_file = self.generate_report(self.test_date, self.mock_state)
            
            # 验证报告文件是否生成
            self.assertTrue(os.path.exists(report_file))
            
            # 验证报告内容
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 验证关键内容是否存在
            self.assertIn(self.mock_state['company_of_interest'], content)
            self.assertIn(self.test_date, content)
            self.assertIn("市场概况", content)
            self.assertIn("基本面分析", content)
            self.assertIn("市场情绪分析", content)
            self.assertIn("重要新闻", content)
            
            self.logger.info(f"Report generated successfully at {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error in report generation test: {str(e)}", exc_info=True)
            raise

    def test_missing_data_handling(self):
        """测试缺失数据的处理"""
        # 创建缺失部分数据的state
        incomplete_state = {
            "company_of_interest": "000001",
            "market_report": "市场分析报告",
            # 故意省略其他字段
        }
        
        try:
            # 生成报告
            report_file = self.generate_report(self.test_date, incomplete_state)
            
            # 验证报告是否生成
            self.assertTrue(os.path.exists(report_file))
            
            # 验证默认值是否正确显示
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn("基本面分析数据未获取", content)
            self.assertIn("情绪分析数据未获取", content)
            self.assertIn("新闻分析数据未获取", content)
            
            self.logger.info("Missing data handling test passed")
            
        except Exception as e:
            self.logger.error(f"Error in missing data test: {str(e)}", exc_info=True)
            raise

if __name__ == '__main__':
    unittest.main() 
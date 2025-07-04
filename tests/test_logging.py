import os
import logging
import unittest

class TestLogging(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        self.log_file = 'test_logging.log'
        # 确保日志文件不存在
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
            
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.log_file, mode='w', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def test_log_writing(self):
        """测试日志写入"""
        # 写入一些测试日志
        test_messages = [
            "测试信息1",
            "测试信息2",
            "测试信息3"
        ]
        
        for msg in test_messages:
            self.logger.info(msg)
            self.logger.debug("调试信息: " + msg)
            self.logger.warning("警告信息: " + msg)
            self.logger.error("错误信息: " + msg)
        
        # 确保日志文件存在
        self.assertTrue(os.path.exists(self.log_file))
        
        # 读取日志内容
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 验证日志内容
        for msg in test_messages:
            self.assertIn(msg, content)
            self.assertIn("警告信息: " + msg, content)
            self.assertIn("错误信息: " + msg, content)
            
        # 打印日志内容以供查看
        print("\n=== 日志文件内容 ===")
        print(content)
        
    def tearDown(self):
        """清理测试环境"""
        # 关闭所有日志处理器
        for handler in logging.getLogger().handlers:
            handler.close()
        
        # 如果需要，可以删除测试日志文件
        # if os.path.exists(self.log_file):
        #     os.remove(self.log_file)

if __name__ == '__main__':
    unittest.main() 
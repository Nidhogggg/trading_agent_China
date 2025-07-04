import chromadb
from chromadb.config import Settings
from openai import OpenAI
import numpy as np
import os

class FinancialSituationMemory:
    def __init__(self, name):
        self.client = OpenAI(base_url="https://ark.cn-beijing.volces.com/api/v3/", api_key=os.getenv("VOLCES_API_KEY"))
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        
        # Delete collection if it exists
        try:
            self.chroma_client.delete_collection(name=name)
        except:
            pass
            
        # Create new collection
        self.situation_collection = self.chroma_client.create_collection(name=name)

    def get_embedding(self, text):
        """Get OpenAI embedding for a text
        
        Args:
            text (str): Input text to get embedding for
            
        Returns:
            list: The combined embedding vector
            
        Note:
            The model has a max token limit of 4096, so we split long texts into chunks,
            get embeddings for each chunk, and then combine them by taking the average.
        """
        # 设置安全的字符长度限制（约3000个token）
        CHUNK_SIZE = 5000
        
        def split_text(text, chunk_size):
            """将文本分成固定大小的块，尽量在句子边界分割"""
            # 首先按句子分割
            sentences = text.replace('\n', '. ').split('. ')
            chunks = []
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                # 如果单个句子就超过了chunk_size，则按字符强制分割
                if len(sentence) > chunk_size:
                    while sentence:
                        chunks.append(sentence[:chunk_size])
                        sentence = sentence[chunk_size:]
                    continue
                
                # 检查添加这个句子是否会超过chunk_size
                if current_size + len(sentence) + 2 <= chunk_size:  # +2 for '. '
                    current_chunk.append(sentence)
                    current_size += len(sentence) + 2
                else:
                    # 如果会超过，保存当前chunk并开始新的chunk
                    if current_chunk:
                        chunks.append('. '.join(current_chunk) + '.')
                    current_chunk = [sentence]
                    current_size = len(sentence) + 2
            
            # 添加最后一个chunk
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
            
            return chunks
        
        try:
            # 如果文本长度在限制之内，直接处理
            if len(text) <= CHUNK_SIZE:
                response = self.client.embeddings.create(
                    model="doubao-embedding-text-240715", 
                    input=text
                )
                return response.data[0].embedding
            
            # 如果文本太长，分块处理
            print(f"Text length ({len(text)}) exceeds chunk size ({CHUNK_SIZE}). Processing in chunks...")
            chunks = split_text(text, CHUNK_SIZE)
            print(f"Split into {len(chunks)} chunks")
            
            # 获取每个块的embedding
            embeddings = []
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)} (length: {len(chunk)})")
                try:
                    response = self.client.embeddings.create(
                        model="doubao-embedding-text-240715", 
                        input=chunk
                    )
                    embeddings.append(response.data[0].embedding)
                except Exception as e:
                    print(f"Error processing chunk {i+1}: {str(e)}")
                    continue
            
            if not embeddings:
                raise Exception("Failed to get any valid embeddings")
            
            # 将所有embedding向量取平均
            combined_embedding = np.mean(embeddings, axis=0)
            # 确保结果的范数与单个embedding相似
            combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)
            
            print(f"Successfully combined {len(embeddings)} embeddings")
            return combined_embedding.tolist()
            
        except Exception as e:
            print(f"Error in get_embedding: {str(e)}")
            raise

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory('financial_situation_memory')

    print("\n=== 测试 get_embedding 函数 ===")
    
    # Test 1: Short text (within chunk size)
    short_text = "测试使用中文文本生成向量嵌入。这是一个简单的金融市场分析示例。"
    print("\n测试1: 短文本嵌入")
    try:
        embedding = matcher.get_embedding(short_text)
        print(f"成功生成短文本的嵌入向量")
        print(f"嵌入向量维度: {len(embedding)}")
        print(f"前5个值: {embedding[:5]}")
    except Exception as e:
        print(f"测试短文本时出错: {str(e)}")

    # Test 2: Long text (exceeding chunk size)
    long_text = """
    这是一份全面的市场分析报告，用于测试我们的文本分块功能。近期市场表现出显著的波动性，
    主要指数经历了大幅震荡。特别是科技板块，受到利率上升和通胀担忧的影响承压明显。机构
    投资者正在减持成长股，而价值股则受到更多关注。中国人民银行的政策立场导致市场情绪发
    生转变，投资者越来越关注具有强劲现金流和稳固市场地位的公司。能源板块受益于大宗商品
    价格上涨，而公用事业和必需消费品等防御性板块则表现出较强的抗跌性。小盘股相对于大盘
    股表现不佳，反映出市场风险规避情绪上升。国际市场同样受到影响，新兴市场面临人民币汇
    率波动和地缘政治紧张局势的不利影响。债券市场出现显著变动，随着投资者对多次降息的预
    期，收益率曲线整体下移。企业盈利表现参差不齐，一些公司报告强劲业绩，而另一些则在供
    应链问题和原材料成本上升方面面临挑战。

    从行业角度来看，新能源、半导体、人工智能等战略新兴产业保持较快发展势头。医药行业在
    创新药研发和医疗器械领域取得重要进展。消费升级趋势持续，高端制造业竞争力不断提升。
    数字经济、绿色发展等新动能加快成长，为市场带来新的投资机会。房地产市场调控政策持续
    优化，因城施策力度加大。基建投资保持韧性，重大项目加快落地。制造业投资稳中有升，高
    技术制造业投资增速较快。就业形势总体稳定，居民消费信心逐步恢复。国际贸易保持增长，
    贸易结构持续优化。金融市场运行平稳，风险防控取得积极成效。

    从微观层面看，上市公司质量稳步提升，公司治理水平不断改善。科技创新能力显著增强，研
    发投入持续加大。产业链供应链韧性增强，企业竞争力稳步提升。ESG投资理念日益普及，绿
    色低碳发展成为重要方向。混合所有制改革深入推进，国企改革三年行动圆满收官。民营经济
    发展环境持续优化，营商环境不断改善。资本市场基础制度建设稳步推进，注册制改革成效显
    著。市场生态持续优化，投资者结构更趋合理。
    """ * 3  # 重复文本以确保超过chunk size
    
    print("\n测试2: 长文本嵌入（需要分块处理）")
    try:
        embedding = matcher.get_embedding(long_text)
        print(f"成功生成长文本的嵌入向量")
        print(f"嵌入向量维度: {len(embedding)}")
        print(f"前5个值: {embedding[:5]}")
    except Exception as e:
        print(f"测试长文本时出错: {str(e)}")

    print("\n=== 测试记忆功能 ===")
    
    # Example data with Chinese text
    example_data = [
        (
            "通货膨胀率上升，利率走高，消费支出下降",
            "建议关注防御性板块如必需消费品和公用事业。审查固定收益投资组合的久期。",
        ),
        (
            "科技板块波动性加大，机构投资者持续减持压力增加",
            "减少对高增长科技股的敞口。在现金流稳定的成熟科技公司中寻找价值投资机会。",
        ),
        (
            "人民币汇率走强影响新兴市场，外汇波动性增加",
            "对国际持仓进行汇率风险对冲。考虑减少新兴市场债券配置。",
        ),
        (
            "市场出现板块轮动，收益率曲线上行",
            "重新平衡投资组合以维持目标配置。考虑增加受益于利率上升的板块敞口。",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    科技板块波动性显著提升，机构投资者持续减仓，
    利率上行对成长股估值造成压力
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\n匹配 {i}:")
            print(f"相似度分数: {rec['similarity_score']:.2f}")
            print(f"匹配到的情况: {rec['matched_situation']}")
            print(f"建议: {rec['recommendation']}")

    except Exception as e:
        print(f"推荐过程中出错: {str(e)}")

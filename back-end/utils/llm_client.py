"""LLM API 客户端 — 兼容 OpenAI API 格式"""
import os
import logging
import requests

logger = logging.getLogger(__name__)

# 从环境变量读取配置
LLM_API_BASE = os.environ.get('LLM_API_BASE', 'https://api.openai.com/v1')
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo')
LLM_MAX_TOKENS = int(os.environ.get('LLM_MAX_TOKENS', '1024'))
LLM_TEMPERATURE = float(os.environ.get('LLM_TEMPERATURE', '0.7'))


class LLMClient:
    """通用 LLM 客户端，兼容 OpenAI API 格式"""

    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = base_url or LLM_API_BASE
        self.api_key = api_key or LLM_API_KEY
        self.model = model or LLM_MODEL

    def chat(self, messages: list, **kwargs) -> str:
        """发送对话请求，返回模型回复文本"""
        url = f'{self.base_url}/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        payload = {
            'model': self.model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', LLM_MAX_TOKENS),
            'temperature': kwargs.get('temperature', LLM_TEMPERATURE),
        }

        try:
            req_timeout = kwargs.get('timeout', 60)
            resp = requests.post(url, json=payload, headers=headers, timeout=req_timeout)
            resp.raise_for_status()
            data = resp.json()
            return data['choices'][0]['message']['content']
        except requests.RequestException as e:
            logger.error(f'LLM 请求失败: {e}')
            raise RuntimeError(f'LLM 请求失败: {e}')

    def chat_with_context(self, question: str, context_text: str, system_prompt: str = None) -> str:
        """基于检索到的上下文进行问答

        Args:
            question: 用户问题
            context_text: 已构建好的上下文字符串（含章节标注和分隔符）
            system_prompt: 自定义系统提示
        """
        if system_prompt is None:
            system_prompt = (
                '你是一个 AI 课程助教。请根据以下提供的课件内容片段回答用户的问题。'
                '如果课件内容不足够回答问题，请如实告知，不要编造信息。'
                '回答时请尽量清晰有条理，可以引用课件中的关键信息。'
            )

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'参考资料：\n{context_text}\n\n用户问题：{question}'},
        ]

        return self.chat(messages)


# 全局单例
llm_client = LLMClient()


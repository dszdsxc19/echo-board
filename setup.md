# Local embeeding
Ref: https://docs.langchain.com/oss/python/integrations/text_embedding/ollama

brew install ollama 

自启动
brew services start ollama

# embdding models： https://ollama.com/search?c=embedding
ollama pull nomic-embed-text

ollama list

# embedding 不需要 ollama run
uv add langchain-ollama
uv add langchain-chroma

chorma embedding setup: 
- https://docs.langchain.com/oss/python/integrations/vectorstores/chroma
- https://docs.langchain.com/oss/python/integrations/text_embedding/ollama

# 大模型
- z.ai https://docs.bigmodel.cn/cn/guide/develop/langchain/introduction
- langchain anthropic: https://docs.langchain.com/oss/python/integrations/chat/anthropic
- 模型价格： https://open.bigmodel.cn/pricing


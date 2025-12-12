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

## 拓展 数据源，我的痛点是财务数据（数字难以感知）

选型，使用 Firefly III（而不是Beancount之类的）

docker-compose 启动：https://docs.firefly-iii.org/how-to/firefly-iii/installation/docker/

docker compose -f docker-compose.yml up -d --pull=always

mcp server: https://github.com/etnperlong/firefly-iii-mcp/?tab=readme-ov-file

http://localhost:3000/mcp 连接

# Langchain MCP: https://docs.langchain.com/oss/python/langchain/mcp#http

# Langchain Agents: https://docs.langchain.com/oss/python/langchain/agents

Zhipu 结构化输出有问题：https://docs.bigmodel.cn/cn/guide/capabilities/struct-output


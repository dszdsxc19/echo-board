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


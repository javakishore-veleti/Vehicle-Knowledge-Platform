"""Shared LlamaIndex helpers — LLM + a VectorStoreIndex built over the in-memory corpus."""
from . import config, corpus


def llm():
    from llama_index.llms.openai import OpenAI as LIOpenAI
    if config.OPENAI_API_KEY:
        return LIOpenAI(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY)
    return LIOpenAI(model=config.GROQ_MODEL, api_key=config.GROQ_API_KEY, api_base=config.GROQ_BASE_URL)


def complete(prompt: str) -> str:
    return str(llm().complete(prompt))


def index():
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.embeddings.openai import OpenAIEmbedding
    Settings.llm = llm()
    if config.OPENAI_API_KEY:
        Settings.embed_model = OpenAIEmbedding(api_key=config.OPENAI_API_KEY)
    docs = [Document(text=d["text"], metadata={"source": d["source"]}) for d in corpus._DOCS]
    return VectorStoreIndex.from_documents(docs)

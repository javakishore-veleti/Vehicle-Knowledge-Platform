"""Shared Haystack helpers — OpenAI generator(s) + an InMemory document store over the corpus."""
from . import config, corpus


def _secret(tok):
    from haystack.utils import Secret
    return Secret.from_token(tok)


def generator():
    from haystack.components.generators import OpenAIGenerator
    if config.OPENAI_API_KEY:
        return OpenAIGenerator(api_key=_secret(config.OPENAI_API_KEY), model=config.OPENAI_MODEL)
    return OpenAIGenerator(api_key=_secret(config.GROQ_API_KEY), model=config.GROQ_MODEL,
                           api_base_url=config.GROQ_BASE_URL)


def chat_generator():
    from haystack.components.generators.chat import OpenAIChatGenerator
    if config.OPENAI_API_KEY:
        return OpenAIChatGenerator(api_key=_secret(config.OPENAI_API_KEY), model=config.OPENAI_MODEL)
    return OpenAIChatGenerator(api_key=_secret(config.GROQ_API_KEY), model=config.GROQ_MODEL,
                               api_base_url=config.GROQ_BASE_URL)


def complete(prompt: str) -> str:
    return generator().run(prompt=prompt)["replies"][0]


def doc_store():
    from haystack import Document
    from haystack.document_stores.in_memory import InMemoryDocumentStore
    store = InMemoryDocumentStore()
    store.write_documents([Document(content=d["text"], meta={"source": d["source"]}) for d in corpus._DOCS])
    return store

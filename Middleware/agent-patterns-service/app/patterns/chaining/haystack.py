"""Prompt chaining on **Haystack** — a native Pipeline: rewrite → OutputAdapter → answer."""
from ... import registry, hay


def run(ctx: dict) -> dict:
    from haystack import Pipeline
    from haystack.components.builders import PromptBuilder
    from haystack.components.converters import OutputAdapter
    pipe = Pipeline()
    pipe.add_component("p1", PromptBuilder(template="Rewrite as a precise vehicle question. Return only the question:\n{{ q }}", required_variables=["q"]))
    pipe.add_component("g1", hay.generator())
    pipe.add_component("pick", OutputAdapter(template="{{ replies[0] }}", output_type=str))
    pipe.add_component("p2", PromptBuilder(template="Answer concisely:\n{{ question }}", required_variables=["question"]))
    pipe.add_component("g2", hay.generator())
    pipe.connect("p1.prompt", "g1.prompt")
    pipe.connect("g1.replies", "pick.replies")
    pipe.connect("pick.output", "p2.question")
    pipe.connect("p2.prompt", "g2.prompt")
    res = pipe.run({"p1": {"q": ctx["input"]}})
    return {"answer": res["g2"]["replies"][0], "steps": ["rewrite", "answer"]}


registry.register("chaining", "haystack", run)

"""Shared toolset + system-prompt config for the ReAct pattern (reused by every framework cell).

Each use case = (tool_names, system_prompt). The tool implementations live in app/tools.py (crawl,
vehicle_spec, NHTSA recalls, dealer inventory, find_moved); each framework cell wraps them in ITS tool
decorator (LangChain @tool, CrewAI @tool, …) and selects the use case's subset by name — so this catalog
is the single source of which tools + instructions each ReAct use case gets."""

USE_CASES = {
    "smart-link-discovery": (["crawl_page"],
        "You are a resource scout. Use crawl_page on the seed URL, then return ONLY the relevant vehicle "
        "resource links (model / spec / pricing pages); skip nav, about, contact."),
    "single-model-deep-dive": (["crawl_page", "vehicle_spec"],
        "You research one model in depth. Use crawl_page to find its spec/trims/pricing pages and "
        "vehicle_spec for facts; then summarize what you found."),
    "recall-safety-lookup": (["nhtsa_recalls"],
        "You handle recall lookups. Use nhtsa_recalls for the model/year in the question, then report them."),
    "dealer-inventory-locator": (["dealer_inventory"],
        "You locate local inventory. Use dealer_inventory with the model and ZIP from the question, then report nearby stock."),
    "broken-link-repair": (["find_moved"],
        "A stored link 404'd. Use find_moved to locate where the page moved, then report the new URL."),
}

DEFAULT_UC = "single-model-deep-dive"


def spec_for(use_case: str | None) -> tuple:
    uc = use_case if use_case in USE_CASES else DEFAULT_UC
    tool_names, system = USE_CASES[uc]
    return uc, tool_names, system

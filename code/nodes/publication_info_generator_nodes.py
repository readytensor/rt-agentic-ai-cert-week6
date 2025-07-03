from typing import Dict, Any, Literal
from lesson2b_extract_entities import run_entity_extraction
from llm import get_llm
from utils import load_config
from paths import CONFIG_FILE_PATH
from langchain_tavily import TavilySearch
from langchain_community.document_loaders import SeleniumURLLoader
from states_types.publication_info_generator import (
    ContentProcessingState,
    ReviewOutput,
    References,
    SearchQueries,
)
from prompt_builder import build_prompt_from_config


config = load_config(CONFIG_FILE_PATH)

MAX_TLDR = 3
MAX_TITLES = 3


def manager_node(state: ContentProcessingState) -> Dict[str, Any]:
    """
    Manager node that coordinates the workflow and makes decisions about processing.
    """
    print("👔 Manager: Analyzing content and coordinating processing...")

    llm = get_llm(config.get("llm", "gpt-4o-mini"))

    prompt = f"""
    As a content processing manager, your task is to analyze the following project description and provide a comprehensive summary:
    
    Text: {state["text"][:500]}...
    
    Your summary should include:
    1. The main theme of the project
    2. Key details and insights that define the project's purpose
    3. The main goals of the project
    
    Ensure the summary is clear and aligns all nodes on the same task, providing context for subsequent processing steps.
    The resultant summary will be used to write an article about the project.
    """

    response = llm.invoke(prompt)
    decision = response.content
    print(f"✅ Manager decision: {decision}")
    return {"manager_decision": decision}


def tldr_generator_node(state: ContentProcessingState) -> Dict[str, Any]:
    """
    Node that generates a concise TLDR summary of the content.
    """
    # Check if this component needs revision (skip if already approved)
    if state.get("tldr_approved", False):
        print("📝 TLDR Generator: Already approved, skipping...")
        return {}

    print("📝 TLDR Generator: Creating summary...")

    llm = get_llm(config.get("llm", "gpt-4o-mini"))

    prompt = f"""
    Create a concise TLDR (Too Long; Didn't Read) summary of the following content.
    The summary should be 2-3 sentences that capture the main points and key insights.
    
    Manager's guidance: {state.get("manager_decision", "No specific guidance")}

    If the reviewer has provided specific feedback for TLDR improvement, incorporate it:
    TLDR-specific feedback: {state.get("tldr_feedback", "No specific feedback")}
    
    Content: {state["text"]}

    Return a list of {MAX_TLDR} different TLDRs at most.
    """

    tldr = llm.invoke(prompt).content
    print(f"✅ TLDR generated: {tldr[:100]}...")
    return {"tldr": tldr}


def title_generator_node(state: ContentProcessingState) -> Dict[str, Any]:
    """
    Node that generates an engaging title for the content.
    """
    # Check if this component needs revision (skip if already approved)
    if state.get("title_approved", False):
        print("🎯 Title Generator: Already approved, skipping...")
        return {}

    print("🎯 Title Generator: Creating title...")

    llm = get_llm(config.get("llm", "gpt-4o-mini"))

    prompt = f"""
    Generate an engaging and descriptive title for the following content.
    The title should be clear, concise, and capture the essence of the content.
    
    Manager's guidance: {state.get("manager_decision", "No specific guidance")}

    If the reviewer has provided specific feedback for title improvement, incorporate it:
    Title-specific feedback: {state.get("title_feedback", "No specific feedback")}
    
    Content: {state["text"]}

    Return a list of {MAX_TITLES} different titles at most.
    """

    title = llm.invoke(prompt).content
    print(f"✅ Title generated: {title}")
    return {"title": title}


def tags_extractor_node(state: ContentProcessingState) -> Dict[str, Any]:
    """
    Node that extracts relevant tags and keywords from the content.
    """

    if state.get("tags", False):
        print("🏷️ Tags Extractor: Already approved, skipping...")
        return {}
    tags = run_entity_extraction(
        state["text"],
        entity_types=[
            "Framework",
            "Model",
            "Dataset",
        ],
    )
    result = []
    for tag in tags:
        result.append(tag["name"])
    print(f"✅ Tags extracted: {', '.join(result)}")
    return {"tags": result}


def web_search_references_generator_node(
    state: ContentProcessingState,
) -> Dict[str, Any]:
    """
    Node that identifies and extracts references, citations, or sources from the content.
    """
    # Check if this component needs revision (skip if already approved)
    if state.get("references_approved", False):
        print("📚 References Generator: Already approved, skipping...")
        return {}

    print("📚 References Generator: Extracting references...")

    llm = get_llm(config.get("llm", "gpt-4o-mini")).with_structured_output(
        SearchQueries
    )

    prompt = f"""
    Manager's guidance: {state.get("manager_decision", "No specific guidance")}
    
    Provide a list of search queries to find relevant references for the following content.
    
    If the reviewer has provided specific feedback for references improvement, incorporate it:
    References-specific feedback: {state.get("references_feedback", "No specific feedback")}

    The list should not contain more than 5 elements.
    
    Content: {state["text"]}
    """

    try:
        queries = llm.invoke(prompt).queries
        print(f"✅ Queries to be executed: {queries}")

        references_summary = []
        for query in queries:
            print(f"🔍 Executing query: {query}")
            result = TavilySearch(max_results=3).invoke(query)["results"]
            references_summary.extend(result)
            print(f"✅ Successfully executed query: {query}")

        urls = [ref["url"] for ref in references_summary]
        loader = SeleniumURLLoader(urls=urls)
        docs = loader.load()
        print(f"✅ Successfully loaded {len(docs)} documents")
        references_full_content = []
        for url, doc in zip(references_summary, docs[:20]):
            references_full_content.append(
                {
                    "url": url,
                    "content": doc.page_content,
                }
            )

        llm = get_llm(config.get("llm", "gpt-4o-mini")).with_structured_output(
            References
        )
        print("📚 References Selector: Selecting references...")

        prompt = f"""
        Select the most relevant references from the following content.

        Manager's guidance: {state.get("manager_decision", "No specific guidance")}

        Content: {state["text"]}

        References: {references_full_content}

        Return a list of references with the following format:
        [
            (
                "url": "https://example.com",
                "title": "The title of the reference"
            ),
        ]

        For example:
        [
            (
                "url": "https://langchain-ai.github.io/langgraph/",
                "title": "LangGraph: A framework for building LLM applications"
            ),
            (
                "url": "https://arxiv.org/abs/1706.03762",
                "title": "Vaswani, et al. 'Attention is all you need.' Advances in neural information processing systems 30 (2017)."
            )
        ]
        """

        result = llm.invoke(prompt).references
        selected_references = []

        for reference in result:
            selected_references.append(
                {
                    "url": reference.url,
                    "title": reference.title,
                }
            )

        return {"references": selected_references}
    except Exception as e:
        print(f"❌ References extraction failed: {e}")
        return {"references": []}


def reviewer_node(state: ContentProcessingState) -> Dict[str, Any]:
    """
    Reviewer node that evaluates the quality and completeness of all processing results.
    """
    # Track revision rounds
    revision_round = state.get("revision_round", 0) + 1
    max_revisions = 2  # Limit to prevent infinite loops

    print(f"🔍 Reviewer: Evaluating processing results (Round {revision_round})")

    llm = get_llm(config.get("llm", "gpt-4o-mini")).with_structured_output(ReviewOutput)

    prompt = f"""
    Review the following content processing results for quality and completeness:
    
    Original Content Length: {len(state["text"])} characters
    Manager's Decision: {state.get("manager_decision", "N/A")}
    Revision Round: {revision_round} (Max: {max_revisions})
    
    Processing Results:
    - Title(s): {state.get("title", "Not generated")}
    - TLDR(s): {state.get("tldr", "Not generated")}
    - References: {state.get("references", [])}]
    
    IMPORTANT: Only review components that haven't been previously approved. For components that were previously approved, set their approval to True and provide positive feedback.
    
    Evaluate each component individually:
    
    1. TITLE: Is it engaging, accurate, and captures the essence of the content?
    2. TLDR: Is it concise yet comprehensive, capturing main points?
    3. TAGS: Are they relevant, comprehensive, and properly categorized?
    4. REFERENCES: Are they appropriate, useful, and complete?
    
    For each component, provide:
    - Whether it should be approved (True/False)
    - Specific feedback explaining your decision
    - If not approved, clear guidance on what needs to be improved
        
    Provide for each component:
    - Individual approval status (tldr_approved, title_approved, references_approved)
    - Individual feedback (tldr_feedback, title_feedback, references_feedback)
    - General feedback summary
    - List of suggestions for improvement
    """

    try:
        response = llm.invoke(prompt)

        # Handle individual component approvals
        overall_approved = (
            response.tldr_approved
            and response.title_approved
            and response.references_approved
        )

        # Force approval if we've reached max revisions to prevent infinite loops
        if revision_round >= max_revisions and not overall_approved:
            overall_approved = True  # Force approve all remaining components
            response.tldr_approved = True
            response.title_approved = True
            response.references_approved = True

        status = "approved" if overall_approved else "needs_revision"

        print()

        print(f"✅ Review completed: {status}")
        print(f"📋 Feedback: {response.model_dump()}")

        # Show individual component status
        components_status = [
            f"TLDR: {'✅' if response.tldr_approved else '❌'}",
            f"Title: {'✅' if response.title_approved else '❌'}",
            f"References: {'✅' if response.references_approved else '❌'}",
        ]
        print(f"📊 Component Status: {' | '.join(components_status)}")

        if not overall_approved:
            needs_revision_list = []
            if not response.tldr_approved:
                needs_revision_list.append("TLDR")
            if not response.title_approved:
                needs_revision_list.append("Title")
            if not response.references_approved:
                needs_revision_list.append("References")

            print(f"🔄 Components needing revision: {', '.join(needs_revision_list)}")

            return {
                "needs_revision": True,
                "revision_round": revision_round,
                "tldr_feedback": response.tldr_feedback,
                "title_feedback": response.title_feedback,
                "references_feedback": response.references_feedback,
                "tldr_approved": response.tldr_approved,
                "title_approved": response.title_approved,
                "references_approved": response.references_approved,
            }
        else:
            print("✅ All components approved - proceeding to final output")

            return {
                "needs_revision": False,
                "revision_round": revision_round,
                "tldr_feedback": response.tldr_feedback,
                "title_feedback": response.title_feedback,
                "references_feedback": response.references_feedback,
                "tldr_approved": response.tldr_approved,
                "title_approved": response.title_approved,
                "references_approved": response.references_approved,
            }
    except Exception as e:
        print(f"❌ Review failed: {e}")
        return {
            "review_feedback": "Review process failed.",
            "final_output": {},
            "needs_revision": False,
            "revision_round": revision_round,
        }


def route_from_reviewer(
    state: ContentProcessingState,
) -> Literal["revision_dispatcher", "end"]:
    """
    Conditional routing function that determines whether to dispatch revisions or end.
    """
    needs_revision = state.get("needs_revision", False)
    tldr_approved = state.get("tldr_approved", False)
    title_approved = state.get("title_approved", False)
    references_approved = state.get("references_approved", False)

    if not needs_revision:
        print("✅ All components approved - routing to END")
        return "end"
    else:
        print("🔄 Some components need revision - routing to revision dispatcher")
        route_to = []
        if not tldr_approved:
            route_to.append("tldr_generator")
        if not title_approved:
            route_to.append("title_generator")
        if not references_approved:
            route_to.append("web_search_references_generator")

        return route_to

"""An agent that summarizes web content."""

import os
from typing import Any, Dict, List, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from agent_demo.tools.web_to_markdown import web_to_markdown

load_dotenv()

model = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_API_BASE"],
)


class State(TypedDict):
    """A TypedDict representing the state of the summarization process.

    Attributes:
        url: The URL of the web page to summarize.
        markdown: The markdown content fetched from the URL.
        summary: The AI-generated summary of the markdown content.
        messages: Conversation messages between human and AI.
    """

    url: str
    markdown: Optional[str]
    summary: Optional[str]
    messages: List[Dict[str, Any]]


def get_markdown(state: State) -> State:
    """Gets markdown content from a URL.

    Args:
        state: A State object containing the URL to fetch markdown from.

    Returns:
        The updated state object with the 'markdown' field populated with the
            markdown content fetched from the URL.
    """
    url = state["url"]
    state["markdown"] = web_to_markdown(url)
    return state


def summarize(state: State) -> State:
    """Summarizes markdown content from the state.

    Args:
        state: A State object containing the markdown content to summarize.

    Returns:
        The updated state object with:
            - "summary": The AI-generated summary of the markdown content.
            - "messages": List of conversation messages between human and AI.

    Raises:
        ValueError: If the markdown field in state is None.
    """
    if state["markdown"] is None:
        raise ValueError("markdown is None")
    prompt = f"""Summarize the following text: {state["markdown"]}"""
    messages = [HumanMessage(content=prompt)]
    summary = model.invoke(messages).content
    messages.append(AIMessage(content=summary))

    state["summary"] = summary
    state["messages"] = messages
    return state


def make_summarize_web_agent():
    """Create a workflow graph for summarizing web content.

    This function creates a workflow that:

        1. Fetches markdown content from a URL.
        2. Generates a summary of that content.

    Returns:
        StateGraph: A compiled workflow graph that can process web URLs into summaries.
            The graph expects a State object containing a URL as input.

    Example:
        ```python
        graph = make_summarize_web_agent()
        result = graph.invoke(
            {
                "url": "https://example.com",
                "markdown": None,
                "summary": None,
                "messages": [],
            }
        )
        ```
    """
    workflow = StateGraph(State)

    workflow.add_node(get_markdown)
    workflow.add_node(summarize)

    workflow.add_edge(START, "get_markdown")
    workflow.add_edge("get_markdown", "summarize")
    workflow.add_edge("summarize", END)

    graph = workflow.compile(name="summarize_web")

    return graph


graph = make_summarize_web_agent()

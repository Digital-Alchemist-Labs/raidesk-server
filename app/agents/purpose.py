"""
Purpose and Mechanism Agent using LangGraph
"""
import json
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.prompts import PURPOSE_MECHANISM_PROMPT
from app.models import PurposeMechanism


class PurposeState(TypedDict):
    """State for purpose agent"""
    concept: str
    category: str
    result: dict
    error: str


def create_llm():
    """Create Ollama LLM instance"""
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.3,
        format="json"
    )


def generate_purpose_node(state: PurposeState) -> PurposeState:
    """Node that generates purpose and mechanism"""
    try:
        llm = create_llm()
        
        prompt = PURPOSE_MECHANISM_PROMPT.format(
            concept=state['concept'],
            category=state['category']
        )
        
        messages = [
            SystemMessage(content="당신은 의료기기 기술문서 작성 전문가입니다."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        result = json.loads(response.content)
        
        return {
            **state,
            "result": result,
            "error": ""
        }
    except Exception as e:
        return {
            **state,
            "result": {},
            "error": str(e)
        }


def create_purpose_agent():
    """Create and compile purpose agent graph"""
    workflow = StateGraph(PurposeState)
    
    # Add nodes
    workflow.add_node("generate_purpose", generate_purpose_node)
    
    # Add edges
    workflow.add_edge(START, "generate_purpose")
    workflow.add_edge("generate_purpose", END)
    
    # Compile
    return workflow.compile()


async def generate_purpose_mechanism(concept: str, category: str) -> PurposeMechanism:
    """
    Main function to generate purpose and mechanism
    
    Args:
        concept: Device concept description
        category: Selected product category
        
    Returns:
        PurposeMechanism with intended use, mechanism, etc.
    """
    agent = create_purpose_agent()
    
    result = await agent.ainvoke({
        "concept": concept,
        "category": category,
        "result": {},
        "error": ""
    })
    
    if result["error"]:
        raise Exception(f"Purpose generation failed: {result['error']}")
    
    data = result["result"]
    
    return PurposeMechanism(**data)


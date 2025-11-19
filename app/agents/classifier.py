"""
Device Classification Agent using LangGraph
"""
import json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.prompts import CLASSIFY_DEVICE_PROMPT
from app.models import ClassifyDeviceResponse, DeviceClassification, ProductCategory


class ClassifierState(TypedDict):
    """State for classifier agent"""
    concept: str
    context: str
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


def classify_node(state: ClassifierState) -> ClassifierState:
    """Node that performs device classification"""
    try:
        llm = create_llm()
        
        context_str = f"\n추가 컨텍스트: {state['context']}" if state.get('context') else ""
        
        prompt = CLASSIFY_DEVICE_PROMPT.format(
            concept=state['concept'],
            context_str=context_str
        )
        
        messages = [
            SystemMessage(content="당신은 한국 의료기기 규제 전문가입니다."),
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


def create_classifier_agent():
    """Create and compile classifier agent graph"""
    workflow = StateGraph(ClassifierState)
    
    # Add nodes
    workflow.add_node("classify", classify_node)
    
    # Add edges
    workflow.add_edge(START, "classify")
    workflow.add_edge("classify", END)
    
    # Compile
    return workflow.compile()


async def classify_device(concept: str, context: str = None) -> ClassifyDeviceResponse:
    """
    Main function to classify device
    
    Args:
        concept: Device concept description
        context: Optional additional context
        
    Returns:
        ClassifyDeviceResponse with classification and suggested categories
    """
    agent = create_classifier_agent()
    
    result = await agent.ainvoke({
        "concept": concept,
        "context": context or "",
        "result": {},
        "error": ""
    })
    
    if result["error"]:
        raise Exception(f"Classification failed: {result['error']}")
    
    data = result["result"]
    
    # Parse response
    classification = DeviceClassification(
        is_medical_device=data.get("is_medical_device", False),
        reasoning=data.get("reasoning", ""),
        confidence=data.get("confidence", 0.0),
        category=data.get("category"),
        risk_class=data.get("risk_class")
    )
    
    suggested_categories = [
        ProductCategory(**cat) for cat in data.get("suggested_categories", [])
    ]
    
    return ClassifyDeviceResponse(
        classification=classification,
        suggested_categories=suggested_categories
    )


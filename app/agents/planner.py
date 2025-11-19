"""
Plan Generation Agent using LangGraph
"""
import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.prompts import GENERATE_PLANS_PROMPT
from app.models import (
    GeneratePlansResponse, 
    Plan, 
    DeviceClassification,
    ProductCategory,
    PurposeMechanism
)


class PlannerState(TypedDict):
    """State for planner agent"""
    classification: dict
    category: dict
    purpose_mechanism: dict
    result: dict
    error: str


def create_llm():
    """Create Ollama LLM instance"""
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.5,
        format="json"
    )


def generate_plans_node(state: PlannerState) -> PlannerState:
    """Node that generates 4-tier plans"""
    try:
        llm = create_llm()
        
        prompt = GENERATE_PLANS_PROMPT.format(
            classification_json=json.dumps(state['classification'], ensure_ascii=False, indent=2),
            category_json=json.dumps(state['category'], ensure_ascii=False, indent=2),
            purpose_mechanism_json=json.dumps(state['purpose_mechanism'], ensure_ascii=False, indent=2)
        )
        
        messages = [
            SystemMessage(content="당신은 한국 의료기기 인허가 전략 전문 컨설턴트입니다."),
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


def create_planner_agent():
    """Create and compile planner agent graph"""
    workflow = StateGraph(PlannerState)
    
    # Add nodes
    workflow.add_node("generate_plans", generate_plans_node)
    
    # Add edges
    workflow.add_edge(START, "generate_plans")
    workflow.add_edge("generate_plans", END)
    
    # Compile
    return workflow.compile()


async def generate_plans(
    classification: DeviceClassification,
    category: ProductCategory,
    purpose_mechanism: PurposeMechanism
) -> GeneratePlansResponse:
    """
    Main function to generate 4-tier plans
    
    Args:
        classification: Device classification
        category: Selected product category
        purpose_mechanism: Purpose and mechanism information
        
    Returns:
        GeneratePlansResponse with 4 plans
    """
    agent = create_planner_agent()
    
    result = await agent.ainvoke({
        "classification": classification.model_dump(by_alias=True),
        "category": category.model_dump(by_alias=True),
        "purpose_mechanism": purpose_mechanism.model_dump(by_alias=True),
        "result": {},
        "error": ""
    })
    
    if result["error"]:
        raise Exception(f"Plan generation failed: {result['error']}")
    
    data = result["result"]
    
    plans = [Plan(**plan_data) for plan_data in data.get("plans", [])]
    
    return GeneratePlansResponse(plans=plans)


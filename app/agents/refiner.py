"""
Plan Refinement Agent using LangGraph
"""
import json
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.prompts import REFINE_PLAN_PROMPT
from app.models import Plan, RefinePlanResponse


class RefinerState(TypedDict):
    """State for refiner agent"""
    plan: dict
    modifications: str
    context: dict
    result: dict
    error: str


def create_llm():
    """Create Ollama LLM instance"""
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.4,
        format="json"
    )


def refine_plan_node(state: RefinerState) -> RefinerState:
    """Node that refines a plan"""
    try:
        llm = create_llm()
        
        prompt = REFINE_PLAN_PROMPT.format(
            plan_json=json.dumps(state['plan'], ensure_ascii=False, indent=2),
            modifications=state['modifications'],
            context_json=json.dumps(state['context'], ensure_ascii=False, indent=2)
        )
        
        messages = [
            SystemMessage(content="당신은 의료기기 인허가 전략 컨설턴트입니다."),
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


def create_refiner_agent():
    """Create and compile refiner agent graph"""
    workflow = StateGraph(RefinerState)
    
    # Add nodes
    workflow.add_node("refine_plan", refine_plan_node)
    
    # Add edges
    workflow.add_edge(START, "refine_plan")
    workflow.add_edge("refine_plan", END)
    
    # Compile
    return workflow.compile()


async def refine_plan(
    plan: Plan,
    modifications: str,
    context: Dict[str, Any]
) -> RefinePlanResponse:
    """
    Main function to refine a plan
    
    Args:
        plan: Original plan
        modifications: User's modification requests
        context: Additional context
        
    Returns:
        RefinePlanResponse with refined plan
    """
    agent = create_refiner_agent()
    
    result = await agent.ainvoke({
        "plan": plan.model_dump(by_alias=True),
        "modifications": modifications,
        "context": context,
        "result": {},
        "error": ""
    })
    
    if result["error"]:
        raise Exception(f"Plan refinement failed: {result['error']}")
    
    data = result["result"]
    refined_plan = Plan(**data)
    
    return RefinePlanResponse(plan=refined_plan)


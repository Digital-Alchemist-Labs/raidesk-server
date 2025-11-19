"""
Streaming endpoints for real-time LLM responses
"""
import json
import asyncio
from typing import AsyncIterator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from app.models import (
    ClassifyDeviceRequest,
    GeneratePurposeRequest,
    GeneratePlansRequest,
    RefinePlanRequest
)
from app.agents.classifier import classify_device
from app.agents.purpose import generate_purpose_mechanism
from app.agents.planner import generate_plans
from app.agents.refiner import refine_plan
from app.dependencies import get_plan_repository
from app.exceptions import PlanNotFoundException


router = APIRouter()


async def stream_classification(concept: str, context: str = None) -> AsyncIterator[str]:
    """
    Stream device classification results
    
    Yields JSON chunks as the AI generates the classification.
    """
    try:
        # Send status update
        yield f"data: {json.dumps({'type': 'status', 'message': 'Starting classification...'})}\n\n"
        
        # For streaming, we need to use the streaming version of the LLM
        # This is a simplified version - you may need to modify the agent to support streaming
        result = await classify_device(concept=concept, context=context)
        
        # Send the complete result
        yield f"data: {json.dumps({'type': 'result', 'data': result.model_dump(by_alias=True)})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


async def stream_purpose(concept: str, category: str) -> AsyncIterator[str]:
    """
    Stream purpose & mechanism generation
    """
    try:
        yield f"data: {json.dumps({'type': 'status', 'message': 'Generating purpose and mechanism...'})}\n\n"
        
        result = await generate_purpose_mechanism(concept=concept, category=category)
        
        yield f"data: {json.dumps({'type': 'result', 'data': result.model_dump(by_alias=True)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


async def stream_plans(request: GeneratePlansRequest, session_id: str = None) -> AsyncIterator[str]:
    """
    Stream plan generation - sends each plan as it's generated
    """
    try:
        yield f"data: {json.dumps({'type': 'status', 'message': 'Generating regulatory plans...'})}\n\n"
        
        # Generate all plans
        result = await generate_plans(
            classification=request.classification,
            category=request.category,
            purpose_mechanism=request.purpose_mechanism
        )
        
        # Stream each plan individually
        for i, plan in enumerate(result.plans, 1):
            yield f"data: {json.dumps({'type': 'plan', 'index': i, 'total': len(result.plans), 'data': plan.model_dump(by_alias=True)})}\n\n"
            await asyncio.sleep(0.1)  # Small delay for smoother streaming
        
        yield f"data: {json.dumps({'type': 'done', 'total_plans': len(result.plans)})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


async def stream_refinement(plan_id: str, modifications: str, context: dict) -> AsyncIterator[str]:
    """
    Stream plan refinement
    """
    try:
        yield f"data: {json.dumps({'type': 'status', 'message': 'Retrieving original plan...'})}\n\n"
        
        # Get plan repository
        from app.dependencies import get_plan_repository
        plan_repo = get_plan_repository()
        
        try:
            original_plan = await plan_repo.get_plan(plan_id)
        except PlanNotFoundException:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Plan not found: {plan_id}'})}\n\n"
            return
        
        yield f"data: {json.dumps({'type': 'status', 'message': 'Refining plan...'})}\n\n"
        
        result = await refine_plan(
            plan=original_plan,
            modifications=modifications,
            context=context
        )
        
        # Save refined plan
        await plan_repo.save_plan(
            plan=result.plan,
            modifications=modifications
        )
        
        yield f"data: {json.dumps({'type': 'result', 'data': result.model_dump(by_alias=True)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


# Streaming endpoints
@router.post("/stream/classify")
async def stream_classify_endpoint(request: ClassifyDeviceRequest):
    """
    Stream device classification results
    
    Returns SSE stream with real-time updates as the AI generates the classification.
    
    **Event Types:**
    - `status`: Progress updates
    - `result`: Final classification result
    - `done`: Stream completion
    - `error`: Error occurred
    
    **Example Frontend (JavaScript):**
    ```javascript
    const eventSource = new EventSource('/api/stream/classify');
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'status') {
        console.log(data.message);
      } else if (data.type === 'result') {
        console.log('Classification:', data.data);
      } else if (data.type === 'done') {
        eventSource.close();
      }
    };
    ```
    """
    return EventSourceResponse(
        stream_classification(request.concept, request.context)
    )


@router.post("/stream/purpose")
async def stream_purpose_endpoint(request: GeneratePurposeRequest):
    """
    Stream purpose & mechanism generation
    
    Returns SSE stream with real-time updates.
    """
    return EventSourceResponse(
        stream_purpose(request.concept, request.category)
    )


@router.post("/stream/standards")
async def stream_plans_endpoint(request: GeneratePlansRequest, session_id: str = None):
    """
    Stream plan generation
    
    Returns SSE stream with each plan sent as it's generated.
    
    **Event Types:**
    - `status`: Progress updates
    - `plan`: Individual plan (includes index and total)
    - `done`: All plans generated
    - `error`: Error occurred
    """
    return EventSourceResponse(
        stream_plans(request, session_id)
    )


@router.post("/stream/refine")
async def stream_refine_endpoint(request: RefinePlanRequest):
    """
    Stream plan refinement
    
    Returns SSE stream with real-time updates as the plan is refined.
    """
    return EventSourceResponse(
        stream_refinement(request.plan_id, request.modifications, request.context)
    )


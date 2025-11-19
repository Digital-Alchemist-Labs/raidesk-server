"""
Regulatory plan generation endpoint
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.models import GeneratePlansRequest, GeneratePlansResponse
from app.agents.planner import generate_plans
from app.storage.plan_repository import PlanRepository
from app.dependencies import get_plan_repository
from app.exceptions import StorageException

router = APIRouter()


@router.post("/standards", response_model=GeneratePlansResponse)
async def generate_plans_endpoint(
    request: GeneratePlansRequest,
    session_id: Optional[str] = None,
    plan_repo: PlanRepository = Depends(get_plan_repository)
):
    """
    Generate 4-tier regulatory plans
    
    Creates comprehensive regulatory strategies:
    - FASTEST: Minimum requirements, fastest approval
    - NORMAL: Industry standard, balanced approach
    - CONSERVATIVE: Maximum evidence, guaranteed approval
    - INNOVATIVE: Innovative device designation, priority review
    
    All generated plans are automatically saved to storage for later retrieval
    and refinement. Optionally associate plans with a session ID.
    """
    try:
        # Generate the plans
        result = await generate_plans(
            classification=request.classification,
            category=request.category,
            purpose_mechanism=request.purpose_mechanism
        )
        
        # Save each plan to storage
        for plan in result.plans:
            try:
                await plan_repo.save_plan(
                    plan=plan,
                    session_id=session_id,
                    modifications="Initial plan generation"
                )
            except StorageException as e:
                # Log error but don't fail the request
                print(f"Warning: Failed to save plan {plan.id}: {str(e)}")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


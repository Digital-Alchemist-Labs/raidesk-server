"""
Plan refinement endpoint
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models import RefinePlanRequest, RefinePlanResponse, Plan
from app.agents.refiner import refine_plan
from app.storage.plan_repository import PlanRepository
from app.dependencies import get_plan_repository
from app.exceptions import PlanNotFoundException, StorageException

router = APIRouter()


@router.post("/refine", response_model=RefinePlanResponse)
async def refine_plan_endpoint(
    request: RefinePlanRequest,
    plan_repo: PlanRepository = Depends(get_plan_repository)
):
    """
    Refine a specific plan based on user feedback
    
    The plan is automatically retrieved from storage using the plan_id.
    After refinement, a new version is saved to the repository.
    
    Adjusts the regulatory strategy according to:
    - User modification requests
    - Budget constraints
    - Timeline requirements
    - Risk tolerance
    """
    try:
        # Retrieve the original plan from storage
        try:
            original_plan = await plan_repo.get_plan(request.plan_id)
        except PlanNotFoundException:
            raise HTTPException(
                status_code=404,
                detail=f"Plan not found: {request.plan_id}"
            )
        
        # Refine the plan
        result = await refine_plan(
            plan=original_plan,
            modifications=request.modifications,
            context=request.context
        )
        
        # Save the refined plan as a new version
        refined_plan = result.plan
        await plan_repo.save_plan(
            plan=refined_plan,
            modifications=request.modifications
        )
        
        return result
        
    except HTTPException:
        raise
    except StorageException as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


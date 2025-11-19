"""
Plan management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel

from app.models import Plan
from app.storage.plan_repository import PlanRepository, PlanRecord
from app.dependencies import get_plan_repository
from app.exceptions import PlanNotFoundException, StorageException


router = APIRouter()


# Response Models
class PlanVersionInfo(BaseModel):
    """Plan version information"""
    version: int
    modifications: Optional[str]
    created_at: str


class PlanRecordResponse(BaseModel):
    """Plan record with version history"""
    id: str
    session_id: Optional[str]
    current_version: int
    versions: List[PlanVersionInfo]
    created_at: str
    updated_at: str


class PlanListItem(BaseModel):
    """Plan list item"""
    id: str
    tier: str
    title: str
    session_id: Optional[str]
    current_version: int
    created_at: str


class PlanListResponse(BaseModel):
    """List of plans response"""
    plans: List[PlanListItem]
    count: int


# Endpoints
@router.get("/plans/{plan_id}", response_model=Plan)
async def get_plan(
    plan_id: str,
    version: Optional[int] = Query(None, description="Specific version to retrieve (default: current)"),
    plan_repo: PlanRepository = Depends(get_plan_repository)
):
    """
    Get a plan by ID
    
    Retrieves a specific plan from storage. You can optionally specify a version
    to retrieve a previous version of the plan.
    """
    try:
        plan = await plan_repo.get_plan(plan_id, version=version)
        return plan
    except PlanNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}/record", response_model=PlanRecordResponse)
async def get_plan_record(
    plan_id: str,
    plan_repo: PlanRepository = Depends(get_plan_repository)
):
    """
    Get full plan record with version history
    
    Returns the complete plan record including all versions and metadata.
    """
    try:
        record = await plan_repo.get_plan_record(plan_id)
        return PlanRecordResponse(
            id=record.id,
            session_id=record.session_id,
            current_version=record.current_version,
            versions=[
                PlanVersionInfo(
                    version=v.version,
                    modifications=v.modifications,
                    created_at=v.created_at.isoformat()
                )
                for v in record.versions
            ],
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat()
        )
    except PlanNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: str,
    plan_repo: PlanRepository = Depends(get_plan_repository)
):
    """
    Delete a plan
    
    Permanently removes a plan and all its versions from storage.
    """
    try:
        await plan_repo.delete_plan(plan_id)
    except PlanNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans", response_model=PlanListResponse)
async def list_plans(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    plan_repo: PlanRepository = Depends(get_plan_repository)
):
    """
    List all plans
    
    Returns a list of all plans in storage. Optionally filter by session ID.
    """
    try:
        records = await plan_repo.list_plans(session_id=session_id)
        
        plan_items = []
        for record in records:
            # Get the current plan to extract tier and title
            try:
                current_plan_data = record.get_current_plan()
                plan_items.append(
                    PlanListItem(
                        id=record.id,
                        tier=current_plan_data.get("tier"),
                        title=current_plan_data.get("title"),
                        session_id=record.session_id,
                        current_version=record.current_version,
                        created_at=record.created_at.isoformat()
                    )
                )
            except Exception:
                # Skip invalid records
                continue
        
        return PlanListResponse(
            plans=plan_items,
            count=len(plan_items)
        )
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))


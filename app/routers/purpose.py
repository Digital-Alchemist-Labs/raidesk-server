"""
Purpose and mechanism generation endpoint
"""
from fastapi import APIRouter, HTTPException
from app.models import GeneratePurposeRequest, PurposeMechanism
from app.agents.purpose import generate_purpose_mechanism

router = APIRouter()


@router.post("/purpose", response_model=PurposeMechanism)
async def generate_purpose_endpoint(request: GeneratePurposeRequest):
    """
    Generate purpose and mechanism suggestions
    
    Creates detailed technical documentation including:
    - Intended use
    - Mechanism of action
    - Target population
    - Clinical benefit
    - Contraindications
    """
    try:
        result = await generate_purpose_mechanism(
            concept=request.concept,
            category=request.category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


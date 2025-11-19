"""
Device classification endpoint
"""
from fastapi import APIRouter, HTTPException
from app.models import ClassifyDeviceRequest, ClassifyDeviceResponse
from app.agents.classifier import classify_device

router = APIRouter()


@router.post("/classify", response_model=ClassifyDeviceResponse)
async def classify_device_endpoint(request: ClassifyDeviceRequest):
    """
    Classify device from concept description
    
    Analyzes the provided device concept and determines:
    - Whether it qualifies as a medical device
    - Suggested product categories
    - Risk classification
    """
    try:
        result = await classify_device(
            concept=request.concept,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


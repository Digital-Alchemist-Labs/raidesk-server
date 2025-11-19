"""
Pydantic models for API request/response
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums
class RiskClass(str, Enum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"


class PlanTier(str, Enum):
    FASTEST = "fastest"
    NORMAL = "normal"
    CONSERVATIVE = "conservative"
    INNOVATIVE = "innovative"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Classification Models
class DeviceClassification(BaseModel):
    is_medical_device: bool = Field(..., alias="isMedicalDevice")
    reasoning: str
    confidence: float
    category: Optional[str] = None
    risk_class: Optional[RiskClass] = Field(None, alias="riskClass")
    
    class Config:
        populate_by_name = True


class ProductCategory(BaseModel):
    code: str
    name: str
    description: str
    regulatory_path: str = Field(..., alias="regulatoryPath")
    
    class Config:
        populate_by_name = True


# Purpose and Mechanism Models
class PurposeMechanism(BaseModel):
    intended_use: str = Field(..., alias="intendedUse")
    mechanism_of_action: str = Field(..., alias="mechanismOfAction")
    target_population: str = Field(..., alias="targetPopulation")
    clinical_benefit: str = Field(..., alias="clinicalBenefit")
    contraindications: Optional[List[str]] = None
    
    class Config:
        populate_by_name = True


# Plan Models
class TimelineItem(BaseModel):
    phase: str
    description: str
    duration: str
    dependencies: Optional[List[str]] = None
    deliverables: List[str]


class CommonStandards(BaseModel):
    timeline: List[TimelineItem]
    standards: List[str]
    documentation: List[str]


class PerformanceEvaluation(BaseModel):
    timeline: List[TimelineItem]
    tests: List[str]
    documentation: List[str]


class Plan(BaseModel):
    id: str
    tier: PlanTier
    title: str
    description: str
    total_duration: str = Field(..., alias="totalDuration")
    estimated_cost: Optional[str] = Field(None, alias="estimatedCost")
    risk_level: RiskLevel = Field(..., alias="riskLevel")
    common_standards: CommonStandards = Field(..., alias="commonStandards")
    performance_evaluation: PerformanceEvaluation = Field(..., alias="performanceEvaluation")
    pros: List[str]
    cons: List[str]
    recommendations: List[str]
    
    class Config:
        populate_by_name = True


# API Request/Response Models
class ClassifyDeviceRequest(BaseModel):
    concept: str
    context: Optional[str] = None


class ClassifyDeviceResponse(BaseModel):
    classification: DeviceClassification
    suggested_categories: List[ProductCategory] = Field(..., alias="suggestedCategories")
    
    class Config:
        populate_by_name = True


class GeneratePurposeRequest(BaseModel):
    concept: str
    category: str


class GeneratePlansRequest(BaseModel):
    classification: DeviceClassification
    category: ProductCategory
    purpose_mechanism: PurposeMechanism = Field(..., alias="purposeMechanism")
    
    class Config:
        populate_by_name = True


class GeneratePlansResponse(BaseModel):
    plans: List[Plan]


class RefinePlanRequest(BaseModel):
    plan_id: str = Field(..., alias="planId")
    modifications: str
    context: Dict[str, Any]
    
    class Config:
        populate_by_name = True


class RefinePlanResponse(BaseModel):
    plan: Plan


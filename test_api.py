"""
Simple API test script for RAiDesk backend
"""
import asyncio
import json
from app.agents.classifier import classify_device
from app.agents.purpose import generate_purpose_mechanism
from app.agents.planner import generate_plans
from app.models import DeviceClassification, ProductCategory, PurposeMechanism


async def test_classifier():
    """Test device classification"""
    print("\n" + "="*50)
    print("Testing Device Classification")
    print("="*50)
    
    concept = "CT 영상에서 폐결절을 자동으로 검출하여 의사의 진단을 보조하는 AI 소프트웨어"
    
    print(f"\n개념: {concept}")
    print("\n분류 중...")
    
    try:
        result = await classify_device(concept)
        print("\n✅ 분류 완료!")
        print(f"\n의료기기 여부: {result.classification.is_medical_device}")
        print(f"신뢰도: {result.classification.confidence:.2%}")
        print(f"판단 근거: {result.classification.reasoning}")
        print(f"위험 등급: {result.classification.risk_class}")
        
        if result.suggested_categories:
            print(f"\n제안된 품목 ({len(result.suggested_categories)}개):")
            for cat in result.suggested_categories:
                print(f"  - {cat.name} ({cat.code})")
                print(f"    {cat.description}")
        
        return result
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        return None


async def test_purpose():
    """Test purpose and mechanism generation"""
    print("\n" + "="*50)
    print("Testing Purpose & Mechanism Generation")
    print("="*50)
    
    concept = "CT 영상에서 폐결절을 자동으로 검출하는 AI 소프트웨어"
    category = "영상의학 진단보조 소프트웨어"
    
    print(f"\n개념: {concept}")
    print(f"품목: {category}")
    print("\n생성 중...")
    
    try:
        result = await generate_purpose_mechanism(concept, category)
        print("\n✅ 생성 완료!")
        print(f"\n사용 목적: {result.intended_use}")
        print(f"작용 원리: {result.mechanism_of_action}")
        print(f"대상 환자군: {result.target_population}")
        print(f"임상적 이점: {result.clinical_benefit}")
        
        if result.contraindications:
            print(f"\n금기사항:")
            for contra in result.contraindications:
                print(f"  - {contra}")
        
        return result
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        return None


async def test_planner():
    """Test plan generation"""
    print("\n" + "="*50)
    print("Testing Plan Generation")
    print("="*50)
    
    # Mock data for testing
    classification = DeviceClassification(
        is_medical_device=True,
        reasoning="영상의학 진단보조 목적으로 의료기기에 해당",
        confidence=0.92,
        category="영상의학 진단보조 소프트웨어",
        risk_class="II"
    )
    
    category = ProductCategory(
        code="A41010.01",
        name="영상의학 진단보조 소프트웨어",
        description="의료영상을 분석하여 병변을 검출",
        regulatory_path="2등급 의료기기 - 인허가 필요"
    )
    
    purpose_mechanism = PurposeMechanism(
        intended_use="CT 영상에서 폐결절을 자동으로 검출",
        mechanism_of_action="딥러닝 알고리즘을 활용한 영상 분석",
        target_population="폐결절 검진이 필요한 성인 환자",
        clinical_benefit="조기 발견을 통한 치료 시기 단축",
        contraindications=["18세 미만", "영상 품질 불량"]
    )
    
    print("\n계획 생성 중...")
    
    try:
        result = await generate_plans(classification, category, purpose_mechanism)
        print(f"\n✅ 생성 완료! ({len(result.plans)}개 계획)")
        
        for plan in result.plans:
            print(f"\n{'─'*50}")
            print(f"🎯 {plan.title} ({plan.tier.value})")
            print(f"{'─'*50}")
            print(f"소요기간: {plan.total_duration}")
            print(f"예상비용: {plan.estimated_cost}")
            print(f"위험수준: {plan.risk_level.value}")
            print(f"\n설명: {plan.description}")
            
            print(f"\n장점:")
            for pro in plan.pros[:2]:  # Show first 2
                print(f"  ✅ {pro}")
            
            print(f"\n단점:")
            for con in plan.cons[:2]:  # Show first 2
                print(f"  ⚠️  {con}")
        
        return result
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("RAiDesk Backend API Test")
    print("="*50)
    
    # Test 1: Classification
    classification_result = await test_classifier()
    
    # Test 2: Purpose & Mechanism
    purpose_result = await test_purpose()
    
    # Test 3: Plan Generation
    plan_result = await test_planner()
    
    print("\n" + "="*50)
    print("테스트 완료!")
    print("="*50)
    
    if classification_result and purpose_result and plan_result:
        print("\n✅ 모든 테스트 통과!")
    else:
        print("\n⚠️  일부 테스트 실패")


if __name__ == "__main__":
    asyncio.run(main())


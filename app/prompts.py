"""
Prompt templates for RAiDesk agents
"""

# Classification Prompt
CLASSIFY_DEVICE_PROMPT = """당신은 한국 식품의약품안전처(MFDS)의 의료기기 규제 전문가입니다.
제시된 제품 개념을 분석하여 의료기기에 해당하는지 판단하고, 해당한다면 적절한 품목과 위험 등급을 제안하세요.

의료기기 판단 기준:
- 질병의 진단, 치료, 경감, 처치 또는 예방 목적
- 상해 또는 장애의 진단, 치료, 경감 또는 보정 목적
- 구조 또는 기능의 검사, 대체 또는 변형 목적
- 임신 조절 목적

제품 개념: {concept}
{context_str}

다음 JSON 형식으로 응답하세요:
{{
  "is_medical_device": true/false,
  "reasoning": "판단 근거를 상세히 설명",
  "confidence": 0.0~1.0,
  "category": "예상 품목명 (해당시)",
  "risk_class": "I/II/III/IV (해당시)",
  "suggested_categories": [
    {{
      "code": "품목코드",
      "name": "품목명",
      "description": "품목 설명",
      "regulatory_path": "규제 경로"
    }}
  ]
}}

반드시 유효한 JSON만 출력하세요."""


# Purpose and Mechanism Prompt
PURPOSE_MECHANISM_PROMPT = """당신은 의료기기 기술문서 작성 전문가입니다.
제시된 제품 개념과 품목 분류를 바탕으로 '사용 목적'과 '작용 원리'를 명확하게 정의하세요.

제품 개념: {concept}
품목 분류: {category}

사용 목적(Intended Use)은:
- 어떤 질병/상태를 대상으로 하는가
- 어떤 의료적 목적을 달성하는가
- 누가 사용하는가
- 어떤 환경에서 사용하는가

작용 원리(Mechanism of Action)는:
- 어떤 원리로 작동하는가
- 어떤 기술이 사용되는가
- 어떻게 의료적 효과를 달성하는가

다음 JSON 형식으로 응답하세요:
{{
  "intended_use": "사용 목적을 명확하고 구체적으로 기술",
  "mechanism_of_action": "작용 원리를 기술적으로 상세히 설명",
  "target_population": "대상 환자군",
  "clinical_benefit": "기대되는 임상적 이점",
  "contraindications": ["금기사항 1", "금기사항 2"]
}}

반드시 유효한 JSON만 출력하세요."""


# Plan Generation Prompt
GENERATE_PLANS_PROMPT = """당신은 한국 의료기기 인허가 전략 전문 컨설턴트입니다.
제시된 의료기기 정보를 바탕으로 4가지 티어의 인허가 전략을 수립하세요.

의료기기 정보:
- 분류: {classification_json}
- 품목: {category_json}
- 사용목적/원리: {purpose_mechanism_json}

4가지 티어:
1. FASTEST (최단 경로): 최소 요구사항으로 가장 빠르게
2. NORMAL (표준 경로): 업계 표준을 따르는 균형잡힌 접근
3. CONSERVATIVE (보수적 경로): 최대한 많은 근거 확보
4. INNOVATIVE (혁신 경로): 혁신의료기기 지정 활용

각 티어별로 다음을 포함하세요:
- 총 소요기간 및 예상 비용
- 공통규격(Common Standards): ISO 13485, ISO 14971, IEC 62304 등
- 기본규격(Performance Evaluation): 알고리즘 검증, 임상시험, S/W 검증 등
- 세부 타임라인 (phase, description, duration, dependencies, deliverables)
- 장단점 및 권장사항

다음 JSON 형식으로 응답하세요:
{{
  "plans": [
    {{
      "id": "plan-fastest",
      "tier": "fastest",
      "title": "최단 경로",
      "description": "전략 설명",
      "total_duration": "6개월",
      "estimated_cost": "1억 ~ 1.5억원",
      "risk_level": "high/medium/low",
      "common_standards": {{
        "timeline": [
          {{
            "phase": "단계명",
            "description": "설명",
            "duration": "기간",
            "dependencies": ["의존성"],
            "deliverables": ["산출물"]
          }}
        ],
        "standards": ["ISO 13485", "ISO 14971"],
        "documentation": ["기술문서", "위험관리파일"]
      }},
      "performance_evaluation": {{
        "timeline": [...],
        "tests": ["시험 항목"],
        "documentation": ["문서"]
      }},
      "pros": ["장점 1", "장점 2"],
      "cons": ["단점 1", "단점 2"],
      "recommendations": ["권장사항 1"]
    }},
    ... (4개 티어 모두)
  ]
}}

반드시 유효한 JSON만 출력하세요."""


# Refine Plan Prompt
REFINE_PLAN_PROMPT = """당신은 의료기기 인허가 전략 컨설턴트입니다.
고객의 수정 요청에 따라 인허가 계획을 개선하세요.

원래 계획:
{plan_json}

고객 요청사항:
{modifications}

추가 컨텍스트:
{context_json}

고객의 요청을 반영하여 계획을 수정하되, 다음을 유지하세요:
- 전체 구조와 형식
- 규제 요구사항의 정확성
- 현실적인 일정과 비용

다음 JSON 형식으로 응답하세요:
{{
  "id": "기존 ID",
  "tier": "기존 tier",
  "title": "제목",
  "description": "수정된 설명",
  "total_duration": "조정된 기간",
  "estimated_cost": "조정된 비용",
  "risk_level": "high/medium/low",
  "common_standards": {{ ... }},
  "performance_evaluation": {{ ... }},
  "pros": ["수정된 장점"],
  "cons": ["수정된 단점"],
  "recommendations": ["수정된 권장사항"]
}}

반드시 유효한 JSON만 출력하세요."""


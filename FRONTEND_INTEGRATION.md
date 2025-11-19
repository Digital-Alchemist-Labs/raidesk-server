# Frontend Integration Guide

프론트엔드(raidesk-app)와 백엔드(raidesk-server) 연동 가이드입니다.

## Quick Start

### 1. 백엔드 서버 시작

```bash
cd /Users/jaylee_83/Documents/_itsjayspace/git_clones/raidesk-server

# 초기 설정 (최초 1회)
./setup.sh

# 서버 실행
./run.sh
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 2. 프론트엔드 설정

프론트엔드 `.env.local` 파일 수정:

```bash
cd /Users/jaylee_83/Documents/_itsjayspace/git_clones/raidesk-app

# .env.local 생성 또는 수정
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_USE_MOCK=false" >> .env.local
```

### 3. 프론트엔드 실행

```bash
npm run dev
```

프론트엔드가 `http://localhost:3000`에서 실행됩니다.

## API 엔드포인트 매핑

프론트엔드의 API 호출이 백엔드로 매핑됩니다:

| 프론트엔드 | 백엔드 | 설명 |
|-----------|--------|------|
| `/api/classify` | `POST /api/classify` | 의료기기 분류 |
| `/api/purpose` | `POST /api/purpose` | 사용목적/원리 생성 |
| `/api/standards` | `POST /api/standards` | 4-tier 계획 생성 |
| `/api/refine` | `POST /api/refine` | 계획 수정 |

## 데이터 흐름

```
프론트엔드                          백엔드
─────────────────────────────────────────────────────────

1. 개념 입력
   ↓
   ClassifyDeviceRequest  →  /api/classify
                              ↓
                              Classifier Agent (LangGraph)
                              ↓
   ClassifyDeviceResponse ←  Result

2. 품목 선택
   ↓
   GeneratePurposeRequest →  /api/purpose
                              ↓
                              Purpose Agent (LangGraph)
                              ↓
   PurposeMechanism      ←   Result

3. 계획 생성
   ↓
   GeneratePlansRequest  →   /api/standards
                              ↓
                              Planner Agent (LangGraph)
                              ↓
   GeneratePlansResponse ←   4 Plans

4. 계획 수정
   ↓
   RefinePlanRequest     →   /api/refine
                              ↓
                              Refiner Agent (LangGraph)
                              ↓
   RefinePlanResponse    ←   Refined Plan
```

## 타입 호환성

백엔드는 프론트엔드의 타입 정의와 완벽하게 호환됩니다:

### DeviceClassification

```typescript
// Frontend (TypeScript)
interface DeviceClassification {
  isMedicalDevice: boolean;
  reasoning: string;
  confidence: number;
  category?: string;
  riskClass?: 'I' | 'II' | 'III' | 'IV';
}
```

```python
# Backend (Pydantic)
class DeviceClassification(BaseModel):
    is_medical_device: bool = Field(..., alias="isMedicalDevice")
    reasoning: str
    confidence: float
    category: Optional[str] = None
    risk_class: Optional[RiskClass] = Field(None, alias="riskClass")
```

Pydantic의 `alias`를 사용하여 camelCase ↔ snake_case 자동 변환됩니다.

## 테스트

### 백엔드 단독 테스트

```bash
cd /Users/jaylee_83/Documents/_itsjayspace/git_clones/raidesk-server
source venv/bin/activate
python test_api.py
```

### curl을 통한 테스트

```bash
# Health check
curl http://localhost:8000/health

# Classification
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"concept": "폐결절 검출 AI 소프트웨어"}'

# Purpose generation
curl -X POST http://localhost:8000/api/purpose \
  -H "Content-Type: application/json" \
  -d '{"concept": "폐결절 검출 AI", "category": "영상의학 진단보조"}'
```

### 프론트엔드에서 테스트

1. 프론트엔드 앱에서 Mock Mode OFF 확인
2. 개념 입력 후 분류 진행
3. 네트워크 탭에서 API 호출 확인

## 문제 해결

### CORS 오류

백엔드 `.env` 파일에서 CORS 설정 확인:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

프론트엔드 포트가 다른 경우 추가해주세요.

### Ollama 연결 실패

```bash
# Ollama 상태 확인
curl http://localhost:11434/api/tags

# Ollama 실행
ollama serve

# GPT-OSS 모델 확인
ollama list
ollama pull gpt-oss
```

### 느린 응답 시간

첫 번째 요청은 Ollama 모델 로딩으로 느릴 수 있습니다.
이후 요청은 빨라집니다.

온도(temperature) 조정으로 속도 개선 가능:
- `app/agents/*.py`에서 `temperature` 값 조정
- 0.1~0.3: 빠르지만 일관적
- 0.5~0.7: 느리지만 창의적

## 환경별 설정

### 개발 환경

```bash
# Backend
DEBUG=True
OLLAMA_BASE_URL=http://localhost:11434

# Frontend
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 프로덕션 환경

```bash
# Backend
DEBUG=False
OLLAMA_BASE_URL=http://ollama-server:11434
HOST=0.0.0.0
PORT=8000

# Frontend
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_URL=https://api.raidesk.com
```

## 모니터링

### LangSmith 연동 (선택사항)

백엔드에서 LangSmith를 활성화하면 에이전트 실행을 추적할 수 있습니다:

```bash
# Backend .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key
LANGCHAIN_PROJECT=raidesk
```

LangSmith 대시보드: https://smith.langchain.com

### API 로깅

FastAPI 자동 로깅:
- 요청/응답 자동 기록
- `uvicorn` 로그 확인
- 프로덕션에서는 로그 수집 시스템 연동 권장

## 성능 최적화

### 백엔드

1. **워커 수 증가** (프로덕션)
   ```bash
   uvicorn app.main:app --workers 4
   ```

2. **캐싱 추가** (향후 개선)
   - 동일 개념에 대한 분류 결과 캐싱
   - Redis 등 활용

3. **비동기 처리**
   - 이미 `async/await` 사용 중
   - LangGraph 비동기 실행 (`ainvoke`)

### 프론트엔드

1. **로딩 상태 표시**
   - 이미 구현됨 (`isLoading`)
   - 사용자 경험 개선

2. **재시도 로직**
   - axios 재시도 설정
   - 네트워크 오류 처리

3. **요청 취소**
   - AbortController 활용
   - 중복 요청 방지

## 다음 단계

### 추가 기능 구현

- [ ] 세션 관리 (데이터베이스 연동)
- [ ] 사용자 인증
- [ ] 파일 업로드 (기술문서 등)
- [ ] 스트리밍 응답 (실시간 생성)
- [ ] 계획 비교 기능
- [ ] PDF 내보내기

### 배포

- [ ] Docker 컨테이너화
- [ ] Kubernetes 설정
- [ ] CI/CD 파이프라인
- [ ] 모니터링 시스템

## 지원

문제가 발생하면 다음을 확인하세요:

1. 백엔드 로그: `uvicorn` 출력
2. 프론트엔드 콘솔: 브라우저 개발자 도구
3. Ollama 로그: `ollama` 출력
4. 네트워크 탭: API 요청/응답 확인

GitHub 이슈로 버그 리포트 환영합니다!


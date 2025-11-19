# 🚀 RAiDesk Backend - Quick Start Guide

5분 안에 RAiDesk 백엔드를 시작하는 방법입니다.

## 📋 사전 요구사항

- **Python 3.10+** 설치 확인
  ```bash
  python3 --version
  ```

- **Ollama 설치 및 GPT-OSS 모델 다운로드**
  ```bash
  # Ollama 설치 (https://ollama.ai)
  # macOS/Linux
  curl https://ollama.ai/install.sh | sh
  
  # GPT-OSS 모델 다운로드
  ollama pull gpt-oss
  
  # Ollama 서버 실행
  ollama serve
  ```

## 🔧 설치 및 실행

### 방법 1: 자동 설치 스크립트 (권장)

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/jaylee_83/Documents/_itsjayspace/git_clones/raidesk-server

# 2. 초기 설정 (최초 1회만)
./setup.sh

# 3. 서버 실행
./run.sh
```

### 방법 2: 수동 설치

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/jaylee_83/Documents/_itsjayspace/git_clones/raidesk-server

# 2. 가상 환경 생성
python3 -m venv venv

# 3. 가상 환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 환경 변수 설정 (필요시)
cp .env.example .env
# .env 파일 편집

# 6. 서버 실행
python app/main.py
```

### 방법 3: Docker (선택사항)

```bash
# Docker Compose로 실행 (Ollama 포함)
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## ✅ 확인

서버가 정상적으로 실행되면:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

브라우저에서 확인:
- **API 문서**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 테스트

```bash
# 가상 환경 활성화
source venv/bin/activate

# 테스트 실행
python test_api.py
```

## 🔗 프론트엔드 연동

```bash
# 1. 프론트엔드 디렉토리로 이동
cd /Users/jaylee_83/Documents/_itsjayspace/git_clones/raidesk-app

# 2. 환경 변수 설정
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_USE_MOCK=false" >> .env.local

# 3. 프론트엔드 실행
npm run dev
```

프론트엔드: http://localhost:3000

## 📚 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 서버 정보 |
| `/health` | GET | 헬스 체크 |
| `/api/classify` | POST | 의료기기 분류 |
| `/api/purpose` | POST | 사용목적/원리 생성 |
| `/api/standards` | POST | 4-tier 계획 생성 |
| `/api/refine` | POST | 계획 수정 |

상세 API 문서: http://localhost:8000/docs

## 🐛 문제 해결

### Ollama 연결 실패

```bash
# Ollama 상태 확인
curl http://localhost:11434/api/tags

# Ollama 재시작
pkill ollama
ollama serve

# GPT-OSS 모델 확인
ollama list
```

### 포트 충돌 (8000 포트 사용 중)

`.env` 파일 수정:
```bash
PORT=8001  # 다른 포트로 변경
```

### 가상 환경 문제

```bash
# 가상 환경 삭제 후 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📖 더 알아보기

- **전체 문서**: [README.md](README.md)
- **프론트엔드 연동**: [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
- **LangChain 문서**: https://docs.langchain.com/oss/python/langchain/overview
- **LangGraph 문서**: https://docs.langchain.com/oss/python/langgraph/overview

## 💡 주요 기능

### 1️⃣ 의료기기 분류
AI가 제품 개념을 분석하여 의료기기 해당 여부와 위험 등급을 판단합니다.

### 2️⃣ 사용목적 생성
기술문서에 필요한 사용 목적과 작용 원리를 자동 생성합니다.

### 3️⃣ 4-Tier 계획
- 🏃 **최단 경로**: 6개월, 최소 비용
- 📊 **표준 경로**: 9-10개월, 균형잡힌 접근
- 🛡️ **보수적 경로**: 12-15개월, 최대 근거
- 💡 **혁신 경로**: 7-8개월, 혁신의료기기 지정

### 4️⃣ 계획 수정
사용자 피드백을 반영하여 계획을 개선합니다.

## 🎯 다음 단계

1. ✅ 백엔드 서버 실행
2. ✅ API 문서 확인 (http://localhost:8000/docs)
3. ✅ 테스트 실행 (`python test_api.py`)
4. ✅ 프론트엔드 연동
5. 🚀 서비스 시작!

---

문제가 있으면 [GitHub Issues](https://github.com/Digital-Alchemist-Labs/raidesk-server/issues)에 올려주세요!


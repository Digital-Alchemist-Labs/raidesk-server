# Streaming Quick Start - 스트리밍 빠른 시작

LLM 응답을 실시간으로 스트리밍하여 더 나은 사용자 경험을 제공하세요!

## 🚀 빠른 시작

### 1. 설치 완료
스트리밍 라이브러리는 이미 설치되어 있습니다!

### 2. 서버 재시작
```bash
# 현재 서버 종료 (Ctrl+C)
# 그리고 다시 시작
./run.sh
```

### 3. 스트리밍 엔드포인트 확인
브라우저에서 열기: http://localhost:8000/docs

새로운 "Streaming" 섹션이 보일 것입니다!

## 🎯 기본 사용법

### React/TypeScript 예제

**1. 커스텀 Hook 생성** (`hooks/useStreaming.ts`):

```typescript
import { useState } from 'react';

export const useStreamingClassify = () => {
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const classify = async (concept: string) => {
    setLoading(true);
    
    const response = await fetch('http://localhost:8000/api/stream/classify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ concept })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.type === 'status') {
            setStatus(data.message);
          } else if (data.type === 'result') {
            setResult(data.data);
          } else if (data.type === 'done') {
            setLoading(false);
          }
        }
      }
    }
  };

  return { classify, status, result, loading };
};
```

**2. 컴포넌트에서 사용**:

```typescript
import { useStreamingClassify } from '@/hooks/useStreaming';

export default function ClassifyPage() {
  const [concept, setConcept] = useState('');
  const { classify, status, result, loading } = useStreamingClassify();

  return (
    <div>
      <input 
        value={concept}
        onChange={e => setConcept(e.target.value)}
        placeholder="의료기기 개념 입력..."
      />
      
      <button onClick={() => classify(concept)} disabled={loading}>
        {loading ? '분류 중...' : '분류 시작'}
      </button>

      {status && <p>📊 {status}</p>}
      
      {result && (
        <div>
          <h3>✅ 결과</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

### Next.js App Router 예제

```typescript
'use client';

import { useState } from 'react';

export default function StreamingDemo() {
  const [concept, setConcept] = useState('');
  const [messages, setMessages] = useState<string[]>([]);
  const [result, setResult] = useState(null);

  const handleStream = async () => {
    setMessages([]);
    setResult(null);

    const response = await fetch('/api/stream/classify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ concept })
    });

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.type === 'status') {
            setMessages(prev => [...prev, data.message]);
          } else if (data.type === 'result') {
            setResult(data.data);
          }
        }
      }
    }
  };

  return (
    <div className="p-4">
      <h1>실시간 AI 분류</h1>
      
      <textarea
        value={concept}
        onChange={e => setConcept(e.target.value)}
        className="w-full p-2 border"
        placeholder="의료기기 개념을 입력하세요..."
      />
      
      <button 
        onClick={handleStream}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        스트리밍 시작
      </button>

      <div className="mt-4">
        <h3>진행 상황:</h3>
        {messages.map((msg, i) => (
          <p key={i}>• {msg}</p>
        ))}
      </div>

      {result && (
        <div className="mt-4 p-4 bg-green-50 rounded">
          <h3>결과:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

## 📡 사용 가능한 스트리밍 엔드포인트

### 1. 기기 분류 스트리밍
```javascript
POST /api/stream/classify

// 요청
{
  "concept": "스마트 인슐린 펌프",
  "context": "자동 혈당 조절 기능"
}

// 스트림 응답
data: {"type":"status","message":"분류 시작..."}
data: {"type":"result","data":{...}}
data: {"type":"done"}
```

### 2. 사용 목적 생성 스트리밍
```javascript
POST /api/stream/purpose

// 요청
{
  "concept": "스마트 인슐린 펌프",
  "category": "능동형 약물 투여 기기"
}
```

### 3. 규제 계획 생성 스트리밍
```javascript
POST /api/stream/standards

// 요청
{
  "classification": {...},
  "category": {...},
  "purposeMechanism": {...}
}

// 스트림 응답 (각 계획이 순차적으로)
data: {"type":"status","message":"계획 생성 중..."}
data: {"type":"plan","index":1,"total":4,"data":{...}}
data: {"type":"plan","index":2,"total":4,"data":{...}}
data: {"type":"plan","index":3,"total":4,"data":{...}}
data: {"type":"plan","index":4,"total":4,"data":{...}}
data: {"type":"done","total_plans":4}
```

### 4. 계획 개선 스트리밍
```javascript
POST /api/stream/refine

// 요청
{
  "planId": "plan-123",
  "modifications": "비용을 30% 줄여주세요",
  "context": {"budget": 100000000}
}
```

## 🎨 UI 개선 아이디어

### 진행률 표시
```typescript
const [progress, setProgress] = useState(0);

// plan 이벤트에서
if (data.type === 'plan') {
  setProgress((data.index / data.total) * 100);
}

// UI
<div className="w-full bg-gray-200 rounded">
  <div 
    className="bg-blue-500 h-2 rounded transition-all"
    style={{ width: `${progress}%` }}
  />
</div>
```

### 타이핑 애니메이션
```typescript
const [displayText, setDisplayText] = useState('');

useEffect(() => {
  if (!result) return;
  
  let i = 0;
  const text = JSON.stringify(result, null, 2);
  const timer = setInterval(() => {
    if (i < text.length) {
      setDisplayText(text.slice(0, i + 1));
      i++;
    } else {
      clearInterval(timer);
    }
  }, 10);
  
  return () => clearInterval(timer);
}, [result]);
```

### 로딩 스피너
```typescript
{loading && (
  <div className="flex items-center gap-2">
    <div className="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent" />
    <span>{status || '처리 중...'}</span>
  </div>
)}
```

## 🧪 테스트

### cURL로 테스트
```bash
curl -N -X POST http://localhost:8000/api/stream/classify \
  -H "Content-Type: application/json" \
  -d '{"concept":"스마트 인슐린 펌프"}'
```

### 브라우저 DevTools에서 테스트
```javascript
// 브라우저 콘솔에서
async function test() {
  const response = await fetch('http://localhost:8000/api/stream/classify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ concept: '스마트 인슐린 펌프' })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    console.log(decoder.decode(value));
  }
}

test();
```

## 🔄 일반 vs 스트리밍

| 기능 | 일반 엔드포인트 | 스트리밍 엔드포인트 |
|------|----------------|-------------------|
| **URL** | `/api/classify` | `/api/stream/classify` |
| **응답 속도** | 전체 완료 후 | 실시간 |
| **사용자 경험** | 대기 필요 | 진행 상황 표시 |
| **구현 복잡도** | 간단 | 중간 |
| **추천 용도** | 간단한 앱 | 고급 UX |

## 💡 프로덕션 팁

1. **타임아웃 설정**: 긴 응답 시간 고려
2. **에러 처리**: 연결 끊김 대비
3. **재연결 로직**: 실패 시 자동 재시도
4. **로딩 상태**: 사용자에게 피드백 제공
5. **취소 기능**: 사용자가 중단 가능하도록

## 📚 더 많은 예제

전체 가이드는 [STREAMING_GUIDE.md](STREAMING_GUIDE.md)를 참조하세요:
- React Hooks 전체 코드
- 에러 처리 예제
- 재연결 로직
- 진행률 표시
- TypeScript 타입 정의

## 🎉 완료!

이제 실시간 스트리밍으로 더 나은 사용자 경험을 제공할 수 있습니다!

**다음 단계:**
1. ✅ 서버 재시작
2. ✅ `/docs`에서 스트리밍 엔드포인트 확인
3. ✅ 프론트엔드에 통합
4. ✅ 사용자 피드백 수집

질문이 있으면 [STREAMING_GUIDE.md](STREAMING_GUIDE.md)를 확인하세요! 🚀


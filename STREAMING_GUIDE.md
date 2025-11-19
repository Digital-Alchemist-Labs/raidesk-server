# Streaming Guide - Real-time LLM Responses

스트리밍 기능을 사용하면 LLM의 응답을 실시간으로 받아올 수 있습니다.

## 설치

먼저 새로운 의존성을 설치하세요:

```bash
pip install -r requirements.txt
```

## 새로운 스트리밍 엔드포인트

### 1. 기기 분류 스트리밍
```
POST /api/stream/classify
```

### 2. 사용 목적 생성 스트리밍
```
POST /api/stream/purpose
```

### 3. 규제 계획 생성 스트리밍
```
POST /api/stream/standards
```

### 4. 계획 개선 스트리밍
```
POST /api/stream/refine
```

## 이벤트 타입

모든 스트리밍 엔드포인트는 다음 이벤트 타입을 반환합니다:

- `status`: 진행 상황 업데이트
- `result`: 최종 결과
- `plan`: 개별 계획 (standards 엔드포인트만)
- `done`: 스트림 완료
- `error`: 오류 발생

## 프론트엔드 통합

### React 예제

```typescript
// hooks/useStreamingClassify.ts
import { useState } from 'react';

interface StreamEvent {
  type: 'status' | 'result' | 'done' | 'error';
  message?: string;
  data?: any;
}

export const useStreamingClassify = () => {
  const [status, setStatus] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const classify = async (concept: string, context?: string) => {
    setIsStreaming(true);
    setError(null);
    setStatus('연결 중...');

    try {
      const response = await fetch('http://localhost:8000/api/stream/classify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ concept, context }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('스트림을 읽을 수 없습니다');

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          setIsStreaming(false);
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6)) as StreamEvent;

            switch (data.type) {
              case 'status':
                setStatus(data.message || '');
                break;
              case 'result':
                setResult(data.data);
                break;
              case 'error':
                setError(data.message || '오류가 발생했습니다');
                setIsStreaming(false);
                break;
              case 'done':
                setStatus('완료');
                setIsStreaming(false);
                break;
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다');
      setIsStreaming(false);
    }
  };

  return { classify, status, result, error, isStreaming };
};
```

### 컴포넌트 사용 예제

```typescript
// components/StreamingClassifier.tsx
import React, { useState } from 'react';
import { useStreamingClassify } from '../hooks/useStreamingClassify';

export const StreamingClassifier: React.FC = () => {
  const [concept, setConcept] = useState('');
  const { classify, status, result, error, isStreaming } = useStreamingClassify();

  const handleClassify = () => {
    classify(concept);
  };

  return (
    <div className="streaming-classifier">
      <h2>실시간 기기 분류</h2>
      
      <textarea
        value={concept}
        onChange={(e) => setConcept(e.target.value)}
        placeholder="의료기기 개념을 입력하세요..."
        disabled={isStreaming}
      />

      <button onClick={handleClassify} disabled={isStreaming}>
        {isStreaming ? '분류 중...' : '분류 시작'}
      </button>

      {status && (
        <div className="status">
          <p>상태: {status}</p>
        </div>
      )}

      {error && (
        <div className="error">
          <p>오류: {error}</p>
        </div>
      )}

      {result && (
        <div className="result">
          <h3>분류 결과</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
```

### 다중 계획 스트리밍 예제

```typescript
// hooks/useStreamingPlans.ts
import { useState } from 'react';

export const useStreamingPlans = () => {
  const [status, setStatus] = useState<string>('');
  const [plans, setPlans] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const generatePlans = async (
    classification: any,
    category: any,
    purposeMechanism: any
  ) => {
    setIsStreaming(true);
    setError(null);
    setPlans([]);
    setStatus('연결 중...');

    try {
      const response = await fetch('http://localhost:8000/api/stream/standards', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          classification,
          category,
          purposeMechanism,
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('스트림을 읽을 수 없습니다');

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          setIsStreaming(false);
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            switch (data.type) {
              case 'status':
                setStatus(data.message || '');
                break;
              case 'plan':
                // 각 계획이 생성될 때마다 추가
                setPlans((prev) => [...prev, data.data]);
                setStatus(`계획 ${data.index}/${data.total} 생성 완료`);
                break;
              case 'error':
                setError(data.message || '오류가 발생했습니다');
                setIsStreaming(false);
                break;
              case 'done':
                setStatus(`총 ${data.total_plans}개 계획 생성 완료`);
                setIsStreaming(false);
                break;
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다');
      setIsStreaming(false);
    }
  };

  return { generatePlans, status, plans, error, isStreaming };
};
```

### Vanilla JavaScript 예제

```javascript
// 기본 스트리밍
async function streamClassification(concept) {
  const response = await fetch('http://localhost:8000/api/stream/classify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ concept }),
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
        
        console.log('이벤트 타입:', data.type);
        
        if (data.type === 'status') {
          console.log('상태:', data.message);
        } else if (data.type === 'result') {
          console.log('결과:', data.data);
        } else if (data.type === 'done') {
          console.log('완료');
        }
      }
    }
  }
}

// 사용
streamClassification('스마트 인슐린 펌프');
```

## EventSource API 대안

SSE를 위한 네이티브 `EventSource` API도 사용할 수 있습니다 (GET 요청만 지원):

```javascript
const eventSource = new EventSource('http://localhost:8000/api/stream/classify');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('이벤트:', data);
};

eventSource.onerror = () => {
  console.error('연결 오류');
  eventSource.close();
};
```

**참고:** `EventSource`는 POST 요청을 지원하지 않으므로, 위의 `fetch` 예제를 사용하는 것이 좋습니다.

## 스트리밍 vs 일반 엔드포인트

### 일반 엔드포인트
```
POST /api/classify          - 전체 결과를 한 번에 반환
POST /api/purpose
POST /api/standards
POST /api/refine
```

**장점:**
- 구현이 간단
- 에러 처리가 쉬움

**단점:**
- 응답을 기다려야 함 (느린 사용자 경험)
- 진행 상황을 알 수 없음

### 스트리밍 엔드포인트
```
POST /api/stream/classify   - 실시간으로 결과 스트리밍
POST /api/stream/purpose
POST /api/stream/standards
POST /api/stream/refine
```

**장점:**
- 실시간 피드백
- 더 나은 사용자 경험
- 진행 상황 표시 가능

**단점:**
- 프론트엔드 구현이 복잡
- 연결 관리 필요

## 프로덕션 고려사항

### 1. 타임아웃 설정

```typescript
// 30초 타임아웃 예제
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000);

try {
  const response = await fetch('http://localhost:8000/api/stream/classify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ concept }),
    signal: controller.signal,
  });
  // ... 스트림 처리
} catch (err) {
  if (err.name === 'AbortError') {
    console.error('타임아웃');
  }
} finally {
  clearTimeout(timeoutId);
}
```

### 2. 재연결 로직

```typescript
const maxRetries = 3;
let retryCount = 0;

async function classifyWithRetry(concept: string) {
  while (retryCount < maxRetries) {
    try {
      await streamClassification(concept);
      break; // 성공
    } catch (err) {
      retryCount++;
      if (retryCount >= maxRetries) {
        console.error('최대 재시도 횟수 초과');
        throw err;
      }
      await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
    }
  }
}
```

### 3. 진행률 표시

```typescript
// 계획 생성 진행률
const [progress, setProgress] = useState(0);

// plan 이벤트 수신 시
if (data.type === 'plan') {
  const progressPercent = (data.index / data.total) * 100;
  setProgress(progressPercent);
}

// UI에서
<ProgressBar value={progress} max={100} />
```

## 테스트

### cURL로 테스트

```bash
# 스트리밍 분류 테스트
curl -N -X POST http://localhost:8000/api/stream/classify \
  -H "Content-Type: application/json" \
  -d '{"concept":"스마트 인슐린 펌프"}'
```

`-N` 플래그는 버퍼링을 비활성화하여 실시간 출력을 볼 수 있습니다.

## 문제 해결

### 스트림이 끊김
- 프록시/로드 밸런서 타임아웃 설정 확인
- nginx 사용 시: `proxy_read_timeout`, `proxy_buffering off` 설정

### 이벤트가 중복됨
- 청크 파싱 로직 확인
- 불완전한 줄 처리 추가

### 메모리 누수
- 컴포넌트 언마운트 시 스트림 정리
- `useEffect` cleanup 함수 사용

```typescript
useEffect(() => {
  let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;
  
  // 스트림 시작...
  
  return () => {
    // 정리
    if (reader) {
      reader.cancel();
    }
  };
}, []);
```

## 다음 단계

1. 새 의존성 설치: `pip install -r requirements.txt`
2. 서버 재시작
3. `/docs`에서 새로운 스트리밍 엔드포인트 확인
4. 프론트엔드에서 위의 예제 통합

스트리밍을 사용하면 더 나은 사용자 경험을 제공할 수 있습니다! 🚀


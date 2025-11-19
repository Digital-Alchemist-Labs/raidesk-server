# Migration Guide - New Server Features

This guide helps you migrate your existing RAiDesk frontend to use the new server features.

## Overview of Changes

The server now includes:
1. ✅ Session management with persistent storage
2. ✅ Automatic plan storage and versioning
3. ✅ Improved error handling
4. ✅ Rate limiting
5. ✅ Structured logging
6. ✅ Flexible storage backends (SQLite/Redis)

## Breaking Changes

### 1. Plan Refinement Endpoint

**Before:**
```javascript
// You had to send the entire plan back
await fetch('/api/refine', {
  method: 'POST',
  body: JSON.stringify({
    planId: plan.id,
    modifications: 'Reduce timeline',
    context: {
      original_plan: plan  // ❌ Had to include entire plan
    }
  })
});
```

**After:**
```javascript
// Just send the plan ID - it's retrieved from storage automatically
await fetch('/api/refine', {
  method: 'POST',
  body: JSON.stringify({
    planId: plan.id,  // ✅ Just the ID
    modifications: 'Reduce timeline',
    context: {
      budget: 500000  // Any additional context
    }
  })
});
```

### 2. Error Response Format

**Before:**
```json
{
  "error": "Internal server error",
  "detail": "Something went wrong"
}
```

**After:**
```json
{
  "error": "Plan not found: plan-123",
  "type": "PlanNotFoundException",
  "details": {
    "plan_id": "plan-123"
  },
  "path": "/api/plans/plan-123"
}
```

## New Features to Integrate

### 1. Session Management

Sessions allow you to track users across multiple API calls and associate plans with user sessions.

#### Implementation

```javascript
// Create a session when user starts
const createSession = async (userData = {}) => {
  const response = await fetch('http://localhost:8000/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: userData })
  });
  return response.json();
};

// Store session ID in state or localStorage
const session = await createSession({ userId: '123' });
localStorage.setItem('sessionId', session.id);

// Update session as user progresses
const updateSession = async (sessionId, data) => {
  const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data })
  });
  return response.json();
};

// Update with classification results
await updateSession(session.id, {
  classification: classificationResult,
  step: 'classification_complete'
});
```

### 2. Automatic Plan Storage

Plans are automatically saved when generated and refined.

#### Implementation

```javascript
// Generate plans with session association
const generatePlans = async (sessionId, classification, category, purpose) => {
  const response = await fetch(
    `http://localhost:8000/api/standards?session_id=${sessionId}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        classification,
        category,
        purposeMechanism: purpose
      })
    }
  );
  const result = await response.json();
  
  // Plans are automatically saved - just use the IDs
  return result.plans.map(p => p.id);
};

// Retrieve a plan later
const getPlan = async (planId) => {
  const response = await fetch(`http://localhost:8000/api/plans/${planId}`);
  return response.json();
};

// Get plan version history
const getPlanHistory = async (planId) => {
  const response = await fetch(`http://localhost:8000/api/plans/${planId}/record`);
  return response.json();
};
```

### 3. Plan Versioning

Every refinement creates a new version, allowing you to track changes and revert if needed.

#### Implementation

```javascript
// Display version history
const PlanVersionHistory = ({ planId }) => {
  const [history, setHistory] = useState(null);
  
  useEffect(() => {
    fetch(`http://localhost:8000/api/plans/${planId}/record`)
      .then(r => r.json())
      .then(setHistory);
  }, [planId]);
  
  if (!history) return <div>Loading...</div>;
  
  return (
    <div>
      <h3>Version History</h3>
      <ul>
        {history.versions.map(v => (
          <li key={v.version}>
            <strong>Version {v.version}</strong>
            {v.modifications && <p>{v.modifications}</p>}
            <small>{new Date(v.created_at).toLocaleString()}</small>
          </li>
        ))}
      </ul>
    </div>
  );
};

// Retrieve specific version
const getSpecificVersion = async (planId, version) => {
  const response = await fetch(
    `http://localhost:8000/api/plans/${planId}?version=${version}`
  );
  return response.json();
};
```

### 4. Improved Error Handling

Better error messages and proper status codes.

#### Implementation

```javascript
const handleApiCall = async (url, options) => {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      
      // Handle specific error types
      switch (error.type) {
        case 'PlanNotFoundException':
          toast.error('Plan not found. It may have expired.');
          break;
        case 'SessionNotFoundException':
          toast.error('Session expired. Please start over.');
          break;
        case 'ValidationException':
          toast.error(`Validation error: ${error.error}`);
          console.error('Validation details:', error.details);
          break;
        case 'RateLimitExceededException':
          toast.error('Too many requests. Please wait a moment.');
          break;
        default:
          toast.error('An error occurred. Please try again.');
      }
      
      throw error;
    }
    
    return response.json();
  } catch (err) {
    console.error('API Error:', err);
    throw err;
  }
};
```

### 5. Request ID Tracking

Every response includes an `X-Request-ID` header for debugging.

#### Implementation

```javascript
const apiCall = async (url, options) => {
  const response = await fetch(url, options);
  const requestId = response.headers.get('X-Request-ID');
  
  console.log('Request ID:', requestId);
  
  if (!response.ok) {
    // Include request ID in error reports
    const error = await response.json();
    console.error('Error with request ID:', requestId, error);
  }
  
  return response.json();
};
```

## Recommended React Context Setup

Create a context to manage sessions and API calls:

```javascript
// contexts/ApiContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Initialize or restore session
  useEffect(() => {
    const storedSessionId = localStorage.getItem('sessionId');
    if (storedSessionId) {
      // Verify session still exists
      fetch(`http://localhost:8000/api/sessions/${storedSessionId}`)
        .then(r => {
          if (r.ok) {
            setSessionId(storedSessionId);
          } else {
            // Session expired, create new one
            createSession();
          }
        });
    } else {
      createSession();
    }
  }, []);
  
  const createSession = async (data = {}) => {
    const response = await fetch('http://localhost:8000/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    });
    const session = await response.json();
    setSessionId(session.id);
    localStorage.setItem('sessionId', session.id);
    return session;
  };
  
  const updateSession = async (data) => {
    if (!sessionId) return;
    
    await fetch(`http://localhost:8000/api/sessions/${sessionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    });
  };
  
  const generatePlans = async (classification, category, purpose) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/standards?session_id=${sessionId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            classification,
            category,
            purposeMechanism: purpose
          })
        }
      );
      return await response.json();
    } finally {
      setLoading(false);
    }
  };
  
  const refinePlan = async (planId, modifications, context = {}) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ planId, modifications, context })
      });
      return await response.json();
    } finally {
      setLoading(false);
    }
  };
  
  const getPlan = async (planId, version = null) => {
    const url = version 
      ? `http://localhost:8000/api/plans/${planId}?version=${version}`
      : `http://localhost:8000/api/plans/${planId}`;
    const response = await fetch(url);
    return response.json();
  };
  
  const value = {
    sessionId,
    loading,
    createSession,
    updateSession,
    generatePlans,
    refinePlan,
    getPlan
  };
  
  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within ApiProvider');
  }
  return context;
};
```

### Usage in Components

```javascript
// In your component
import { useApi } from './contexts/ApiContext';

function PlanGeneration() {
  const { generatePlans, sessionId, loading } = useApi();
  const [plans, setPlans] = useState([]);
  
  const handleGenerate = async () => {
    const result = await generatePlans(
      classification,
      category,
      purposeMechanism
    );
    setPlans(result.plans);
  };
  
  return (
    <div>
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Plans'}
      </button>
      <div>Session: {sessionId}</div>
    </div>
  );
}
```

## Environment Configuration

Update your `.env.local`:

```env
# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_TIMEOUT=30000

# Optional: Session configuration
NEXT_PUBLIC_SESSION_STORAGE=localStorage
```

## Testing Checklist

- [ ] Session creation and retrieval
- [ ] Plan generation with session association
- [ ] Plan refinement without sending full plan data
- [ ] Error handling for 404, 422, 429, 500 errors
- [ ] Request ID logging
- [ ] Version history display
- [ ] Session expiration handling
- [ ] Rate limit handling

## Rollback Plan

If you need to rollback to the old API:

1. Keep your old frontend code
2. The server maintains backward compatibility for most endpoints
3. Only `/api/refine` has a breaking change
4. You can still send `original_plan` in context as a fallback

## Questions or Issues?

- Check `SERVER_FEATURES.md` for complete documentation
- Review the health endpoint: `http://localhost:8000/health`
- Check server logs for debugging
- Verify storage connection in health endpoint

## Performance Improvements

The new implementation provides:
- **Reduced payload sizes**: No need to send full plan data for refinement
- **Faster responses**: Plans retrieved from cache/storage
- **Better scalability**: Rate limiting prevents abuse
- **Improved reliability**: Proper error handling and retries


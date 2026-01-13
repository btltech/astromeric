# Quick Reference - New Implementation Patterns

## 📖 Using New Backend Patterns

### 1. Custom Exceptions

```python
from app.exceptions import InvalidDateError, AuthenticationError, StructuredLogger

logger = StructuredLogger(__name__)

try:
    if not valid_date:
        raise InvalidDateError("Invalid birth date", value=date_str)
except InvalidDateError as e:
    logger.error(e.message, request_id=request_id, code=e.code)
```

### 2. Structured Responses

```python
from app.schemas import ApiResponse, ResponseStatus, NatalProfileRequest

@router.post("/v2/natal", response_model=ApiResponse[NatalProfileData])
async def calculate_natal(request: Request, req: NatalProfileRequest):
    request_id = request.state.request_id

    try:
        # Do work
        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=result,
            message="Calculation complete",
            request_id=request_id,
        )
    except Exception as e:
        logger.error(str(e), request_id=request_id)
        raise
```

### 3. Request ID Tracking

```python
# Automatically added to every request
# Access via: request.state.request_id
# Returned in response header: X-Request-ID

# In logs:
logger.info("User action", request_id=request_id, user=name)
# Output: [req_abc123] User action | user=name
```

---

## 📖 Using New Frontend Types

### 1. Import and Use API Types

```typescript
import type {
  ApiResponse,
  NatalProfileData,
  CompatibilityData,
  DailyFeaturesData
} from '../types/api';

// Properly typed API calls
const natal: ApiResponse<NatalProfileData> = await fetchNatalProfile(...);
const compatibility: ApiResponse<CompatibilityData> = await fetchCompatibility(...);
const daily: ApiResponse<DailyFeaturesData> = await fetchDailyFeatures(...);
```

### 2. Type-Safe Components

```typescript
interface NatalChartProps {
  data: NatalProfileData;
  onClose?: () => void;
}

export function NatalChart({ data, onClose }: NatalChartProps) {
  return (
    <div>
      <h2>{data.profile.name}</h2>
      <p>Sun: {data.chart.sun_sign}</p>
    </div>
  );
}
```

### 3. Conditional 3D Rendering

```typescript
import { lazy, Suspense } from 'react';

// Only loads on desktop
const CosmicBackground = lazy(() => import('./CosmicBackground'));

function App() {
  const shouldRender3D = () => window.innerWidth > 1024;

  return (
    <>
      {shouldRender3D() && (
        <Suspense fallback={null}>
          <CosmicBackground />
        </Suspense>
      )}
    </>
  );
}
```

---

## 🧪 Running Tests

### E2E Tests

```bash
# Run all tests in headless mode
npm run test:e2e

# Open interactive Cypress UI
npm run test:e2e:open

# Run specific test file
npx cypress run --spec "cypress/e2e/critical-paths.cy.ts"
```

### Unit Tests (existing)

```bash
npm run test           # Watch mode
npm run test:run       # Run once
npm run test:coverage  # With coverage report
```

---

## 🏗️ Creating a New v2 Endpoint

### Step-by-Step Template

**1. Define request/response types** (in `backend/app/schemas.py`):

```python
class MyFeatureRequest(BaseModel):
    """Request for my feature."""
    profile: ProfilePayload
    option1: str
    option2: int = Field(default=10, ge=1, le=100)

class MyFeatureData(BaseModel):
    """Response data for my feature."""
    result: str
    score: float
    details: Dict[str, Any]
```

**2. Create router** (`backend/app/routers/myfeature.py`):

```python
from fastapi import APIRouter, Request
from ..schemas import ApiResponse, ResponseStatus, MyFeatureRequest
from ..exceptions import StructuredLogger

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/v2/myfeature", tags=["My Feature"])

@router.post("/", response_model=ApiResponse[MyFeatureData])
async def calculate_feature(request: Request, req: MyFeatureRequest):
    """Calculate my feature with standardized format."""
    request_id = request.state.request_id

    try:
        logger.info(
            "Calculating my feature",
            request_id=request_id,
            option1=req.option1,
        )

        # Do calculation
        result = my_feature_function(req)

        return ApiResponse(
            status=ResponseStatus.SUCCESS,
            data=MyFeatureData(
                result=result['value'],
                score=result['score'],
                details=result['details'],
            ),
            request_id=request_id,
        )
    except Exception as e:
        logger.error(str(e), request_id=request_id)
        raise
```

**3. Register in main.py**:

```python
from .routers import myfeature

api.include_router(myfeature.router)
```

**4. Add TypeScript types** (in `src/types/api.ts`):

```typescript
export interface MyFeatureData {
  result: string;
  score: number;
  details: Record<string, unknown>;
}
```

**5. Add API client** (in `src/api/client.ts`):

```typescript
export function fetchMyFeature(request: MyFeatureRequest) {
  return apiFetch<ApiResponse<MyFeatureData>>('/v2/myfeature', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}
```

**6. Use in component**:

```typescript
import type { MyFeatureData } from '../types/api';
import { fetchMyFeature } from '../api/client';

async function handleSubmit() {
  const response = await fetchMyFeature({
    profile: currentProfile,
    option1: 'value',
    option2: 50,
  });

  if (response.status === 'success') {
    console.log(response.data.result);
  }
}
```

---

## 🔐 Adding Auth to Endpoints

### Protect an Endpoint

```python
from fastapi import Depends
from app.auth import get_current_user
from app.models import User

@router.post("/v2/readings/save")
async def save_reading(
    request: Request,
    req: ReadingRequest,
    current_user: User = Depends(get_current_user),
):
    """Protected endpoint - requires authentication."""
    # current_user is available
    # Can use current_user.id, current_user.email, etc.

    return ApiResponse(
        status=ResponseStatus.SUCCESS,
        data={"saved": True, "user_id": current_user.id},
        request_id=request.state.request_id,
    )
```

---

## 📊 Error Response Format

### Success Response

```json
{
  "status": "success",
  "data": {
    "sun_sign": "Gemini",
    "moon_sign": "Libra",
    "rising_sign": "Virgo"
  },
  "message": "Natal profile calculated successfully",
  "request_id": "req_abc123xyz",
  "timestamp": "2026-01-01T13:54:00Z"
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_DATE",
    "message": "Invalid date format",
    "field": "date_of_birth",
    "value": "2099-12-31"
  },
  "request_id": "req_abc123xyz",
  "timestamp": "2026-01-01T13:54:00Z"
}
```

---

## 🐛 Debugging with Request IDs

### Trace a Request

```python
# In logs, you'll see:
# [req_abc123xyz] User called endpoint | profile_name=John

# Get all logs for a specific request:
# docker logs app | grep "req_abc123xyz"

# Or use structured logging:
logger.info("Something", request_id=request_id, context="value")
```

### From Frontend

```typescript
// Check response header for request ID
const response = await fetch('/api/v2/natal', {...});
const requestId = response.headers.get('X-Request-ID');
console.log(`Request ID: ${requestId}`);

// Include in error reports
if (error) {
  reportError({
    message: error.message,
    request_id: requestId,
  });
}
```

---

## 📈 Bundle Optimization Tips

### Lazy Load Expensive Features

```typescript
const PdfExporter = lazy(() => import('./utils/pdfExport'));

// Later in component:
<Suspense fallback={<Loading />}>
  <PdfExporter data={chartData} />
</Suspense>;
```

### Check Bundle Size

```bash
# Build and check sizes
npm run build:prod

# Look for large chunks:
# - CosmicBackground.xyz.js - 3D components
# - pdfExport.xyz.js - PDF generation
# - html2canvas.xyz.js - Canvas rendering
```

---

## 🔍 Common Patterns

### Validation

```python
# Before processing
if not isinstance(req.latitude, float) or not -90 <= req.latitude <= 90:
    raise InvalidCoordinatesError("Invalid latitude")
```

### Pagination

```python
from app.schemas import PaginatedResponse, PaginationParams

@router.get("/v2/items", response_model=PaginatedResponse[Item])
async def list_items(params: PaginationParams = Depends()):
    # params.page, params.page_size, params.sort_by available
    pass
```

### Structured Error Logging

```python
logger.error(
    "Chart calculation failed",
    request_id=request_id,
    code="EPHEMERIS_ERROR",
    birth_date=req.profile.date_of_birth,
    error_details=str(exception),
)
```

---

**For more details**: See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)

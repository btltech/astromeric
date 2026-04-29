# OpenAPI Type Generation

This project supports generating TypeScript types from the FastAPI backend's OpenAPI schema.

## Setup

The `openapi-typescript` package is installed as a dev dependency.

## Generating Types

### From Local Backend

1. Start the backend server:
   ```bash
   cd backend
   source ../.venv/bin/activate
   uvicorn app.main:api --reload --port 8000
   ```

2. Generate types:
   ```bash
   npm run generate:api
   ```

This creates `src/api/generated.ts` with all API types.

### From Production Backend

```bash
npm run generate:api:prod
```

## Usage

Once types are generated, import them in your code:

```typescript
import type { paths, components } from './api/generated';

// Access response types
type ForecastResponse = components['schemas']['ForecastData'];
type ProfilePayload = components['schemas']['ProfilePayload'];

// Access endpoint paths
type DailyForecastEndpoint = paths['/v2/forecasts/daily'];
type DailyForecastRequest = DailyForecastEndpoint['post']['requestBody']['content']['application/json'];
type DailyForecastResponse = DailyForecastEndpoint['post']['responses']['200']['content']['application/json'];
```

## Type-Safe API Client

The existing `src/api/client.ts` provides a typed wrapper around the API.
The generated types can be used to enhance type safety:

```typescript
import { api } from './api/client';
import type { components } from './api/generated';

type Profile = components['schemas']['ProfilePayload'];

const profile: Profile = {
  name: 'John Doe',
  date_of_birth: '1990-05-15',
  time_of_birth: '14:30',
};

const forecast = await api.forecasts.daily({ profile });
```

## Regenerating Types

Run type generation whenever:
- Backend API changes (new endpoints, modified schemas)
- After pulling changes that affect the API
- Before major releases to ensure frontend/backend sync

## Best Practices

1. **Keep types in sync**: Add `npm run generate:api` to your pre-commit hooks
2. **Review generated changes**: Check `src/api/generated.ts` diffs for breaking changes
3. **Use strict types**: Import specific types rather than using `any`
4. **Handle errors**: Use the generated error response types

## Troubleshooting

### Types not updating
Make sure the backend server is running and accessible at the expected URL.

### Schema changes not reflected
Clear any caches and regenerate:
```bash
rm src/api/generated.ts
npm run generate:api
```

### Import errors
Ensure your `tsconfig.json` includes the generated file's directory in `include`.

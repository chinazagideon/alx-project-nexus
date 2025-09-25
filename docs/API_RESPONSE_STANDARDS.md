# API Response Standards

This document outlines the standardized API response format used throughout the Connect Hire API for consistent frontend integration and improved DRF documentation.

## Response Format

All API responses follow a consistent structure:

### Success Response
```json
{
    "success": true,
    "message": "Human-readable success message",
    "data": {
        // Response payload
    },
    "status_code": 200
}
```

### Error Response
```json
{
    "success": false,
    "message": "Human-readable error message",
    "data": null,
    "status_code": 400,
    "errors": {
        // Detailed error information (optional)
    }
}
```

## Usage Examples

### 1. Using APIResponse Class

```python
from core.response import APIResponse

# Success responses
return APIResponse.success(
    data=serializer.data,
    message="User created successfully"
)

return APIResponse.created(
    data=serializer.data,
    message="Resource created successfully"
)

return APIResponse.no_content(
    message="Resource deleted successfully"
)

# Error responses
return APIResponse.error(
    message="Validation failed",
    errors={"field": ["error message"]},
    status_code=400
)

return APIResponse.not_found(
    message="User not found"
)

return APIResponse.unauthorized(
    message="Authentication required"
)
```

### 2. Using StandardResponseMixin for ViewSets

```python
from core.mixins import StandardResponseMixin
from rest_framework import viewsets

class MyViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    # All CRUD operations automatically use standardized responses
    pass
```

### 3. Using StandardAPIViewMixin for APIView

```python
from core.mixins import StandardAPIViewMixin
from rest_framework.views import APIView

class MyAPIView(StandardAPIViewMixin, APIView):
    def get(self, request):
        return self.success_response(
            data={"key": "value"},
            message="Data retrieved successfully"
        )
    
    def post(self, request):
        try:
            # Process data
            return self.created_response(
                data=result,
                message="Resource created successfully"
            )
        except ValidationError as e:
            return self.validation_error_response(
                errors=e.detail,
                message="Validation failed"
            )
```

### 4. DRF Documentation Integration

```python
from core.response import APIResponse
from drf_spectacular.utils import extend_schema

@extend_schema(
    operation_id="create_user",
    summary="Create new user",
    responses={
        201: APIResponse.success(
            data=UserSerializer(),
            message="User created successfully",
            status_code=201
        ),
        400: APIResponse.validation_error(
            errors={"field": ["error message"]},
            message="Validation failed"
        ),
        401: APIResponse.unauthorized(),
    }
)
def create(self, request):
    # Implementation
    pass
```

## Status Code Standards

| Status Code | Method | Description |
|-------------|--------|-------------|
| 200 | GET, PUT, PATCH | Success |
| 201 | POST | Created |
| 204 | DELETE | No Content |
| 400 | Any | Bad Request (Validation Error) |
| 401 | Any | Unauthorized |
| 403 | Any | Forbidden |
| 404 | Any | Not Found |
| 405 | Any | Method Not Allowed |
| 429 | Any | Too Many Requests |
| 500 | Any | Internal Server Error |

## Frontend Integration

### JavaScript/TypeScript Example

```typescript
interface APIResponse<T = any> {
    success: boolean;
    message: string;
    data: T;
    status_code: number;
    errors?: Record<string, string[]>;
}

async function fetchUsers(): Promise<APIResponse<User[]>> {
    const response = await fetch('/api/users/');
    const data: APIResponse<User[]> = await response.json();
    
    if (data.success) {
        console.log('Success:', data.message);
        return data.data; // User[]
    } else {
        console.error('Error:', data.message);
        if (data.errors) {
            console.error('Validation errors:', data.errors);
        }
        throw new Error(data.message);
    }
}
```

### React Hook Example

```typescript
import { useState, useEffect } from 'react';

interface APIResponse<T> {
    success: boolean;
    message: string;
    data: T;
    status_code: number;
    errors?: Record<string, string[]>;
}

function useAPI<T>(url: string) {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch(url)
            .then(res => res.json())
            .then((response: APIResponse<T>) => {
                if (response.success) {
                    setData(response.data);
                    setError(null);
                } else {
                    setError(response.message);
                    setData(null);
                }
            })
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, [url]);

    return { data, loading, error };
}
```

## Migration Guide

### Before (Old Format)
```python
def create(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

### After (New Format)
```python
def create(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    return APIResponse.created(
        data=serializer.data,
        message="Resource created successfully"
    )
```

## Benefits

1. **Consistent Frontend Integration**: All responses follow the same structure
2. **Better Error Handling**: Standardized error messages and codes
3. **Improved Documentation**: DRF docs show exact response format
4. **Easier Testing**: Predictable response structure
5. **Better UX**: Clear success/error messages for users

## Exception Handling

The custom exception handler automatically converts DRF exceptions to standardized format:

```python
# DRF ValidationError becomes:
{
    "success": false,
    "message": "Validation failed",
    "data": null,
    "status_code": 400,
    "errors": {
        "field_name": ["This field is required."]
    }
}
```

## Customization

You can extend the `APIResponse` class or create custom response methods:

```python
class CustomAPIResponse(APIResponse):
    @staticmethod
    def paginated_success(data, pagination_info, message="Data retrieved successfully"):
        return APIResponse.success(
            data={
                "results": data,
                "pagination": pagination_info
            },
            message=message
        )
```

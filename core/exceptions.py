from rest_framework.views import exception_handler

def drf_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework
    """
    resp = exception_handler(exc, context)
    if resp is not None:
        resp.data = {'success': False, 'detail': resp.data, 'status_code': resp.status_code}
    return resp
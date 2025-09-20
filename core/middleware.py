import uuid


class RequestIDMiddleware:
    """
    Middleware to add a request ID to the request
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Add a request ID to the request
        """
        request.request_id = uuid.uuid4().hex
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response

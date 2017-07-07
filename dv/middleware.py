from django.conf import settings

class CORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        allow = False
        for path in settings.CORS_ALLOW_PATHS:
            if request.path.startswith(path):
                allow = True
                break
        if not allow:
           return response

        response["Access-Control-Allow-Origin"] = "*"
        return response

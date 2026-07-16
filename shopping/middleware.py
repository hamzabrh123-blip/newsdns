from django.http import HttpResponsePermanentRedirect

class HttpToHttpsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check agar connection insecure (http) hai
        if not request.is_secure():
            host = request.get_host()
            url = f"https://{host}{request.get_path()}"
            return HttpResponsePermanentRedirect(url) # Ye 301 redirect hai
        
        return self.get_response(request)
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest

# Create your views here.

def health(request) -> JsonResponse:
    #print(type(request.GET))
    #print(request.GET.get("status"))
    #print(request.GET.getlist("status"))
    data: dict = {
        "status": "ok",
        # Request information
        "request": {
            "method": request.method,
            "path": request.path,
            "path_info": request.path_info,
            "scheme": request.scheme,
            "encoding": request.encoding,
            "content_type": request.content_type,
            "content_params": request.content_params,
        },
        # URL query parameters
        "GET": dict(request.GET),
        # POST form data
        "POST": dict(request.POST),
        # Request body
        "body": request.body.decode("utf-8", errors="replace"),
        # HTTP headers
        "headers": dict(request.headers),
        # Cookies
        "COOKIES": request.COOKIES,
        # Uploaded files
        "FILES": {
            key: [
                {
                    "name": file.name,
                    "size": file.size,
                    "content_type": file.content_type,
                }
                for file in request.FILES.getlist(key)
            ]
            for key in request.FILES
        },
        # WSGI metadata
        "META": {
            "REQUEST_METHOD": request.META.get("REQUEST_METHOD"),
            "PATH_INFO": request.META.get("PATH_INFO"),
            "QUERY_STRING": request.META.get("QUERY_STRING"),
            "SERVER_NAME": request.META.get("SERVER_NAME"),
            "SERVER_PORT": request.META.get("SERVER_PORT"),
            "REMOTE_ADDR": request.META.get("REMOTE_ADDR"),
            "HTTP_HOST": request.META.get("HTTP_HOST"),
            "HTTP_USER_AGENT": request.META.get("HTTP_USER_AGENT"),
            "HTTP_ACCEPT": request.META.get("HTTP_ACCEPT"),
            "CONTENT_TYPE": request.META.get("CONTENT_TYPE"),
            "CONTENT_LENGTH": request.META.get("CONTENT_LENGTH"),
        },
        # User information
        "user": {
            "is_authenticated": request.user.is_authenticated,
            "is_anonymous": request.user.is_anonymous,
        },
        # Session
        "session": dict(request.session),
    }

    kwargs: dict = {
                    "headers": {
                                "X-API-Version": "1.0",
                                },
                    
                    }
    
    return JsonResponse(
                        data,
                        status=200,
                        safe=True,
                        json_dumps_params={
                            "indent": 4,
                            "ensure_ascii": False
                        },
                        **kwargs
                    )

def version(request) -> JsonResponse:
    data: dict = {
                    "api": "device-inventory",
                    "module": "core"
                }
    return JsonResponse(
                            data,
                            status=200,
                            safe=True,
                            json_dumps_params={
                                "indent": 4,
                                "ensure_ascii": False
                            },
                        )
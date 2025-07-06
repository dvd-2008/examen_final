class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("antes de la vista")
        # Lógica antes de la vista
        response = self.get_response(request)
        # Lógica después de la vista
        print("después de la vista")
        return response

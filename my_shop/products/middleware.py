def test_middleware(get_responce):
    def middleware(request):
         response = get_responce(request)
         return response
    return middleware
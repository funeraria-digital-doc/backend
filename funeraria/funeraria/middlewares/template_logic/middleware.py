from requests import request


class DuplicateKeysMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print('no middleware')
        print(self)
        response = self.get_response(request)
        print(response.__dict__)
        print(response)
        return response
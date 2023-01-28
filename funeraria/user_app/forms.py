from allauth.account.forms import LoginForm
class MyCustomLoginForm(LoginForm):
     def __init__(self, *args, **kwargs):
        super(MyCustomLoginForm, self).__init__(*args, **kwargs)
        print('passa aqui')

    # def login(self, *args, **kwargs):
    #     print('passa aqui 1')
    #     # Add your own processing here.

    #     # You must return the original result.
    #     return super(MyCustomLoginForm, self).login(*args, **kwargs)
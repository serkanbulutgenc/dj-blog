from .base import * 

DEBUG=True
ALLOWED_HOSTS+=env.list('ALLOWED_HOSTS', default=[])
SECRET_KEY = "django-insecure-uy5yfg_!5r029!wennbn@ig#_srfl+b%-j8^-8m59z%+)am)vv-pro"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    'https://refinemui-fbik--5173--31fc58ec.local-credentialless.webcontainer.io'
]

CORS_ALLOW_CREDENTIALS = True
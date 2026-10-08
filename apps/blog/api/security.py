from allauth.headless.contrib.ninja.security import JWTTokenAuth


class JWTBearerAuth(JWTTokenAuth):
    openapi_type = "http"
    openapi_scheme = "bearer"
    openapi_bearerFormat = "JWT"  # noqa: N815 - OpenAPI field name


jwt_bearer_auth = JWTBearerAuth()

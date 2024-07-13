from starlette.requests import Request

from hard.aws.models.user import User


class AuthorizationError(Exception):
    pass


def get_aws_event(request: Request) -> dict:
    try:
        return request.scope["aws.event"]
    except KeyError:
        raise KeyError("No AWS event in request")


def get_user_claims(request: Request) -> User:
    event = get_aws_event(request)
    try:
        claims = event["requestContext"]["authorizer"]["claims"]
        user_id = claims["cognito:username"]
        email = claims["email"]
    except KeyError:
        raise AuthorizationError("Unable to get user claims")
    return User.model_validate({"id": user_id, "email": email})

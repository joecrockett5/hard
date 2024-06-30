from starlette.requests import Request


def get_aws_event(request: Request) -> dict:
    try:
        return request.scope["aws.event"]
    except KeyError:
        raise KeyError("No AWS event in request")


def get_user_claims(request: Request) -> dict:
    event = get_aws_event(request)
    return event.requestContext.authorizer.claims

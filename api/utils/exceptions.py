from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from .response import CustomResponse


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        errors = response.data
        message = "An error occurred."

        if isinstance(exc, ValidationError):
            message = "Validation failed."
        else:
            # For other DRF exceptions, extract the detail message if present
            if isinstance(errors, dict) and 'detail' in errors:
                message = errors['detail']
                errors = None
            elif isinstance(errors, list) and len(errors) > 0:
                message = str(errors[0])
                errors = None
            elif isinstance(errors, str):
                message = errors
                errors = None

        return CustomResponse.error(
            message=message,
            status_code=status_code,
            errors=errors
        )

    return response

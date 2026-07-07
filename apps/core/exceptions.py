from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler that standardizes error responses.
    Format:
    {
        "errors": [
            {
                "field": "fieldname" or "non_field_errors",
                "message": "Error description message"
            }
        ]
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_errors = []
        if isinstance(response.data, dict):
            for field, value in response.data.items():
                if isinstance(value, list):
                    for msg in value:
                        custom_errors.append({
                            "field": field,
                            "message": str(msg)
                        })
                else:
                    custom_errors.append({
                        "field": field,
                        "message": str(value)
                    })
        elif isinstance(response.data, list):
            for msg in response.data:
                custom_errors.append({
                    "field": "non_field_errors",
                    "message": str(msg)
                })
        else:
            custom_errors.append({
                "field": "non_field_errors",
                "message": str(response.data)
            })
        
        response.data = {"errors": custom_errors}

    return response

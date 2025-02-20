from rest_framework.exceptions import APIException


class OrderCreationError(APIException):
    status_code = 400
    default_detail = "Order creation error"
    default_code = "error_occurred"


class OrderCancellationError(APIException):
    status_code = 400
    default_detail = "Order cancellation error"
    default_code = "error_occurred"

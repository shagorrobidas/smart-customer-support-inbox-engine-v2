import datetime
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
from typing import Any, Optional, Dict


class CustomResponse:
    @staticmethod
    def _now_iso() -> str:
        return timezone.now().astimezone(datetime.timezone.utc).isoformat()

    @staticmethod
    def success(
        message: str,
        data: Optional[Any] = None,
        status_code: int = status.HTTP_200_OK,
    ) -> Response:

        response_data: Dict[str, Any] = {
            "success": True,
            "status_code": int(status_code),
            "message": message,
            "timestamp": CustomResponse._now_iso(),
            "data": data,
            "errors": None,
        }

        return Response(response_data, status=int(status_code))

    @staticmethod
    def error(
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: Optional[Any] = None,
        data: Optional[Any] = None,
        errors: Optional[Any] = None,
    ) -> Response:

        response_data: Dict[str, Any] = {
            "success": False,
            "status_code": int(status_code),
            "code": code if code is not None else int(status_code),
            "message": message,
            "timestamp": CustomResponse._now_iso(),
            "data": data,
            "errors": errors,
        }

        return Response(response_data, status=int(status_code))

from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .response import CustomResponse


class CustomPagination(PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        message = "Data retrieved successfully."
        
        if hasattr(self, 'view') and hasattr(self.view, 'get_queryset'):
            try:
                model = self.view.get_queryset().model
                model_name = model._meta.verbose_name_plural.title()
                message = f"{model_name} retrieved successfully."
            except Exception:
                pass

        paginated_data = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        }

        return CustomResponse.success(
            message=message,
            data=paginated_data,
            status_code=status.HTTP_200_OK
        )

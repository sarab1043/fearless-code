from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from utils.constants import (
    COUNT,
    DATA,
    LIST_FETCHED_SUCCESS,
    MESSAGE,
    NEXT,
    PREVIOUS,
    SUCCESS,
    TRUE,
)


class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"

    def get_paginated_response(self, data):
        return Response(
            {
                SUCCESS: TRUE,
                MESSAGE: LIST_FETCHED_SUCCESS,
                DATA: data,
                NEXT: self.get_next_link(),
                PREVIOUS: self.get_previous_link(),
                COUNT: self.page.paginator.count,
            }
        )
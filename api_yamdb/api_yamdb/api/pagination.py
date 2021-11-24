from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api_yamdb.settings import PAGINATOR_PAGE_ITEMS_COUNT


class Pagination(PageNumberPagination):
    page_size = PAGINATOR_PAGE_ITEMS_COUNT

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })

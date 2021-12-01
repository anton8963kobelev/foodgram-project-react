from rest_framework import status
from rest_framework.exceptions import NotFound as NotFoundError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPaginator(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    page_query_param = 'page'

    def generate_response(self, queryset, serializer_obj, request):
        try:
            page_data = self.paginate_queryset(queryset, request)
        except NotFoundError:
            return Response(
                {"error": "Для запрашиваемой страницы результатов не найдено"},
                status=status.HTTP_400_BAD_REQUEST)
        serialized_page = serializer_obj(page_data, many=True)
        return self.get_paginated_response(serialized_page.data)

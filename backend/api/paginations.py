from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    """Настройка количества объектов на странице."""

    page_size_query_param = 'limit'
from rest_framework.pagination import PageNumberPagination


class PageLimitPaginator(PageNumberPagination):
    """Класс для переопределения параметра для пагинации"""

    page_size_query_param = 'limit'

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from wagtail.models import Page

# To enable logging of search queries for use with the "Promoted search results" module
# <https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html>
# uncomment the following line and the lines indicated in the search function
# (after adding wagtail.contrib.search_promotions to INSTALLED_APPS):

# from wagtail.contrib.search_promotions.models import Query


def _perform_search(search_query):
    """Helper function to perform the search, making it easier to mock in tests."""
    if search_query:
        return Page.objects.live().search(search_query)
    return Page.objects.none()


def search(request):
    search_query = request.GET.get("query", "")
    page = request.GET.get("page", 1)

    # Search
    search_results = _perform_search(search_query)

    # To log this query for use with the "Promoted search results" module:
    # if search_query:
    #     query = Query.get(search_query)
    #     query.add_hit()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )

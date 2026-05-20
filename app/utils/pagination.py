from math import ceil

from flask import request

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100


def get_pagination_params():
    page = request.args.get("page", DEFAULT_PAGE, type=int)
    per_page = request.args.get("per_page", DEFAULT_PER_PAGE, type=int)

    page = max(page, 1)
    per_page = max(per_page, 1)
    per_page = min(per_page, MAX_PER_PAGE)

    return page, per_page


def paginate_query(query, page, per_page):
    total = query.count()
    items = (
        query
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )
    pages = ceil(total / per_page) if total else 0

    return {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1 and pages > 0
        }
    }


def paginated_response(paginated, schema):
    return {
        "items": schema.dump(paginated["items"]),
        "pagination": paginated["pagination"]
    }

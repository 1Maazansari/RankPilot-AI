"""
Pydantic schemas for Page.
"""

from pydantic import BaseModel, ConfigDict


class PageBase(BaseModel):
    """Base schema shared by all Page schemas."""

    url: str

    final_url: str | None = None

    title: str | None = None

    meta_description: str | None = None

    canonical_url: str | None = None

    robots_meta: str | None = None

    language: str | None = None

    charset: str | None = None

    status_code: int | None = None

    response_time: float | None = None

    page_size: int | None = None

    word_count: int = 0

    h1_count: int = 0

    h2_count: int = 0

    image_count: int = 0

    missing_alt_count: int = 0

    internal_links: int = 0

    external_links: int = 0

    is_indexable: bool = True

    has_https: bool = True

    has_open_graph: bool = False

    has_twitter_card: bool = False

    has_schema_markup: bool = False

    seo_score: float | None = None


class PageCreate(PageBase):
    """Schema used when creating a Page."""

    scan_id: int


class PageUpdate(BaseModel):
    """Schema used when updating a Page."""

    title: str | None = None

    meta_description: str | None = None

    seo_score: float | None = None


class PageResponse(PageBase):
    """Schema returned by the API."""

    id: int

    scan_id: int

    model_config = ConfigDict(from_attributes=True)


class PageAnalysis(PageBase):
    """
    Schema returned by the HTML parser.

    This is NOT stored directly in the database.
    """
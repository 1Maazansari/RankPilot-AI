from pydantic import BaseModel, ConfigDict, Field


class ScannerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    url: str
    title: str = ""
    meta_description: str = ""
    canonical: str = ""
    meta_robots: str = ""
    og_title: str = Field(default="", alias="og:title")
    og_description: str = Field(default="", alias="og:description")
    h1_count: int
    h2_count: int
    images: int
    missing_alt: int
    internal_links: int
    robots_found: bool
    sitemap_found: bool

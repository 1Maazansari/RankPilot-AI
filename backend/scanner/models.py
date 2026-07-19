from pydantic import BaseModel, ConfigDict, Field


class ScannerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # URL
    url: str

    # Basic SEO
    title: str = ""
    meta_description: str = ""
    canonical: str = ""
    meta_robots: str = ""

    # Technical SEO
    language: str = ""
    charset: str = ""
    viewport: str = ""
    favicon: str = ""

    # Open Graph
    og_title: str = Field(default="", alias="og:title")
    og_description: str = Field(default="", alias="og:description")
    og_image: str = Field(default="", alias="og:image")
    og_url: str = Field(default="", alias="og:url")
    og_type: str = Field(default="", alias="og:type")

    # Twitter Cards
    twitter_card: str = ""
    twitter_title: str = ""
    twitter_description: str = ""
    twitter_image: str = ""

    # Heading Analysis
    h1_count: int
    h2_count: int

    # Image Analysis
    images: int
    missing_alt: int

    # Link Analysis
    internal_links: int

    # Technical Files
    robots_found: bool
    sitemap_found: bool
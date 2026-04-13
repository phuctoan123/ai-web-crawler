from pydantic import BaseModel


class Venue(BaseModel):
    """
    Represents the data structure of a VnExpress article.
    """

    title: str
    url: str
    summary: str
    category: str
    published_at: str

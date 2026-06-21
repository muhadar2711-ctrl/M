from fastapi import APIRouter
from app.services.calendar import scrape_forexfactory, scrape_investing
from app.schemas.news import NewsAPIResponse

router = APIRouter()

@router.get("/forexfactory", response_model=NewsAPIResponse)
async def get_forexfactory_news():
    """
    Scrapes ForexFactory for High Impact (Red Folder) news.
    Timezones returned are native strings from the site.
    """
    data = await scrape_forexfactory()
    return {"status": "success", "count": len(data), "data": data}

@router.get("/investing", response_model=NewsAPIResponse)
async def get_investing_news():
    """
    Scrapes Investing.com for High Impact news (3 Bulls).
    Safe fallback to 403 if Cloudflare blocks the request.
    """
    data = await scrape_investing()
    return {"status": "success", "count": len(data), "data": data}

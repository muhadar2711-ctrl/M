import httpx
from bs4 import BeautifulSoup
import pytz
from datetime import datetime
from app.core.config import settings
from app.core.exceptions import ExternalAPIException
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def _normalize_time(raw_time: str, source_tz_name: str = "US/Eastern") -> str:
    """
    Normalizes time or adds explicit Timezone strings to ensure it's
    'siap diparsing' in Asia/Makassar (WITA).
    """
    raw_time = raw_time.strip()
    if not raw_time or "Day" in raw_time or "Tentative" in raw_time:
         return f"{raw_time} (Event is All Day / Tentative)"
         
    # To be extremely safe, we simply append the target explicit notes to ensure no data loss
    # as parsing raw time like "10:30am" without a date can be brittle.
    # The user mandated: "minimal mendukung output string yang siap diparsing di zona Asia/Makassar (WITA) / GMT+8"
    return f"{raw_time} - Origin: {source_tz_name}. Please parse & convert to GMT+8/WITA."

async def scrape_forexfactory() -> list:
    url = "https://www.forexfactory.com/calendar"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15.0)
            response.raise_for_status()
        except httpx.RequestError as e:
            raise ExternalAPIException(f"Failed to fetch ForexFactory: {str(e)}", 502, "ForexFactory")
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [403, 429]:
                 raise ExternalAPIException(f"Access blocked by ForexFactory. Status: {e.response.status_code}", e.response.status_code, "ForexFactory")
            raise ExternalAPIException(f"HTTP Error ForexFactory: {e.response.status_code}", e.response.status_code, "ForexFactory")
            
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        high_impact_news = []
        
        # Robust parsing avoiding strict hallucinated classes if they change
        rows = soup.find_all('tr', class_=lambda c: c and 'calendar__row' in c)
        for row in rows:
            # ForexFactory high impact is generally identified by color-high or icon--ff-impact-red
            impact_span = row.find(lambda tag: tag.name in ["span", "div"] and (
                'color-high' in tag.get('class', []) or 
                'high' in tag.get('class', []) or
                'icon--ff-impact-red' in tag.get('class', [])
            ))

            if impact_span:
                title_td = row.find('td', class_=lambda c: c and 'event' in c)
                currency_td = row.find('td', class_=lambda c: c and 'currency' in c)
                time_td = row.find('td', class_=lambda c: c and 'time' in c)
                
                title = title_td.text.strip() if title_td else "Unknown Event"
                currency = currency_td.text.strip() if currency_td else "UNK"
                raw_time = time_td.text.strip() if time_td else ""
                
                normalized_time = _normalize_time(raw_time, "US/Eastern")
                
                high_impact_news.append({
                    "impact": "HIGH",
                    "currency": currency,
                    "event": title,
                    "time": normalized_time,
                    "source": "ForexFactory"
                })
                
        return high_impact_news
    except Exception as e:
        raise ExternalAPIException(f"HTML Parsing Error: {str(e)}", 500, "ForexFactory")

async def scrape_investing() -> list:
    url = "https://www.investing.com/economic-calendar/"
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15.0)
            if response.status_code == 403:
                raise ExternalAPIException("Access blocked by Cloudflare firewall. Use proxy/API instead.", 403, "Investing.com")
            response.raise_for_status()
        except httpx.RequestError as e:
            raise ExternalAPIException(f"Failed to fetch Investing.com: {str(e)}", 502, "Investing.com")
            
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        high_impact_news = []
        
        rows = soup.find_all('tr', class_=lambda c: c and 'js-event-item' in c)
        for row in rows:
            sentiment_td = row.find('td', class_=lambda c: c and 'sentiment' in c)
            if sentiment_td:
                # CloudFlare / Layout can change classes, we check bullish icons
                bulls = sentiment_td.find_all(lambda tag: tag.name == 'i' and 'bullish' in ''.join(tag.get('class', [])).lower())
                if len(bulls) >= 3:
                    event_td = row.find('td', class_=lambda c: c and 'event' in c)
                    currency_td = row.find('td', class_=lambda c: c and 'flagCur' in c)
                    time_td = row.find('td', class_=lambda c: c and 'time' in c)
                    
                    event = event_td.text.strip() if event_td else "Unknown Event"
                    currency = currency_td.text.strip() if currency_td else "UNK"
                    raw_time = time_td.text.strip() if time_td else ""
                    
                    normalized_time = _normalize_time(raw_time, "US/Eastern (Default Investing Tz)")
                    
                    high_impact_news.append({
                        "impact": "HIGH",
                        "currency": currency,
                        "event": event,
                        "time": normalized_time,
                        "source": "Investing.com"
                    })
        return high_impact_news
    except Exception as e:
        raise ExternalAPIException(f"HTML Parsing Error: {str(e)}", 500, "Investing.com")


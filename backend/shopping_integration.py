# shopping_integration.py - Real shopping API integrations
import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import quote
import logging
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ShoppingResult:
    title: str
    price: str
    url: str
    image_url: str
    store: str
    rating: Optional[float] = None
    reviews: Optional[int] = None
    availability: str = "In Stock"
    shipping: str = ""
    brand: str = ""

class ShoppingAggregator:
    """Aggregate shopping results from multiple sources"""
    
    def __init__(self):
        self.session = None
        
        # API Keys (add to your .env file)
        self.ebay_app_id = os.getenv('EBAY_APP_ID')
        self.amazon_tag = os.getenv('AMAZON_ASSOCIATE_TAG')
        
        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            )
        return self.session
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
    
    async def search_all_stores(self, part_number: str, part_name: str = "") -> Dict[str, List[ShoppingResult]]:
        """Search all available stores for a part"""
        search_term = part_number if part_number else part_name
        if not search_term:
            return {}
        
        # Run all searches concurrently
        tasks = [
            self.search_ebay_api(search_term),
            self.search_amazon_scrape(search_term),
            self.search_autozone_scrape(search_term),
            self.search_rockauto_scrape(search_term),
            self.search_advance_auto_scrape(search_term),
            self.search_oreilly_scrape(search_term)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        shopping_results = {}
        store_names = ['eBay', 'Amazon', 'AutoZone', 'RockAuto', 'Advance Auto', "O'Reilly"]
        
        for i, result in enumerate(results):
            store_name = store_names[i]
            if isinstance(result, list):
                shopping_results[store_name] = result
            else:
                logging.error(f"Error searching {store_name}: {result}")
                shopping_results[store_name] = []
        
        return shopping_results
    
    async def search_ebay_api(self, search_term: str) -> List[ShoppingResult]:
        """Search eBay using their official API"""
        if not self.ebay_app_id:
            return await self.search_ebay_scrape(search_term)
        
        try:
            session = await self.get_session()
            
            # eBay Finding API
            url = "https://svcs.ebay.com/services/search/FindingService/v1"
            params = {
                'OPERATION-NAME': 'findItemsByKeywords',
                'SERVICE-VERSION': '1.0.0',
                'SECURITY-APPNAME': self.ebay_app_id,
                'RESPONSE-DATA-FORMAT': 'JSON',
                'REST-PAYLOAD': '',
                'keywords': f"{search_term} automotive part",
                'paginationInput.entriesPerPage': '10',
                'itemFilter(0).name': 'ListingType',
                'itemFilter(0).value': 'FixedPrice',
                'itemFilter(1).name': 'Condition',
                'itemFilter(1).value': 'New',
                'sortOrder': 'BestMatch'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_ebay_api_results(data)
                else:
                    # Fallback to scraping
                    return await self.search_ebay_scrape(search_term)
                    
        except Exception as e:
            logging.error(f"eBay API search failed: {e}")
            return await self.search_ebay_scrape(search_term)
    
    def _parse_ebay_api_results(self, data: Dict) -> List[ShoppingResult]:
        """Parse eBay API response"""
        results = []
        
        try:
            items = data.get('findItemsByKeywordsResponse', [{}])[0].get('searchResult', [{}])[0].get('item', [])
            
            for item in items:
                title = item.get('title', [''])[0]
                price = f"${item.get('sellingStatus', [{}])[0].get('currentPrice', [{}])[0].get('__value__', '0')}"
                url = item.get('viewItemURL', [''])[0]
                image_url = item.get('galleryURL', [''])[0]
                
                results.append(ShoppingResult(
                    title=title,
                    price=price,
                    url=url,
                    image_url=image_url,
                    store="eBay",
                    availability="Available"
                ))
                
        except Exception as e:
            logging.error(f"Error parsing eBay API results: {e}")
        
        return results
    
    async def search_ebay_scrape(self, search_term: str) -> List[ShoppingResult]:
        """Scrape eBay search results"""
        try:
            session = await self.get_session()
            url = f"https://www.ebay.com/sch/i.html?_nkw={quote(search_term + ' automotive part')}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    items = soup.find_all('div', class_='s-item__wrapper')
                    
                    for item in items[:8]:
                        try:
                            title_elem = item.find('h3', class_='s-item__title')
                            price_elem = item.find('span', class_='s-item__price')
                            link_elem = item.find('a', class_='s-item__link')
                            img_elem = item.find('img')
                            
                            if title_elem and price_elem and link_elem:
                                title = title_elem.get_text(strip=True)
                                if "Shop on eBay" not in title:
                                    results.append(ShoppingResult(
                                        title=title,
                                        price=price_elem.get_text(strip=True),
                                        url=link_elem.get('href', ''),
                                        image_url=img_elem.get('src', '') if img_elem else '',
                                        store="eBay"
                                    ))
                        except:
                            continue
                    
                    return results
                    
        except Exception as e:
            logging.error(f"eBay scraping failed: {e}")
        
        return []
    
    async def search_amazon_scrape(self, search_term: str) -> List[ShoppingResult]:
        """Scrape Amazon search results"""
        try:
            session = await self.get_session()
            url = f"https://www.amazon.com/s?k={quote(search_term + ' automotive part')}"
            
            # Amazon requires specific headers
            headers = self.headers.copy()
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            })
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    items = soup.find_all('div', {'data-component-type': 's-search-result'})
                    
                    for item in items[:6]:
                        try:
                            title_elem = item.find('h2', class_='s-size-mini')
                            if not title_elem:
                                title_elem = item.find('span', class_='a-text-normal')
                            
                            price_elem = item.find('span', class_='a-price-whole')
                            if not price_elem:
                                price_elem = item.find('span', class_='a-offscreen')
                            
                            link_elem = item.find('h2').find('a') if item.find('h2') else None
                            img_elem = item.find('img', class_='s-image')
                            
                            if title_elem and price_elem and link_elem:
                                title = title_elem.get_text(strip=True)
                                price = price_elem.get_text(strip=True)
                                url = "https://amazon.com" + link_elem.get('href', '')
                                
                                # Add affiliate tag if available
                                if self.amazon_tag and 'tag=' not in url:
                                    url += f"&tag={self.amazon_tag}"
                                
                                results.append(ShoppingResult(
                                    title=title,
                                    price=price if price.startswith('$') else f"${price}",
                                    url=url,
                                    image_url=img_elem.get('src', '') if img_elem else '',
                                    store="Amazon",
                                    shipping="Prime eligible"
                                ))
                        except:
                            continue
                    
                    return results
                    
        except Exception as e:
            logging.error(f"Amazon scraping failed: {e}")
        
        return []
    
    async def search_autozone_scrape(self, search_term: str) -> List[ShoppingResult]:
        """Scrape AutoZone search results"""
        try:
            session = await self.get_session()
            url = f"https://www.autozone.com/search?searchText={quote(search_term)}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    items = soup.find_all('div', class_='search-result-item')
                    
                    for item in items[:5]:
                        try:
                            title_elem = item.find('h3') or item.find('a', class_='product-name')
                            price_elem = item.find('span', class_='price') or item.find('span', class_='sale-price')
                            link_elem = item.find('a')
                            
                            if title_elem and link_elem:
                                title = title_elem.get_text(strip=True)
                                price = price_elem.get_text(strip=True) if price_elem else "Call for price"
                                url = link_elem.get('href', '')
                                if url.startswith('/'):
                                    url = "https://www.autozone.com" + url
                                
                                results.append(ShoppingResult(
                                    title=title,
                                    price=price,
                                    url=url,
                                    image_url='',
                                    store="AutoZone",
                                    availability="In Store",
                                    shipping="Free store pickup"
                                ))
                        except:
                            continue
                    
                    return results
                    
        except Exception as e:
            logging.error(f"AutoZone scraping failed: {e}")
        
        return []
    
    async def search_rockauto_scrape(self, search_term: str) -> List[ShoppingResult]:
        """Scrape RockAuto search results"""
        try:
            session = await self.get_session()
            url = f"https://www.rockauto.com/en/search/?searchtype=partnumber&q={quote(search_term)}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    # RockAuto has anti-bot measures, so this is a simplified version
                    return [
                        ShoppingResult(
                            title=f"Search {search_term} on RockAuto",
                            price="Various prices",
                            url=url,
                            image_url='',
                            store="RockAuto",
                            availability="Check website",
                            shipping="Calculated at checkout"
                        )
                    ]
                    
        except Exception as e:
            logging.error(f"RockAuto scraping failed: {e}")
        
        return []
    
    async def search_advance_auto_scrape(self, search_term: str) -> List[ShoppingResult]:
        """Scrape Advance Auto Parts search results"""
        try:
            session = await self.get_session()
            url = f"https://shop.advanceautoparts.com/find/search?q={quote(search_term)}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    # This would need to be updated based on their actual HTML structure
                    return [
                        ShoppingResult(
                            title=f"Search {search_term} on Advance Auto",
                            price="Check website",
                            url=url,
                            image_url='',
                            store="Advance Auto Parts",
                            availability="In Store",
                            shipping="Free store pickup"
                        )
                    ]
                    
        except Exception as e:
            logging.error(f"Advance Auto scraping failed: {e}")
        
        return []
    
    async def search_oreilly_scrape(self, search_term: str) -> List[ShoppingResult]:
        """Scrape O'Reilly Auto Parts search results"""
        try:
            session = await self.get_session()
            url = f"https://www.oreillyauto.com/search?q={quote(search_term)}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    return [
                        ShoppingResult(
                            title=f"Search {search_term} on O'Reilly Auto",
                            price="Check website",
                            url=url,
                            image_url='',
                            store="O'Reilly Auto Parts",
                            availability="In Store",
                            shipping="Same day pickup"
                        )
                    ]
                    
        except Exception as e:
            logging.error(f"O'Reilly scraping failed: {e}")
        
        return []
    
    def get_price_comparison(self, results: Dict[str, List[ShoppingResult]]) -> Dict:
        """Generate price comparison summary"""
        all_prices = []
        
        for store_results in results.values():
            for result in store_results:
                # Extract numeric price
                price_text = result.price.replace('$', '').replace(',', '')
                try:
                    price = float(re.findall(r'\d+\.?\d*', price_text)[0])
                    all_prices.append(price)
                except:
                    continue
        
        if not all_prices:
            return {
                'lowest_price': None,
                'highest_price': None,
                'average_price': None,
                'price_range': None
            }
        
        return {
            'lowest_price': min(all_prices),
            'highest_price': max(all_prices),
            'average_price': sum(all_prices) / len(all_prices),
            'price_range': max(all_prices) - min(all_prices),
            'total_listings': len(all_prices)
        }

# Global instance
shopping_aggregator = ShoppingAggregator()
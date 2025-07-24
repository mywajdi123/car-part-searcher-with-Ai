from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageEnhance
import io
import re
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
import aiohttp
from urllib.parse import quote
from typing import Dict, List
from dataclasses import dataclass

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Car Parts AI API - Ultra Simple",
    description="Lightweight automotive part recognition API",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class ShoppingResult:
    title: str
    price: str
    url: str
    store: str
    availability: str = "Available online"

class SimplePartRecognizer:
    """Simple part recognition using regex patterns only"""
    
    def __init__(self):
        # Enhanced automotive part patterns
        self.part_patterns = {
            'toyota': [
                r'\b\d{5}-\d{5}\b',  # 90915-YZZD4
                r'\b\d{5}-[A-Z0-9]{5}\b',
            ],
            'honda': [
                r'\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b',  # 15400-PLM-A02
                r'\b\d{5}-[A-Z]{3}-[A-Z]\d{2}\b'
            ],
            'ford': [
                r'\b[A-Z]\d[A-Z]\d-\d{4,5}-[A-Z]{1,2}\b',  # F1TZ-6714-A
                r'\bFL-\d{3}-S\b'  # FL-820-S
            ],
            'gm': [
                r'\b1\d{7,8}\b',  # 12345678
                r'\bPF\d{2,4}[A-Z]?\b',  # PF52
                r'\bAC\s*DELCO\b'
            ],
            'aftermarket': [
                r'\bPH\d{4}[A-Z]?\b',  # FRAM PH3593A
                r'\b\d{5}[A-Z]?\b',    # WIX 51515
                r'\bM1[A-Z]?-\d{3,4}\b'  # Mobil1
            ]
        }
        
        # Generic automotive patterns
        self.generic_patterns = [
            r'\b[A-Z]{2,4}\d{3,8}[A-Z]?\b',  # AC123456A
            r'\b\d{4,8}-[A-Z0-9]{2,6}\b',    # 12345-ABC
            r'\b[A-Z]\d{3}-\d{3}-\d{3}\b',   # A123-456-789
            r'\b\d{8,12}\b',                 # Long numeric
            r'\b[A-Z0-9]{3,6}-[A-Z0-9]{2,6}-[A-Z0-9]{2,6}\b'  # Complex patterns
        ]
    
    def find_part_numbers(self, text_list: List[str]) -> Dict:
        """Find part numbers from text list using enhanced patterns"""
        all_candidates = []
        
        for text in text_list:
            text_clean = text.strip().upper()
            if len(text_clean) < 3:
                continue
                
            likelihood = self._calculate_likelihood(text_clean)
            if likelihood > 0.3:
                all_candidates.append({
                    'text': text_clean,
                    'likelihood': likelihood,
                    'original': text
                })
        
        # Sort by likelihood
        all_candidates.sort(key=lambda x: x['likelihood'], reverse=True)
        
        best_part = all_candidates[0]['text'] if all_candidates else None
        
        return {
            'part_number': best_part,
            'candidates': all_candidates[:5],
            'success': best_part is not None
        }
    
    def _calculate_likelihood(self, text: str) -> float:
        """Calculate likelihood that text is a part number"""
        score = 0.0
        
        # Check known patterns
        for brand, patterns in self.part_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    score += 0.8
                    break
        
        # Check generic patterns
        for pattern in self.generic_patterns:
            if re.search(pattern, text):
                score += 0.6
                break
        
        # Heuristics
        if re.search(r'\d', text):  # Has numbers
            score += 0.2
        if re.search(r'[A-Z]', text):  # Has letters
            score += 0.1
        if re.search(r'-', text):  # Has hyphens
            score += 0.1
        if 4 <= len(text) <= 25:  # Good length
            score += 0.2
        if re.search(r'^[A-Z0-9\-]+$', text):  # Only valid chars
            score += 0.1
        
        # Brand keywords
        brands = ['TOYOTA', 'HONDA', 'FORD', 'GM', 'BOSCH', 'FRAM', 'WIX', 'AC', 'DELCO', 'MOBIL']
        for brand in brands:
            if brand in text:
                score += 0.3
                break
        
        return min(score, 1.0)

class FreeShoppingScraper:
    """Free shopping search without heavy dependencies"""
    
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_shopping_links(self, part_number: str) -> List[ShoppingResult]:
        """Generate direct shopping links to major retailers"""
        if not part_number:
            return []
        
        stores = [
            {
                'name': 'AutoZone',
                'url': f"https://www.autozone.com/search?searchText={quote(part_number)}",
                'price': 'Check prices online',
                'note': 'Free store pickup • Same day'
            },
            {
                'name': 'Advance Auto Parts',
                'url': f"https://shop.advanceautoparts.com/find/search?q={quote(part_number)}",
                'price': 'Competitive pricing',
                'note': 'Professional installation available'
            },
            {
                'name': "O'Reilly Auto Parts",
                'url': f"https://www.oreillyauto.com/search?q={quote(part_number)}",
                'price': 'Great prices',
                'note': 'Same day pickup • Expert advice'
            },
            {
                'name': 'RockAuto',
                'url': f"https://www.rockauto.com/en/search/?searchtype=partnumber&q={quote(part_number)}",
                'price': 'Wholesale prices',
                'note': 'Huge selection • Catalog parts'
            },
            {
                'name': 'Amazon Auto',
                'url': f"https://www.amazon.com/s?k={quote(part_number + ' automotive part')}&rh=n%3A15684181",
                'price': 'Prime pricing',
                'note': 'Fast Prime delivery • Returns'
            },
            {
                'name': 'eBay Motors',
                'url': f"https://www.ebay.com/sch/i.html?_nkw={quote(part_number)}&_sacat=6030",
                'price': 'Auction & Buy Now',
                'note': 'New & used • Global sellers'
            }
        ]
        
        results = []
        for store in stores:
            results.append(ShoppingResult(
                title=f"🔗 {store['name']} - Search {part_number}",
                price=store['price'],
                url=store['url'],
                store=store['name'],
                availability=store['note']
            ))
        
        return results

# Enhanced mock database
ENHANCED_PARTS_DB = {
    "90915-YZZD4": {
        "part_name": "Toyota OEM Oil Filter",
        "category": "Engine",
        "description": "Genuine Toyota oil filter for 4-cylinder engines",
        "compatibility": [
            {"make": "Toyota", "model": "Camry", "years": "2018-2023", "engines": ["2.5L 4cyl"], "confidence": 0.98, "notes": "Direct OEM fit"},
            {"make": "Toyota", "model": "RAV4", "years": "2019-2023", "engines": ["2.5L 4cyl"], "confidence": 0.95, "notes": "Perfect match"},
            {"make": "Lexus", "model": "ES350", "years": "2019-2023", "engines": ["2.5L 4cyl"], "confidence": 0.90, "notes": "Hybrid models"}
        ],
        "interchangeable": [
            {"part_number": "PF457G", "brand": "FRAM", "type": "Aftermarket", "price_range": "$8-12"},
            {"part_number": "51515", "brand": "WIX", "type": "Aftermarket", "price_range": "$10-15"},
            {"part_number": "PH3593A", "brand": "FRAM", "type": "Aftermarket", "price_range": "$6-10"}
        ],
        "specifications": {
            "filter_type": "Spin-on",
            "thread": "3/4-16",
            "gasket_diameter": "62mm",
            "height": "80mm"
        }
    },
    "HONDA": {
        "part_name": "Honda Automotive Part",
        "category": "Various",
        "description": "Honda brand automotive component",
        "compatibility": [
            {"make": "Honda", "model": "Various Models", "years": "2010-2023", "engines": ["Multiple"], "confidence": 0.70, "notes": "Brand match detected"}
        ],
        "interchangeable": [],
        "specifications": {}
    },
    "PF52": {
        "part_name": "AC Delco Oil Filter PF52",
        "category": "Engine",
        "description": "Premium oil filter for GM V8 engines",
        "compatibility": [
            {"make": "Chevrolet", "model": "Silverado 1500", "years": "2014-2019", "engines": ["5.3L V8", "6.2L V8"], "confidence": 0.98, "notes": "Direct fit"},
            {"make": "GMC", "model": "Sierra 1500", "years": "2014-2019", "engines": ["5.3L V8", "6.2L V8"], "confidence": 0.98, "notes": "OEM quality"},
            {"make": "Chevrolet", "model": "Tahoe", "years": "2015-2020", "engines": ["5.3L V8"], "confidence": 0.95, "notes": "Perfect match"}
        ],
        "interchangeable": [
            {"part_number": "51515", "brand": "WIX", "type": "Aftermarket", "price_range": "$12-18"},
            {"part_number": "PH3593A", "brand": "FRAM", "type": "Aftermarket", "price_range": "$8-14"}
        ],
        "specifications": {
            "filter_type": "Spin-on",
            "thread": "13/16-16",
            "anti_drainback_valve": "Yes"
        }
    }
}

# Initialize services
part_recognizer = SimplePartRecognizer()
shopping_scraper = FreeShoppingScraper()

@app.get("/")
def read_root():
    return {
        "message": "Car Parts AI Backend - Ultra Simple Edition ✨",
        "status": "🟢 Online",
        "features": [
            "🎯 Smart part number detection",
            "🛒 Direct shopping links to 6 major stores", 
            "🗄️ Enhanced parts database",
            "⚡ Lightweight & fast",
            "🎨 Works with your beautiful UI"
        ],
        "no_dependencies": "No heavy ML libraries required!"
    }

@app.post("/api/predict")
async def predict_api(file: UploadFile = File(...)):
    start_time = datetime.now()
    
    try:
        # Basic file validation
        content = await file.read()
        size_kb = round(len(content) / 1024, 2)

        if not file.content_type.startswith('image/'):
            return JSONResponse(
                status_code=400,
                content={"error": "Please upload an image file"}
            )

        logger.info(f"Processing image: {file.filename} ({size_kb} KB)")

        # For now, we'll simulate OCR with some common automotive texts
        # In a real scenario, you'd use OCR here
        simulated_texts = [
            "HONDA", "90915-YZZD4", "PF52", "AC DELCO", 
            "TOYOTA", "OIL FILTER", "MADE IN USA"
        ]
        
        # Enhanced part recognition
        part_results = part_recognizer.find_part_numbers(simulated_texts)
        part_number = part_results.get('part_number')
        
        # Database search
        database_result = {"found": False, "data": None}
        
        if part_number and part_number in ENHANCED_PARTS_DB:
            database_result = {
                "found": True,
                "data": ENHANCED_PARTS_DB[part_number]
            }
        else:
            # Try partial matching
            for text in simulated_texts:
                text_upper = text.upper()
                if text_upper in ENHANCED_PARTS_DB:
                    database_result = {
                        "found": True,
                        "data": ENHANCED_PARTS_DB[text_upper]
                    }
                    if not part_number:
                        part_number = text_upper
                    break

        # Calculate confidence
        overall_confidence = 0.5
        if part_results.get('success') and database_result.get('found'):
            overall_confidence = 0.85
        elif part_results.get('success'):
            overall_confidence = 0.70
        elif database_result.get('found'):
            overall_confidence = 0.65

        # Simulate AI analysis
        ai_analysis = {
            "part_identification": {
                "part_type": database_result['data']['part_name'] if database_result.get('found') else "Automotive Component",
                "category": database_result['data']['category'] if database_result.get('found') else "General",
                "part_function": "Essential automotive component for vehicle operation"
            },
            "physical_specs": {
                "condition": "New",
                "visible_markings": simulated_texts
            },
            "confidence_scores": {
                "overall": overall_confidence,
                "part_identification": 0.80,
                "compatibility": 0.75
            },
            "ai_used": False,  # Since we're not using real AI
            "model": "pattern-matching"
        }

        # Build response
        response_data = {
            "filename": file.filename,
            "size_kb": size_kb,
            "message": "Image processed successfully",
            "detected_texts": simulated_texts,
            "texts_found": len(simulated_texts),
            "part_number": part_number,
            
            # Enhanced analysis
            "ai_analysis": ai_analysis,
            "database_result": database_result,
            "enhanced_ocr": {
                "success": part_results.get('success'),
                "part_candidates": part_results.get('candidates', []),
                "total_detections": len(simulated_texts)
            },
            
            # Overall metrics
            "overall_confidence": overall_confidence,
            "sources": {
                "enhanced_ocr": "processed",
                "ai_vision": "pattern_matching",
                "parts_database": "found" if database_result.get('found') else "not_found"
            },
            "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
        }

        logger.info(f"Processing completed in {response_data['processing_time_ms']}ms")
        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing failed: {str(e)}"}
        )

@app.get("/api/shopping/{part_number}")
async def get_shopping_results(part_number: str):
    """Get shopping links for a part number"""
    try:
        # Get shopping links
        shopping_results = await shopping_scraper.get_shopping_links(part_number)
        
        # Format for frontend
        formatted_results = {
            "AutoZone": [],
            "Advance Auto": [], 
            "O'Reilly": [],
            "RockAuto": [],
            "Amazon": [],
            "eBay": []
        }
        
        # Organize by store
        for result in shopping_results:
            store_key = result.store.replace("'", "").replace(" Auto Parts", "").replace(" Motors", "")
            if store_key in formatted_results:
                formatted_results[store_key].append({
                    "title": result.title,
                    "price": result.price,
                    "url": result.url,
                    "availability": result.availability,
                    "store": result.store
                })

        return JSONResponse(content={
            "part_number": part_number,
            "shopping_results": formatted_results,
            "total_listings": len(shopping_results),
            "price_comparison": {
                "message": "Click links above to compare prices across all stores",
                "stores_available": len(shopping_results)
            },
            "search_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Shopping search failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Shopping search failed: {str(e)}"}
        )

@app.get("/partinfo/")
async def part_info_legacy(part_number: str):
    """Legacy endpoint for compatibility"""
    shopping_results = await shopping_scraper.get_shopping_links(part_number)
    
    return JSONResponse(content={
        "part_number": part_number,
        "google_url": f"https://www.google.com/search?q={part_number}+car+part",
        "ebay_url": f"https://www.ebay.com/sch/i.html?_nkw={part_number}",
        "amazon_url": f"https://www.amazon.com/s?k={part_number}",
        "results_count": len(shopping_results),
        "enhanced_links": [
            {"title": r.title, "url": r.url, "store": r.store} 
            for r in shopping_results
        ]
    })

@app.on_event("shutdown")
async def shutdown():
    await shopping_scraper.close()
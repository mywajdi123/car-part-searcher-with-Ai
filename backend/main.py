from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import easyocr
from PIL import Image
import numpy as np
import io
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Enhanced imports
from enhanced_ocr import enhanced_ocr
from cnn_model import cnn_recognizer
from shopping_integration import shopping_aggregator
from parts_database import parts_db
from car_ai import CarPartAI

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Car Parts AI API",
    description="Advanced automotive part recognition and shopping API",
    version="2.0.0"
)

# Initialize services
car_ai = CarPartAI()

# Enhanced CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def legacy_extract_part_numbers(texts):
    """Legacy part number extraction for fallback"""
    part_patterns = [
        r'^[A-Z0-9]{3,6}-[A-Z0-9]{2,4}-[A-Z0-9]{2,6}$',
        r'^[A-Z0-9]{4,10}-[A-Z0-9]{3,6}$',
        r'^[A-Z0-9]{6,12}$',
        r'^[0-9]{8,12}$',
        r'^[A-Z]{2,4}[0-9]{4,8}[A-Z]?$', 
        r'^[0-9]{2,4}-[0-9]{3,6}-[0-9]{2,4}$',
    ]
    
    potential_parts = []
    
    for text in texts:
        cleaned = re.sub(r'[^\w-]', '', text.upper())
        for pattern in part_patterns:
            if re.match(pattern, cleaned) and len(cleaned) >= 5:
                potential_parts.append({
                    'original': text,
                    'cleaned': cleaned,
                    'confidence': len(cleaned)
                })
    
    if potential_parts:
        best_match = max(potential_parts, key=lambda x: x['confidence'])
        return best_match['cleaned']
    
    return None

@app.get("/")
def read_root():
    return {
        "message": "Car Parts AI Backend v2.0 is running!",
        "features": [
            "Enhanced OCR with multiple engines",
            "CNN-based visual part recognition", 
            "Real-time shopping integration",
            "Advanced parts database",
            "OpenAI Vision API integration"
        ],
        "endpoints": [
            "/api/predict - Main part analysis endpoint",
            "/api/shopping/{part_number} - Get shopping results",
            "/api/model-info - Get model information",
            "/partinfo/ - Legacy part info endpoint"
        ]
    }

@app.get("/api/model-info")
async def get_model_info():
    """Get information about loaded models and services"""
    return {
        "cnn_model": cnn_recognizer.get_model_info(),
        "enhanced_ocr": {
            "available": True,
            "engines": ["EasyOCR", "Tesseract", "Multiple preprocessing variants"]
        },
        "openai_vision": {
            "available": car_ai.has_openai,
            "model": "gpt-4o-mini"
        },
        "shopping_integration": {
            "stores": ["eBay", "Amazon", "AutoZone", "RockAuto", "Advance Auto", "O'Reilly"],
            "real_apis": ["eBay API"],
            "scraping": ["Amazon", "AutoZone", "Others"]
        },
        "parts_database": {
            "available": True,
            "entries": len(parts_db.mock_database)
        }
    }

@app.post("/api/predict")
async def predict_api(file: UploadFile = File(...)):
    """Enhanced prediction endpoint with all features"""
    return await process_image_enhanced(file)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    """Legacy endpoint for backward compatibility"""
    return await process_image_enhanced(file)

async def process_image_enhanced(file: UploadFile):
    """Enhanced image processing with all new features"""
    start_time = datetime.now()
    
    try:
        # Read and validate image
        content = await file.read()
        size_kb = round(len(content) / 1024, 2)

        if not file.content_type.startswith('image/'):
            return JSONResponse(
                status_code=400,
                content={"error": "Please upload an image file"}
            )

        # Convert to OpenCV format
        image = Image.open(io.BytesIO(content)).convert("RGB")
        np_img = np.array(image)
        cv_img = np_img[:, :, ::-1].copy()  # RGB to BGR for OpenCV

        logger.info(f"Processing image: {file.filename} ({size_kb} KB)")

        # 1. Enhanced OCR Processing
        logger.info("Starting enhanced OCR processing...")
        enhanced_ocr_results = enhanced_ocr.extract_part_numbers(cv_img)
        
        # 2. Legacy OCR for fallback
        try:
            reader = easyocr.Reader(['en'], gpu=False)
            legacy_result = reader.readtext(np_img)
            legacy_texts = [text for (_, text, confidence) in legacy_result if confidence > 0.5]
        except Exception as e:
            logger.warning(f"Legacy OCR failed: {e}")
            legacy_texts = []

        # 3. CNN Visual Recognition
        logger.info("Starting CNN visual recognition...")
        cnn_results = cnn_recognizer.predict_part(cv_img)

        # 4. OpenAI Vision Analysis
        logger.info("Starting OpenAI vision analysis...")
        ai_analysis = await car_ai.identify_car_part(content, enhanced_ocr_results.get('all_texts', []))

        # 5. Determine best part number
        part_number = None
        part_confidence = 0.0
        
        # Priority: Enhanced OCR > Legacy OCR > AI extracted
        if enhanced_ocr_results.get('part_number'):
            part_number = enhanced_ocr_results['part_number']
            part_confidence = 0.9
        elif legacy_texts:
            legacy_part = legacy_extract_part_numbers(legacy_texts)
            if legacy_part:
                part_number = legacy_part
                part_confidence = 0.7
        
        # 6. Database search
        logger.info("Searching parts database...")
        database_result = None
        if part_number:
            database_result = await parts_db.search_part_by_number(part_number)
        elif enhanced_ocr_results.get('all_texts'):
            # Try searching with detected texts
            for text in enhanced_ocr_results['all_texts'][:3]:  # Try top 3 texts
                db_result = await parts_db.search_part_by_number(text)
                if db_result:
                    database_result = db_result
                    if not part_number:
                        part_number = text
                        part_confidence = 0.6
                    break

        # 7. Combine all analysis results
        combined_analysis = {
            # Basic info
            "filename": file.filename,
            "size_kb": size_kb,
            "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
            
            # OCR Results
            "detected_texts": enhanced_ocr_results.get('all_texts', legacy_texts),
            "texts_found": len(enhanced_ocr_results.get('all_texts', legacy_texts)),
            "part_number": part_number,
            "part_number_confidence": part_confidence,
            
            # Enhanced OCR details
            "enhanced_ocr": {
                "success": enhanced_ocr_results.get('success', False),
                "part_candidates": enhanced_ocr_results.get('part_candidates', []),
                "total_detections": enhanced_ocr_results.get('total_detections', 0)
            },
            
            # CNN Results
            "cnn_analysis": cnn_results,
            
            # OpenAI Vision Results
            "ai_analysis": ai_analysis,
            
            # Database Results
            "database_result": {
                "found": database_result is not None,
                "data": {
                    "part_name": database_result.part_name if database_result else None,
                    "category": database_result.category if database_result else None,
                    "compatibility": [
                        {
                            "make": comp.make,
                            "model": comp.model, 
                            "years": comp.years,
                            "engines": comp.engines,
                            "confidence": comp.confidence,
                            "notes": comp.notes
                        } for comp in database_result.compatibility
                    ] if database_result else [],
                    "interchangeable": [
                        {
                            "part_number": part.part_number,
                            "brand": part.brand,
                            "type": part.type,
                            "price_range": part.price_range
                        } for part in database_result.interchangeable  
                    ] if database_result else [],
                    "specifications": database_result.specifications if database_result else {}
                } if database_result else None
            },
            
            # Overall confidence calculation
            "overall_confidence": calculate_overall_confidence(
                enhanced_ocr_results, cnn_results, ai_analysis, database_result
            ),
            
            # Data sources used
            "sources": {
                "enhanced_ocr": "processed" if enhanced_ocr_results.get('success') else "failed",
                "cnn_vision": "processed" if cnn_results.get('success') else "failed", 
                "ai_vision": "openai_gpt4o" if ai_analysis.get('ai_used') else "rule_based",
                "parts_database": database_result.source if database_result else "not_found"
            },
            
            # Performance metrics
            "performance": {
                "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                "engines_used": sum([
                    1 if enhanced_ocr_results.get('success') else 0,
                    1 if cnn_results.get('success') else 0,
                    1 if ai_analysis.get('ai_used') else 0,
                    1 if database_result else 0
                ])
            }
        }

        logger.info(f"Image processing completed in {combined_analysis['processing_time_ms']}ms")
        return JSONResponse(content=combined_analysis)

    except Exception as e:
        logger.error(f"Image processing failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Processing failed: {str(e)}",
                "processing_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
        )

def calculate_overall_confidence(enhanced_ocr, cnn_results, ai_analysis, database_result):
    """Calculate overall confidence score from all sources"""
    scores = []
    
    # Enhanced OCR confidence
    if enhanced_ocr.get('success') and enhanced_ocr.get('part_candidates'):
        ocr_score = enhanced_ocr['part_candidates'][0].get('combined_score', 0)
        scores.append(ocr_score * 0.3)  # 30% weight
    
    # CNN confidence  
    if cnn_results.get('success'):
        cnn_score = cnn_results.get('confidence', 0)
        scores.append(cnn_score * 0.25)  # 25% weight
    
    # AI analysis confidence
    ai_confidence = ai_analysis.get('confidence_scores', {}).get('overall', 
                     ai_analysis.get('confidence', 0.5))
    scores.append(ai_confidence * 0.25)  # 25% weight
    
    # Database match confidence
    if database_result:
        db_score = database_result.confidence
        scores.append(db_score * 0.2)  # 20% weight
    
    return sum(scores) if scores else 0.5

@app.get("/api/shopping/{part_number}")
async def get_shopping_results(part_number: str, part_name: str = ""):
    """Get shopping results for a specific part number"""
    try:
        logger.info(f"Getting shopping results for: {part_number}")
        
        # Search all stores
        shopping_results = await shopping_aggregator.search_all_stores(part_number, part_name)
        
        # Get price comparison
        price_comparison = shopping_aggregator.get_price_comparison(shopping_results)
        
        # Format response
        formatted_results = {}
        total_listings = 0
        
        for store, results in shopping_results.items():
            formatted_store_results = []
            for result in results:
                formatted_store_results.append({
                    "title": result.title,
                    "price": result.price,
                    "url": result.url,
                    "image_url": result.image_url,
                    "rating": result.rating,
                    "reviews": result.reviews,
                    "availability": result.availability,
                    "shipping": result.shipping,
                    "brand": result.brand
                })
            
            formatted_results[store] = formatted_store_results
            total_listings += len(formatted_store_results)
        
        return JSONResponse(content={
            "part_number": part_number,
            "shopping_results": formatted_results,
            "price_comparison": price_comparison,
            "total_listings": total_listings,
            "stores_searched": list(shopping_results.keys()),
            "search_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Shopping search failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Shopping search failed: {str(e)}"}
        )

@app.get("/partinfo/")
async def part_info(part_number: str):
    """Legacy part info endpoint with enhanced shopping integration"""
    try:
        # Get shopping results
        shopping_results = await shopping_aggregator.search_all_stores(part_number)
        
        # Format for legacy compatibility
        google_url = f"https://www.google.com/search?q={part_number}+car+part"
        ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={part_number}"
        amazon_url = f"https://www.amazon.com/s?k={part_number}"
        
        # Extract eBay results for legacy format
        ebay_results = []
        if 'eBay' in shopping_results:
            for result in shopping_results['eBay'][:5]:
                ebay_results.append({
                    "title": result.title,
                    "price": result.price,
                    "image_url": result.image_url,
                    "listing_url": result.url
                })

        return JSONResponse(content={
            "part_number": part_number,
            "google_url": google_url,
            "ebay_url": ebay_url,
            "amazon_url": amazon_url,
            "ebay_results": ebay_results,
            "results_count": len(ebay_results),
            "enhanced_shopping": shopping_results,
            "error": None
        })

    except Exception as e:
        logger.error(f"Part info lookup failed: {e}")
        return JSONResponse(content={
            "part_number": part_number,
            "google_url": f"https://www.google.com/search?q={part_number}+car+part",
            "ebay_url": f"https://www.ebay.com/sch/i.html?_nkw={part_number}",
            "amazon_url": f"https://www.amazon.com/s?k={part_number}",
            "ebay_results": [],
            "results_count": 0,
            "error": f"Lookup failed: {str(e)}"
        })

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Car Parts AI Backend v2.0...")
    logger.info(f"OpenAI Vision: {'Available' if car_ai.has_openai else 'Not available'}")
    logger.info(f"CNN Model: {'Loaded' if cnn_recognizer.model else 'Not loaded'}")
    logger.info("All services initialized successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("Shutting down services...")
    await parts_db.close()
    await shopping_aggregator.close()
    logger.info("Shutdown complete!")
# car_ai.py - Add this new file to your backend
import base64
import httpx
import json
from typing import Optional, Dict, Any

class CarPartAI:
    """AI-powered car part and vehicle identification"""
    
    def __init__(self):
        # You'll need to get API keys for these services
        self.openai_api_key = None  # Add your OpenAI API key here
        self.vision_api_url = "https://api.openai.com/v1/chat/completions"
    
    async def identify_car_part(self, image_bytes: bytes, detected_texts: list) -> Dict[str, Any]:
        """Use AI to identify car parts from image"""
        
        # Convert image to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create the prompt
        prompt = f"""
        Analyze this car part image and provide:
        1. Part type (e.g., brake pad, air filter, spark plug, etc.)
        2. Likely car make/model compatibility
        3. Part category (engine, brakes, electrical, etc.)
        4. Estimated year range
        
        Detected text from OCR: {', '.join(detected_texts)}
        
        Respond in JSON format:
        {{
            "part_type": "specific part name",
            "category": "part category",
            "likely_makes": ["make1", "make2"],
            "year_range": "2010-2020",
            "confidence": 0.85,
            "description": "detailed description"
        }}
        """
        
        if not self.openai_api_key:
            # Fallback to rule-based detection
            return self._fallback_part_detection(detected_texts)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.vision_api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['choices'][0]['message']['content']
                    
                    # Try to parse JSON response
                    try:
                        return json.loads(ai_response)
                    except:
                        # If JSON parsing fails, create structured response
                        return {
                            "part_type": "Unknown",
                            "category": "General",
                            "likely_makes": ["Universal"],
                            "year_range": "Various",
                            "confidence": 0.3,
                            "description": ai_response,
                            "ai_used": True
                        }
                        
        except Exception as e:
            print(f"AI detection failed: {e}")
            
        # Fallback to rule-based detection
        return self._fallback_part_detection(detected_texts)
    
    def _fallback_part_detection(self, detected_texts: list) -> Dict[str, Any]:
        """Rule-based car part detection when AI is unavailable"""
        
        # Common car part keywords
        part_keywords = {
            "brake": {"category": "Braking System", "type": "Brake Component"},
            "filter": {"category": "Filtration", "type": "Filter"},
            "spark": {"category": "Ignition", "type": "Spark Plug"},
            "oil": {"category": "Engine", "type": "Oil Component"},
            "belt": {"category": "Engine", "type": "Belt"},
            "hose": {"category": "Cooling/Fuel", "type": "Hose"},
            "sensor": {"category": "Electrical", "type": "Sensor"},
            "pump": {"category": "Fuel/Cooling", "type": "Pump"},
            "valve": {"category": "Engine", "type": "Valve"},
            "gasket": {"category": "Engine", "type": "Gasket"},
        }
        
        # Car make patterns
        make_patterns = {
            "honda": ["honda", "acura"],
            "toyota": ["toyota", "lexus", "scion"],
            "ford": ["ford", "lincoln", "mercury"],
            "gm": ["chevrolet", "chevy", "gmc", "cadillac", "buick"],
            "bmw": ["bmw", "mini"],
            "vw": ["volkswagen", "vw", "audi", "porsche"],
            "nissan": ["nissan", "infiniti"],
            "hyundai": ["hyundai", "kia", "genesis"],
        }
        
        detected_text = " ".join(detected_texts).lower()
        
        # Detect part type
        part_type = "Unknown Part"
        category = "General"
        
        for keyword, info in part_keywords.items():
            if keyword in detected_text:
                part_type = info["type"]
                category = info["category"]
                break
        
        # Detect likely makes
        likely_makes = []
        for make_group, variants in make_patterns.items():
            for variant in variants:
                if variant in detected_text:
                    likely_makes.append(make_group.title())
                    break
        
        if not likely_makes:
            likely_makes = ["Universal"]
        
        return {
            "part_type": part_type,
            "category": category,
            "likely_makes": likely_makes,
            "year_range": "Various",
            "confidence": 0.6 if part_type != "Unknown Part" else 0.3,
            "description": f"Detected {part_type.lower()} based on text analysis",
            "ai_used": False
        }
# car_ai.py - Enhanced with OpenAI Vision API
import base64
import os
import json
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class CarPartAI:
    """AI-powered car part and vehicle identification using OpenAI Vision"""
    
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.has_openai = True
            print("✅ OpenAI Vision API initialized successfully")
        else:
            self.client = None
            self.has_openai = False
            print("⚠️  OpenAI API key not found - using fallback detection")
    
    async def identify_car_part(self, image_bytes: bytes, detected_texts: list) -> Dict[str, Any]:
        """Use AI to identify car parts from image"""
        
        if self.has_openai:
            try:
                return await self._openai_vision_analysis(image_bytes, detected_texts)
            except Exception as e:
                print(f"OpenAI Vision failed: {e}")
                print("Falling back to rule-based detection...")
        
        # Fallback to rule-based detection
        return self._fallback_part_detection(detected_texts)
    
    async def _openai_vision_analysis(self, image_bytes: bytes, detected_texts: list) -> Dict[str, Any]:
        """Analyze car part using OpenAI Vision API"""
        
        # Convert image to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create the prompt
        prompt = f"""
        You are an expert automotive technician. Analyze this car part image and provide detailed information.

        OCR detected these texts: {', '.join(detected_texts) if detected_texts else 'None'}

        Please identify:
        1. Specific part name (e.g. "Brake Pad", "Air Filter", "Spark Plug")
        2. Part category (Engine, Brakes, Electrical, Suspension, etc.)
        3. Likely compatible car makes/brands 
        4. Estimated year range of compatibility
        5. Brief description of the part's function
        6. Any visible part numbers or manufacturer info
        7. Condition assessment (New, Used, Worn, etc.)

        Respond ONLY with valid JSON in this exact format:
        {{
            "part_type": "specific part name",
            "category": "part category", 
            "likely_makes": ["make1", "make2", "make3"],
            "year_range": "2010-2020",
            "description": "detailed description of part and function",
            "part_numbers": ["any visible part numbers"],
            "manufacturer": "detected manufacturer if visible",
            "condition": "New/Used/Worn/Unknown",
            "confidence": 0.85,
            "compatibility_notes": "specific compatibility information"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # High detail for better part recognition
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.3  # Lower temperature for more consistent results
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                # Remove any markdown formatting
                if ai_response.startswith("```json"):
                    ai_response = ai_response.split("```json")[1].split("```")[0].strip()
                elif ai_response.startswith("```"):
                    ai_response = ai_response.split("```")[1].strip()
                
                result = json.loads(ai_response)
                
                # Add metadata
                result["ai_used"] = True
                result["model"] = "gpt-4o"
                result["cost_estimate"] = "$0.0025"
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                print(f"Raw response: {ai_response}")
                
                # Create structured response from unstructured text
                return {
                    "part_type": "AI Analysis Available",
                    "category": "See Description", 
                    "likely_makes": ["Various"],
                    "year_range": "Various",
                    "description": ai_response,
                    "part_numbers": detected_texts,
                    "manufacturer": "Unknown",
                    "condition": "Unknown",
                    "confidence": 0.7,
                    "compatibility_notes": "See full AI analysis in description",
                    "ai_used": True,
                    "model": "gpt-4o",
                    "cost_estimate": "$0.0025"
                }
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise e
    
    def _fallback_part_detection(self, detected_texts: list) -> Dict[str, Any]:
        """Enhanced rule-based car part detection when AI is unavailable"""
        
        # Comprehensive car part keywords
        part_keywords = {
            # Engine Parts
            "filter": {"type": "Air/Oil Filter", "category": "Engine/Filtration"},
            "spark": {"type": "Spark Plug", "category": "Ignition"},
            "plug": {"type": "Spark Plug", "category": "Ignition"},
            "oil": {"type": "Oil Filter/Component", "category": "Engine"},
            "belt": {"type": "Drive Belt", "category": "Engine"},
            "timing": {"type": "Timing Component", "category": "Engine"},
            "gasket": {"type": "Gasket/Seal", "category": "Engine"},
            "valve": {"type": "Valve Component", "category": "Engine"},
            "piston": {"type": "Piston Component", "category": "Engine"},
            
            # Braking System
            "brake": {"type": "Brake Component", "category": "Braking System"},
            "pad": {"type": "Brake Pad", "category": "Braking System"},
            "rotor": {"type": "Brake Rotor", "category": "Braking System"},
            "caliper": {"type": "Brake Caliper", "category": "Braking System"},
            
            # Suspension
            "shock": {"type": "Shock Absorber", "category": "Suspension"},
            "strut": {"type": "Strut", "category": "Suspension"},
            "spring": {"type": "Spring", "category": "Suspension"},
            "bushing": {"type": "Bushing", "category": "Suspension"},
            
            # Electrical
            "sensor": {"type": "Sensor", "category": "Electrical"},
            "switch": {"type": "Switch", "category": "Electrical"},
            "relay": {"type": "Relay", "category": "Electrical"},
            "fuse": {"type": "Fuse", "category": "Electrical"},
            "bulb": {"type": "Light Bulb", "category": "Electrical"},
            
            # Fuel/Cooling
            "pump": {"type": "Pump", "category": "Fuel/Cooling"},
            "hose": {"type": "Hose", "category": "Cooling/Fuel"},
            "radiator": {"type": "Radiator", "category": "Cooling"},
            "thermostat": {"type": "Thermostat", "category": "Cooling"},
            "injector": {"type": "Fuel Injector", "category": "Fuel System"},
        }
        
        # Enhanced car make patterns
        make_patterns = {
            "Toyota": ["toyota", "lexus", "scion"],
            "Honda": ["honda", "acura"],
            "Ford": ["ford", "lincoln", "mercury", "motorcraft"],
            "GM": ["chevrolet", "chevy", "gmc", "cadillac", "buick", "pontiac", "oldsmobile"],
            "BMW": ["bmw", "mini"],
            "Mercedes": ["mercedes", "mb", "benz"],
            "VW Group": ["volkswagen", "vw", "audi", "porsche", "skoda", "seat"],
            "Nissan": ["nissan", "infiniti", "datsun"],
            "Hyundai": ["hyundai", "kia", "genesis"],
            "Chrysler": ["chrysler", "dodge", "jeep", "ram", "plymouth"],
            "Mazda": ["mazda"],
            "Subaru": ["subaru"],
            "Volvo": ["volvo"],
        }
        
        detected_text = " ".join(detected_texts).lower()
        
        # Detect part type with priority scoring
        part_matches = []
        for keyword, info in part_keywords.items():
            if keyword in detected_text:
                # Score based on keyword specificity and position
                score = len(keyword) + (10 if detected_text.startswith(keyword) else 0)
                part_matches.append((score, info))
        
        if part_matches:
            # Get the highest scoring match
            part_info = max(part_matches, key=lambda x: x[0])[1]
            part_type = part_info["type"]
            category = part_info["category"]
            confidence = 0.7
        else:
            part_type = "Unknown Automotive Part"
            category = "General"
            confidence = 0.3
        
        # Detect likely makes
        likely_makes = []
        for make_group, variants in make_patterns.items():
            for variant in variants:
                if variant in detected_text:
                    likely_makes.append(make_group)
                    break
        
        if not likely_makes:
            likely_makes = ["Universal/Various Makes"]
        
        # Try to extract part numbers from detected text
        part_numbers = []
        for text in detected_texts:
            # Look for alphanumeric patterns that could be part numbers
            cleaned = text.strip().upper()
            if len(cleaned) >= 5 and any(c.isdigit() for c in cleaned) and any(c.isalpha() for c in cleaned):
                part_numbers.append(cleaned)
        
        return {
            "part_type": part_type,
            "category": category,
            "likely_makes": likely_makes,
            "year_range": "Various (depends on specific part)",
            "description": f"Detected {part_type.lower()} based on text analysis. For accurate compatibility, verify part numbers and consult vehicle specifications.",
            "part_numbers": part_numbers,
            "manufacturer": "Unknown",
            "condition": "Unknown",
            "confidence": confidence,
            "compatibility_notes": "Rule-based detection - verify compatibility before purchase",
            "ai_used": False,
            "model": "rule-based",
            "cost_estimate": "Free"
        }
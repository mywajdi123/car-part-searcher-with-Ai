# parts_database.py - Simple automotive parts database
import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os

@dataclass
class PartCompatibility:
    make: str
    model: str
    years: str
    engines: List[str]
    confidence: float
    notes: str = ""

@dataclass
class InterchangeablePart:
    part_number: str
    brand: str
    type: str  # OEM, Aftermarket, etc.
    price_range: str = ""

@dataclass
class PartInfo:
    part_number: str
    part_name: str
    category: str
    description: str
    compatibility: List[PartCompatibility]
    interchangeable: List[InterchangeablePart]
    specifications: Dict[str, str]
    confidence: float
    source: str

class PartsDatabase:
    """Simple parts database with mock data"""
    
    def __init__(self):
        self.session = None
        self.mock_database = self._create_mock_database()
        
    def _create_mock_database(self) -> Dict[str, Dict]:
        """Create comprehensive mock database"""
        return {
            # Honda Alternator
            "31100-5AA-A02": {
                "part_name": "Honda OEM Alternator",
                "category": "Electrical",
                "description": "Genuine Honda alternator for Civic and Accord models",
                "compatibility": [
                    PartCompatibility("Honda", "Civic", "2016-2021", ["1.5L Turbo", "2.0L"], 0.95, "Direct fit"),
                    PartCompatibility("Honda", "Accord", "2018-2022", ["1.5L Turbo"], 0.90, "Check mounting"),
                    PartCompatibility("Acura", "ILX", "2016-2022", ["2.4L"], 0.85, "Similar design")
                ],
                "interchangeable": [
                    InterchangeablePart("ALT-H-001", "Denso", "OEM", "$180-220"),
                    InterchangeablePart("13579", "Bosch", "Aftermarket", "$120-160"),
                    InterchangeablePart("8483", "Remy", "Remanufactured", "$80-120")
                ],
                "specifications": {
                    "output": "130 Amp",
                    "voltage": "12V",
                    "mounting": "Bolt-on",
                    "warranty": "3 Years"
                }
            },
            
            # Toyota Oil Filter
            "90915-YZZD4": {
                "part_name": "Toyota OEM Oil Filter",
                "category": "Engine",
                "description": "Genuine Toyota oil filter for 4-cylinder engines",
                "compatibility": [
                    PartCompatibility("Toyota", "Camry", "2018-2023", ["2.5L 4cyl"], 0.98, "Direct OEM fit"),
                    PartCompatibility("Toyota", "RAV4", "2019-2023", ["2.5L 4cyl"], 0.98, "Direct OEM fit"),
                    PartCompatibility("Lexus", "ES350", "2019-2023", ["2.5L 4cyl"], 0.90, "Hybrid models")
                ],
                "interchangeable": [
                    InterchangeablePart("PF457G", "FRAM", "Aftermarket", "$8-12"),
                    InterchangeablePart("51515", "WIX", "Aftermarket", "$10-15")
                ],
                "specifications": {
                    "filter_type": "Spin-on",
                    "thread": "3/4-16",
                    "gasket_diameter": "62mm"
                }
            },
            
            # Generic entries for common searches
            "HONDA": {
                "part_name": "Honda Automotive Part",
                "category": "Various",
                "description": "Honda brand automotive component",
                "compatibility": [
                    PartCompatibility("Honda", "Various Models", "2010-2023", ["Multiple Engines"], 0.70, "Brand match detected")
                ],
                "interchangeable": [],
                "specifications": {}
            }
        }
    
    async def search_part_by_number(self, part_number: str) -> Optional[PartInfo]:
        """Search for part by number"""
        
        # Clean the part number
        cleaned_part = self._clean_part_number(part_number)
        
        # Try exact match first
        if cleaned_part in self.mock_database:
            data = self.mock_database[cleaned_part]
            return PartInfo(
                part_number=cleaned_part,
                part_name=data["part_name"],
                category=data["category"], 
                description=data["description"],
                compatibility=data["compatibility"],
                interchangeable=data["interchangeable"],
                specifications=data["specifications"],
                confidence=0.95,
                source="mock_database"
            )
        
        # Try partial matches
        for db_part, data in self.mock_database.items():
            if cleaned_part.upper() in db_part.upper() or db_part.upper() in cleaned_part.upper():
                return PartInfo(
                    part_number=db_part,
                    part_name=f"{data['part_name']} (Similar to {part_number})",
                    category=data["category"],
                    description=f"Similar part found: {data['description']}",
                    compatibility=data["compatibility"],
                    interchangeable=data["interchangeable"],
                    specifications=data["specifications"],
                    confidence=0.75,
                    source="fuzzy_match"
                )
        
        return None
    
    def _clean_part_number(self, part_number: str) -> str:
        """Clean and standardize part number format"""
        return re.sub(r'[^\w\-]', '', part_number.upper())
    
    async def close(self):
        """Close any open connections"""
        if self.session:
            await self.session.close()

# Create global instance
parts_db = PartsDatabase()
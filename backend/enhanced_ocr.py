# enhanced_ocr.py - Advanced OCR with automotive part number recognition
import cv2
import numpy as np
import easyocr
import re
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from typing import List, Dict, Tuple, Optional
import logging

class EnhancedOCR:
    """Advanced OCR specifically tuned for automotive part recognition"""
    
    def __init__(self):
        # Initialize multiple OCR engines
        self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
        
        # Automotive part number patterns (comprehensive)
        self.part_patterns = {
            # OEM Patterns
            'toyota': [
                r'\b\d{5}-\d{5}\b',  # 90915-YZZD4
                r'\b\d{5}-[A-Z0-9]{5}\b',
                r'\bTOYOTA\s+\d{5}-\d{5}\b'
            ],
            'honda': [
                r'\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b',  # 15400-PLM-A02
                r'\bHONDA\s+\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b',
                r'\b\d{5}-[A-Z]{3}-[A-Z]\d{2}\b'
            ],
            'ford': [
                r'\b[A-Z]\d[A-Z]\d-\d{4,5}-[A-Z]{1,2}\b',  # F1TZ-6714-A
                r'\bFORD\s+[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+\b',
                r'\bFL-\d{3}-S\b'  # FL-820-S
            ],
            'gm': [
                r'\b1\d{7,8}\b',  # 12345678
                r'\bAC\s*DELCO\s+[A-Z]*\d+[A-Z]*\b',  # AC DELCO PF52
                r'\bPF\d{2,4}[A-Z]?\b'
            ],
            'bmw': [
                r'\b11\d{2}\s?\d{3}\s?\d{3}\b',  # 11 12 7 834 495
                r'\bBMW\s+\d{2}\s?\d{3}\s?\d{3}\b'
            ],
            'mercedes': [
                r'\b[A-Z]\d{3}\s?\d{3}\s?\d{2}\s?\d{2}\b',  # A000 140 04 18
                r'\bMB\s+[A-Z0-9\s]+\b'
            ],
            # Aftermarket Patterns
            'bosch': [
                r'\b\d{3}\s?\d{3}\s?\d{3}\b',  # 0 280 158 117
                r'\bBOSCH\s+[A-Z0-9\-\s]+\b'
            ],
            'denso': [
                r'\b\d{3}-\d{4}\b',  # 234-4055
                r'\bDENSO\s+[A-Z0-9\-]+\b'
            ],
            'fram': [
                r'\bPH\d{4}[A-Z]?\b',  # PH3593A
                r'\bFRAM\s+[A-Z]{2}\d{4}[A-Z]?\b'
            ],
            'wix': [
                r'\b\d{5}[A-Z]?\b',  # 51515
                r'\bWIX\s+\d{4,6}[A-Z]?\b'
            ],
            'mobil1': [
                r'\bM1[A-Z]?-\d{3,4}[A-Z]?\b',  # M1-110A
                r'\bMOBIL\s*1\s+[A-Z0-9\-]+\b'
            ]
        }
        
        # Generic automotive patterns
        self.generic_patterns = [
            r'\b[A-Z]{2,4}\d{3,6}[A-Z]?\b',  # AC123456A
            r'\b\d{4,6}-[A-Z0-9]{2,4}\b',    # 12345-ABC
            r'\b[A-Z]\d{3}-\d{3}-\d{3}\b',   # A123-456-789
            r'\b\d{8,12}\b',                 # Long numeric codes
            r'\b[A-Z]{1,3}\d{3,8}[A-Z]{0,2}\b'  # General alphanumeric
        ]
        
    def preprocess_image(self, image: np.ndarray) -> List[np.ndarray]:
        """Advanced image preprocessing for better OCR accuracy"""
        processed_images = []
        
        # Original image
        processed_images.append(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. High contrast version
        contrast = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        processed_images.append(cv2.cvtColor(contrast, cv2.COLOR_GRAY2BGR))
        
        # 2. Denoised version
        denoised = cv2.fastNlMeansDenoising(gray)
        processed_images.append(cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR))
        
        # 3. Adaptive threshold
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        processed_images.append(cv2.cvtColor(adaptive_thresh, cv2.COLOR_GRAY2BGR))
        
        # 4. Morphological operations to clean up text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        processed_images.append(cv2.cvtColor(morph, cv2.COLOR_GRAY2BGR))
        
        # 5. Edge enhancement
        edges = cv2.Canny(gray, 50, 150)
        edge_enhanced = cv2.bitwise_or(gray, edges)
        processed_images.append(cv2.cvtColor(edge_enhanced, cv2.COLOR_GRAY2BGR))
        
        return processed_images
    
    def extract_text_multiple_engines(self, image: np.ndarray) -> Dict[str, List[Dict]]:
        """Extract text using multiple OCR engines for better accuracy"""
        results = {}
        
        # Process with multiple image preprocessing variants
        processed_images = self.preprocess_image(image)
        
        all_detections = []
        
        for i, proc_img in enumerate(processed_images):
            try:
                # EasyOCR
                easyocr_results = self.easyocr_reader.readtext(proc_img)
                for bbox, text, confidence in easyocr_results:
                    if confidence > 0.3:  # Lower threshold for part numbers
                        all_detections.append({
                            'text': text.strip(),
                            'confidence': confidence,
                            'bbox': bbox,
                            'engine': 'easyocr',
                            'preprocessing': i
                        })
                
                # Tesseract (if available)
                try:
                    # Convert to PIL Image for tesseract
                    pil_img = Image.fromarray(cv2.cvtColor(proc_img, cv2.COLOR_BGR2RGB))
                    
                    # Multiple Tesseract configs for different text types
                    configs = [
                        '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
                        '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
                        '--psm 7',
                        '--psm 13'
                    ]
                    
                    for config in configs:
                        try:
                            tesseract_text = pytesseract.image_to_string(pil_img, config=config)
                            lines = [line.strip() for line in tesseract_text.split('\n') if line.strip()]
                            
                            for line in lines:
                                if len(line) >= 3:  # Minimum length for part numbers
                                    all_detections.append({
                                        'text': line,
                                        'confidence': 0.7,  # Default confidence for tesseract
                                        'bbox': None,
                                        'engine': 'tesseract',
                                        'preprocessing': i,
                                        'config': config
                                    })
                        except:
                            continue
                            
                except ImportError:
                    pass  # Tesseract not available
                    
            except Exception as e:
                logging.warning(f"OCR processing failed for image variant {i}: {e}")
                continue
        
        # Deduplicate and rank results
        results['detections'] = self._deduplicate_detections(all_detections)
        
        return results
    
    def _deduplicate_detections(self, detections: List[Dict]) -> List[Dict]:
        """Remove duplicate detections and rank by confidence"""
        seen_texts = {}
        
        for detection in detections:
            text = detection['text'].upper().strip()
            if not text:
                continue
                
            # Skip very short or very long texts
            if len(text) < 2 or len(text) > 50:
                continue
                
            # Keep the detection with highest confidence
            if text not in seen_texts or detection['confidence'] > seen_texts[text]['confidence']:
                seen_texts[text] = detection
        
        # Sort by confidence and part number likelihood
        ranked_detections = list(seen_texts.values())
        ranked_detections.sort(key=lambda x: (
            self._calculate_part_likelihood(x['text']),
            x['confidence']
        ), reverse=True)
        
        return ranked_detections
    
    def _calculate_part_likelihood(self, text: str) -> float:
        """Calculate likelihood that text is a part number"""
        score = 0.0
        text_upper = text.upper()
        
        # Check against known patterns
        for brand, patterns in self.part_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    score += 0.9
                    break
        
        # Check generic patterns
        for pattern in self.generic_patterns:
            if re.search(pattern, text_upper):
                score += 0.7
                break
        
        # Heuristics
        if re.search(r'\d', text):  # Contains numbers
            score += 0.3
        if re.search(r'[A-Z]', text):  # Contains letters
            score += 0.2
        if re.search(r'-', text):  # Contains hyphens
            score += 0.2
        if 5 <= len(text) <= 20:  # Reasonable length
            score += 0.3
        if re.search(r'^[A-Z0-9\-]+$', text):  # Only alphanumeric and hyphens
            score += 0.2
            
        # Brand indicators
        brand_keywords = ['TOYOTA', 'HONDA', 'FORD', 'GM', 'BMW', 'MERCEDES', 'BOSCH', 'DENSO', 'FRAM', 'WIX', 'MOBIL', 'AC', 'DELCO']
        for keyword in brand_keywords:
            if keyword in text_upper:
                score += 0.4
                break
        
        return min(score, 1.0)
    
    def extract_part_numbers(self, image: np.ndarray) -> Dict:
        """Main method to extract part numbers from image"""
        try:
            # Extract all text
            ocr_results = self.extract_text_multiple_engines(image)
            
            # Find best part number candidates
            part_candidates = []
            all_texts = []
            
            for detection in ocr_results['detections']:
                text = detection['text']
                all_texts.append(text)
                
                likelihood = self._calculate_part_likelihood(text)
                if likelihood > 0.5:  # Threshold for part number candidates
                    part_candidates.append({
                        'text': text,
                        'likelihood': likelihood,
                        'confidence': detection['confidence'],
                        'combined_score': likelihood * detection['confidence'],
                        'engine': detection['engine']
                    })
            
            # Sort candidates by combined score
            part_candidates.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Identify best part number
            best_part_number = None
            if part_candidates:
                best_candidate = part_candidates[0]
                if best_candidate['combined_score'] > 0.4:
                    best_part_number = best_candidate['text']
            
            return {
                'part_number': best_part_number,
                'all_texts': all_texts,
                'part_candidates': part_candidates[:5],  # Top 5 candidates
                'total_detections': len(ocr_results['detections']),
                'success': best_part_number is not None
            }
            
        except Exception as e:
            logging.error(f"Enhanced OCR failed: {e}")
            return {
                'part_number': None,
                'all_texts': [],
                'part_candidates': [],
                'total_detections': 0,
                'success': False,
                'error': str(e)
            }

# Global instance
enhanced_ocr = EnhancedOCR()
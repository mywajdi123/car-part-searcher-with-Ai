# cnn_model.py - CNN for automotive part visual recognition
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision.models import resnet50, efficientnet_b3
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Dict, List, Tuple, Optional
import os
import requests
from io import BytesIO

class AutoPartsCNN(nn.Module):
    """CNN model specifically designed for automotive part recognition"""
    
    def __init__(self, num_classes=50):  # 50 common automotive parts
        super(AutoPartsCNN, self).__init__()
        
        # Use pre-trained EfficientNet as backbone
        self.backbone = efficientnet_b3(pretrained=True)
        
        # Modify classifier for automotive parts
        num_features = self.backbone.classifier.in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes)
        )
        
        # Additional features for part condition assessment
        self.condition_classifier = nn.Sequential(
            nn.Linear(num_features, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 4)  # New, Used, Worn, Damaged
        )
        
    def forward(self, x):
        # Extract features from backbone
        features = self.backbone.features(x)
        features = self.backbone.avgpool(features)
        features = torch.flatten(features, 1)
        
        # Part classification
        part_logits = self.backbone.classifier(features)
        
        # Condition classification
        condition_logits = self.condition_classifier(features)
        
        return part_logits, condition_logits

class AutomotivePartRecognizer:
    """Complete automotive part recognition system"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.is_loaded = False
        
        # Part categories mapping
        self.part_classes = {
            0: "Air Filter", 1: "Oil Filter", 2: "Fuel Filter", 3: "Cabin Filter",
            4: "Brake Pad", 5: "Brake Rotor", 6: "Brake Caliper", 7: "Brake Line",
            8: "Spark Plug", 9: "Ignition Coil", 10: "Glow Plug", 11: "Distributor Cap",
            12: "Alternator", 13: "Starter", 14: "Battery", 15: "Voltage Regulator",
            16: "Radiator", 17: "Thermostat", 18: "Water Pump", 19: "Cooling Fan",
            20: "Shock Absorber", 21: "Strut", 22: "Spring", 23: "Control Arm",
            24: "Tie Rod", 25: "Ball Joint", 26: "Stabilizer Bar", 27: "Bushing",
            28: "Timing Belt", 29: "Serpentine Belt", 30: "V-Belt", 31: "Chain",
            32: "Fuel Pump", 33: "Fuel Injector", 34: "Throttle Body", 35: "MAF Sensor",
            36: "O2 Sensor", 37: "MAP Sensor", 38: "TPS Sensor", 39: "Knock Sensor",
            40: "Headlight", 41: "Taillight", 42: "Turn Signal", 43: "Bulb",
            44: "Tire", 45: "Rim", 46: "Hub Cap", 47: "Valve Stem",
            48: "Exhaust Pipe", 49: "Muffler"
        }
        
        self.condition_classes = {
            0: "New",
            1: "Used - Good",
            2: "Used - Worn", 
            3: "Damaged"
        }
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Try to load pre-trained model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model or initialize new one"""
        try:
            model_path = "automotive_parts_model.pth"
            
            # Initialize model
            self.model = AutoPartsCNN(num_classes=len(self.part_classes))
            
            # Try to load pre-trained weights
            if os.path.exists(model_path):
                try:
                    checkpoint = torch.load(model_path, map_location=self.device)
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                    self.is_loaded = True
                    logging.info("Loaded pre-trained automotive parts model")
                except Exception as e:
                    logging.warning(f"Could not load pre-trained model: {e}")
                    self.is_loaded = False
            else:
                # Try to download from a hypothetical model repository
                self._download_pretrained_model(model_path)
            
            self.model.to(self.device)
            self.model.eval()
            
        except Exception as e:
            logging.error(f"Failed to initialize CNN model: {e}")
            self.model = None
            self.is_loaded = False
    
    def _download_pretrained_model(self, model_path: str):
        """Download pre-trained model (placeholder for actual model hosting)"""
        try:
            # This would be replaced with actual model download URL
            # model_url = "https://your-model-host.com/automotive_parts_model.pth"
            # response = requests.get(model_url)
            # if response.status_code == 200:
            #     with open(model_path, 'wb') as f:
            #         f.write(response.content)
            #     self.is_loaded = True
            
            # For now, we'll use the untrained model
            logging.info("Using untrained CNN model - would download in production")
            self.is_loaded = False
            
        except Exception as e:
            logging.warning(f"Could not download pre-trained model: {e}")
            self.is_loaded = False
    
    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for CNN inference"""
        try:
            # Convert BGR to RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Convert to PIL Image
            pil_image = Image.fromarray(image_rgb)
            
            # Apply transforms
            tensor_image = self.transform(pil_image)
            
            # Add batch dimension
            tensor_image = tensor_image.unsqueeze(0)
            
            return tensor_image.to(self.device)
            
        except Exception as e:
            logging.error(f"Image preprocessing failed: {e}")
            return None
    
    def predict_part(self, image: np.ndarray) -> Dict:
        """Predict automotive part from image using CNN"""
        if self.model is None:
            return {
                'success': False,
                'error': 'CNN model not available',
                'part_type': 'Unknown',
                'confidence': 0.0,
                'condition': 'Unknown',
                'condition_confidence': 0.0
            }
        
        try:
            # Preprocess image
            input_tensor = self.preprocess_image(image)
            if input_tensor is None:
                raise Exception("Image preprocessing failed")
            
            # Run inference
            with torch.no_grad():
                part_logits, condition_logits = self.model(input_tensor)
                
                # Get predictions
                part_probs = F.softmax(part_logits, dim=1)
                condition_probs = F.softmax(condition_logits, dim=1)
                
                # Get top predictions
                part_confidence, part_idx = torch.max(part_probs, 1)
                condition_confidence, condition_idx = torch.max(condition_probs, 1)
                
                # Convert to CPU and extract values
                part_idx = part_idx.cpu().item()
                condition_idx = condition_idx.cpu().item()
                part_confidence = part_confidence.cpu().item()
                condition_confidence = condition_confidence.cpu().item()
                
                # Get class names
                part_type = self.part_classes.get(part_idx, 'Unknown')
                condition = self.condition_classes.get(condition_idx, 'Unknown')
                
                # Get top 3 predictions for more detailed analysis
                top3_parts = torch.topk(part_probs, 3, dim=1)
                top3_conditions = torch.topk(condition_probs, 3, dim=1)
                
                top_predictions = []
                for i in range(3):
                    pred_idx = top3_parts.indices[0][i].cpu().item()
                    pred_conf = top3_parts.values[0][i].cpu().item()
                    pred_name = self.part_classes.get(pred_idx, 'Unknown')
                    top_predictions.append({
                        'part_type': pred_name,
                        'confidence': pred_conf
                    })
                
                return {
                    'success': True,
                    'part_type': part_type,
                    'confidence': part_confidence,
                    'condition': condition,
                    'condition_confidence': condition_confidence,
                    'top_predictions': top_predictions,
                    'model_loaded': self.is_loaded,
                    'category': self._get_part_category(part_type)
                }
                
        except Exception as e:
            logging.error(f"CNN prediction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'part_type': 'Unknown',
                'confidence': 0.0,
                'condition': 'Unknown',
                'condition_confidence': 0.0
            }
    
    def _get_part_category(self, part_type: str) -> str:
        """Map part type to general category"""
        categories = {
            'Engine': ['Air Filter', 'Oil Filter', 'Fuel Filter', 'Spark Plug', 'Ignition Coil', 
                      'Timing Belt', 'Serpentine Belt', 'V-Belt', 'Chain', 'Fuel Pump', 
                      'Fuel Injector', 'Throttle Body'],
            'Brakes': ['Brake Pad', 'Brake Rotor', 'Brake Caliper', 'Brake Line'],
            'Electrical': ['Alternator', 'Starter', 'Battery', 'Voltage Regulator', 'MAF Sensor',
                          'O2 Sensor', 'MAP Sensor', 'TPS Sensor', 'Knock Sensor'],
            'Cooling': ['Radiator', 'Thermostat', 'Water Pump', 'Cooling Fan'],
            'Suspension': ['Shock Absorber', 'Strut', 'Spring', 'Control Arm', 'Tie Rod',
                          'Ball Joint', 'Stabilizer Bar', 'Bushing'],
            'Lighting': ['Headlight', 'Taillight', 'Turn Signal', 'Bulb'],
            'Wheels': ['Tire', 'Rim', 'Hub Cap', 'Valve Stem'],
            'Exhaust': ['Exhaust Pipe', 'Muffler'],
            'Filtration': ['Cabin Filter']
        }
        
        for category, parts in categories.items():
            if part_type in parts:
                return category
        
        return 'General'
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            'model_available': self.model is not None,
            'model_loaded': self.is_loaded,
            'device': str(self.device),
            'num_part_classes': len(self.part_classes),
            'num_condition_classes': len(self.condition_classes)
        }

# Global instance
cnn_recognizer = AutomotivePartRecognizer()
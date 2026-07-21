"""Gemma 4 via Google Gemini API - Real Gemma 4, free tier."""
import requests
import os
import json
from loguru import logger


class GemmaEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = "gemma-4-26b-a4b-it"
        
        if self.api_key:
            self._use_api = True
            logger.info(f"USING REAL GEMMA 4 ({self.model}) via Google Gemini API")
        else:
            self._use_api = False
            logger.warning("No GEMINI_API_KEY - using mock responses")
    
    def generate(self, prompt: str, max_tokens: int = 400) -> str:
        if self._use_api:
            result = self._api_generate(prompt, max_tokens)
            if result:
                return result
        logger.warning("Falling back to MOCK response")
        return self._mock_response(prompt)
    
    def _api_generate(self, prompt: str, max_tokens: int) -> str:
        """Call Google Gemini API with real Gemma 4."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            
            payload = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.2,
                    "topP": 0.95,
                }
            }
            
            logger.info(f"Calling Gemma 4 via Gemini API...")
            
            response = requests.post(
                url,
                params={"key": self.api_key},
                json=payload,
                timeout=30,
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    logger.info(f"Gemma 4: {text[:80]}...")
                    return text
                logger.warning("Empty response from Gemma 4")
                return None
            elif response.status_code == 429:
                logger.error("Rate limited. Waiting 5 seconds...")
                import time
                time.sleep(5)
                return None
            else:
                logger.error(f"Gemini API error {response.status_code}: {response.text[:200]}")
                return None
                
        except Exception as e:
            logger.error(f"Gemma 4 API call failed: {e}")
            return None
    
    def _mock_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        if "symptoms" in prompt_lower:
            return '{"diagnosis": [{"disease": "Malaria", "confidence": 0.78}, {"disease": "Typhoid", "confidence": 0.15}], "triage_level": "URGENT", "tests": ["MRDT", "Blood Culture"], "treatment": [{"medicine": "ACT", "dosage": "6 doses over 3 days"}, {"medicine": "Paracetamol", "dosage": "500mg twice daily"}], "self_care": ["Drink plenty of water", "Rest", "Take paracetamol for fever if available"]}'
        
        if "emergency" in prompt_lower:
            return '{"emergency_type": "ROAD_ACCIDENT", "severity": "SEVERE", "casualties_estimated": 3, "hazards_detected": "Fuel leakage suspected", "auto_message": "Road traffic accident reported. 3 visible casualties. Possible fuel leak. Immediate ambulance dispatch recommended."}'
        
        if "stock" in prompt_lower:
            return '{"days_until_stockout": 2, "severity": "CRITICAL", "recommended_action": "Transfer from Coast General Hospital", "suggested_quantity": 100, "ai_message": "CRITICAL: Stock will deplete in 2 days."}'
        
        if "rank" in prompt_lower or "hospital" in prompt_lower:
            return '{"ranked_hospitals": [{"name": "Mama Ngina Hospital", "score": 88, "reason": "Tests available, doctor present, short wait"}, {"name": "Likoni PHC", "score": 55, "reason": "Closer but no doctor available"}], "recommendation": "Go to Mama Ngina Hospital."}'
        
        if "daily" in prompt_lower or "summary" in prompt_lower:
            return '{"summary": "Today the hospital treated 87 patients.", "recommendations": ["Restock paediatric amoxicillin"], "prediction": "Expect similar load tomorrow."}'
        
        if "attendance" in prompt_lower:
            return '{"pattern_detected": true, "pattern_description": "Absent on Mondays and Fridays", "recommendation": "Schedule discussion and arrange locum coverage"}'
        
        return '{"analysis": "Analysis complete", "recommendation": "Proceed with standard protocol"}'

gemma = GemmaEngine()

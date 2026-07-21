"""Gemma 4 via Google Gemini API - With system prompt for JSON."""
import requests
import os
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
        """Call Google Gemini API with system instruction for JSON-only output."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            
            payload = {
                "system_instruction": {
                    "parts": [{
                        "text": "You are a medical AI. You ONLY output valid JSON. Never include explanations, markdown, or text outside the JSON object. Start your response with { and end with }."
                    }]
                },
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.1,
                    "topP": 0.9,
                }
            }
            
            logger.info("Calling Gemma 4 via Gemini API...")
            
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
                    # Clean response - strip any markdown or leading text
                    text = text.strip()
                    if '{' in text:
                        text = text[text.find('{'):text.rfind('}')+1]
                    logger.info(f"Gemma 4: {text[:80]}...")
                    return text
                return None
            elif response.status_code == 429:
                logger.error("Rate limited")
                return None
            else:
                logger.error(f"API error {response.status_code}: {response.text[:200]}")
                return None
                
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None
    
    def _mock_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        if "symptoms" in prompt_lower:
            return '{"diagnosis": [{"disease": "Malaria", "confidence": 0.78}, {"disease": "Typhoid", "confidence": 0.15}], "triage_level": "URGENT", "tests": ["MRDT", "Blood Culture"], "treatment": [{"medicine": "ACT", "dosage": "6 doses over 3 days"}, {"medicine": "Paracetamol", "dosage": "500mg twice daily"}], "self_care": ["Drink water", "Rest"]}'
        
        if "emergency" in prompt_lower:
            return '{"emergency_type": "ROAD_ACCIDENT", "severity": "SEVERE", "casualties_estimated": 3, "hazards_detected": "Fuel leak", "auto_message": "Accident at location. Dispatch immediately."}'
        
        if "stock" in prompt_lower:
            return '{"days_until_stockout": 2, "severity": "CRITICAL", "recommended_action": "Transfer from Coast General", "suggested_quantity": 100, "ai_message": "Stock depletes in 2 days."}'
        
        if "rank" in prompt_lower or "hospital" in prompt_lower:
            return '{"ranked_hospitals": [{"name": "Mama Ngina Hospital", "score": 88, "reason": "Tests available"}], "recommendation": "Go to Mama Ngina Hospital."}'
        
        if "daily" in prompt_lower:
            return '{"summary": "87 patients treated today.", "recommendations": ["Restock amoxicillin"], "prediction": "Similar load tomorrow."}'
        
        if "attendance" in prompt_lower:
            return '{"pattern_detected": true, "pattern_description": "Absent Mondays/Fridays", "recommendation": "Schedule discussion."}'
        
        return '{"analysis": "Complete", "recommendation": "Standard protocol"}'

gemma = GemmaEngine()

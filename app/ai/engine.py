"""Gemma 4 engine - works with or without PyTorch installed."""
import json
from app.config import settings
from loguru import logger


class GemmaEngine:
    """Singleton for Gemma 4 model management."""
    
    _instance = None
    _model = None
    _tokenizer = None
    _torch_available = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._check_torch()
    
    def _check_torch(self):
        """Check if PyTorch and Transformers are available."""
        try:
            import torch
            import transformers
            self._torch_available = True
            logger.info("PyTorch and Transformers available - can load Gemma 4")
        except ImportError:
            self._torch_available = False
            logger.info("PyTorch not installed - using mock AI responses for development")
    
    def load_model(self):
        """Load Gemma 4 from Hugging Face if torch is available."""
        if self._model is not None:
            return
        
        if not self._torch_available:
            logger.info("Skipping model load - using mock responses")
            return
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            logger.info(f"Loading Gemma model: {settings.GEMMA_MODEL}")
            self._tokenizer = AutoTokenizer.from_pretrained(
                settings.GEMMA_MODEL,
                token=settings.HF_TOKEN or True
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                settings.GEMMA_MODEL,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                token=settings.HF_TOKEN or True,
                low_cpu_mem_usage=True,
            )
            logger.info("Gemma model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load Gemma model: {e}. Using mock responses.")
            self._model = None
            self._tokenizer = None
    
    def generate(self, prompt: str, max_tokens: int = 300) -> str:
        """Run inference or return mock response."""
        if not self._torch_available or self._model is None:
            return self._mock_response(prompt)
        
        try:
            import torch
            inputs = self._tokenizer(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")
            
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.3,
                do_sample=True,
            )
            return self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Gemma inference failed: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Mock responses for development without GPU."""
        prompt_lower = prompt.lower()
        
        if "symptoms" in prompt_lower:
            return '{"diagnosis": [{"disease": "Malaria", "confidence": 0.78}, {"disease": "Typhoid", "confidence": 0.15}], "triage_level": "URGENT", "tests": ["MRDT", "Blood Culture"], "treatment": [{"medicine": "ACT", "dosage": "6 doses over 3 days"}, {"medicine": "Paracetamol", "dosage": "500mg twice daily"}], "self_care_advice": ["Drink plenty of water", "Rest", "Take paracetamol for fever if available"]}'
        
        if "emergency" in prompt_lower:
            return '{"emergency_type": "ROAD_ACCIDENT", "severity": "SEVERE", "casualties_estimated": 3, "hazards_detected": "Fuel leakage suspected", "auto_message": "Road traffic accident reported. 3 visible casualties. Possible fuel leak. Nearest facility: Coast General Hospital. Immediate ambulance dispatch recommended."}'
        
        if "stock" in prompt_lower or "inventory" in prompt_lower:
            return '{"days_until_stockout": 2, "severity": "CRITICAL", "recommended_action": "Transfer from Coast General Hospital", "suggested_source": "Coast General Hospital", "suggested_quantity": 100, "ai_message": "CRITICAL: Stock will deplete in 2 days. Recommend urgent transfer of 100 units from Coast General Hospital."}'
        
        if "rank" in prompt_lower or "hospital" in prompt_lower:
            return '{"ranked_hospitals": [{"name": "Mama Ngina Hospital", "score": 88, "reason": "Tests available, doctor present, short wait time"}, {"name": "Likoni PHC", "score": 55, "reason": "Closer but no doctor available today"}], "recommendation": "Go to Mama Ngina Hospital for best care."}'
        
        if "daily" in prompt_lower or "summary" in prompt_lower:
            return '{"summary": "Today the hospital treated 87 patients with 12 admissions and 8 discharges. Stock levels are generally adequate with 2 warnings. Staff attendance was 87%. Bed occupancy is at 72%.", "recommendations": ["Restock paediatric amoxicillin", "Review Dr. Otieno attendance pattern"], "prediction": "Expect similar patient load tomorrow with possible increase in malaria cases."}'
        
        if "attendance" in prompt_lower:
            return '{"pattern_detected": true, "pattern_description": "Absent on Mondays and Fridays for 3 consecutive weeks", "impact": "Patient wait times increase by 3x on affected days", "recommendation": "Schedule confidential discussion and arrange temporary locum coverage for Mondays and Fridays"}'
        
        return '{"analysis": "Analysis complete", "recommendation": "Proceed with standard protocol"}'

# Global instance
gemma = GemmaEngine()

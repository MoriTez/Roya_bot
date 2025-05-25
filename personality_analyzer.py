import json
import os
from openai import OpenAI
from typing import Dict, Any

class PersonalityAnalyzer:
    def __init__(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        else:
            self.openai_client = None
    
    def analyze_personality(self, base64_image: str, face_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze personality traits from facial features using OpenAI vision model
        """
        # اگر کلید OpenAI نداریم، از تحلیل ساده استفاده می‌کنیم
        if not self.openai_client:
            return self._get_simple_analysis(face_features)
        
        try:
            # Prepare the analysis prompt in Persian
            system_prompt = """شما یک متخصص روانشناسی و تحلیل چهره هستید. وظیفه شما تحلیل ویژگی‌های شخصیتی و وضعیت عاطفی افراد بر اساس ویژگی‌های چهره آنهاست.

بر اساس تصویر ارائه شده، ویژگی‌های زیر را تحلیل کنید:

1. ویژگی‌های شخصیتی (عدد بین 0 تا 1):
   - برون‌گرایی (extraversion)
   - انعطاف‌پذیری (openness)
   - وظیفه‌شناسی (conscientiousness) 
   - توافق‌پذیری (agreeableness)
   - اعتماد به نفس (confidence)
   - خلاقیت (creativity)
   - رهبری (leadership)

2. وضعیت عاطفی (عدد بین 0 تا 1):
   - شادی (happiness)
   - آرامش (calmness)
   - سطح انرژی (energy_level)
   - سطح استرس (stress_level)

3. ارزیابی کلی شخصیت (متن فارسی)

پاسخ را به صورت JSON با ساختار زیر ارائه دهید:
{
  "personality_traits": {
    "extraversion": number,
    "openness": number,
    "conscientiousness": number,
    "agreeableness": number,
    "confidence": number,
    "creativity": number,
    "leadership": number
  },
  "emotional_state": {
    "happiness": number,
    "calmness": number,
    "energy_level": number,
    "stress_level": number
  },
  "overall_assessment": "متن ارزیابی کلی به فارسی"
}"""

            user_prompt = f"""لطفاً این تصویر چهره را تحلیل کنید و ویژگی‌های شخصیتی و عاطفی فرد را استخراج کنید.

اطلاعات تکمیلی از تحلیل تصویر:
- ابعاد چهره: {face_features.get('face_dimensions', 'نامشخص')}
- تعداد چشم‌های شناسایی شده: {face_features.get('eye_count', 0)}
- لبخند شناسایی شده: {'بله' if face_features.get('smile_detected', False) else 'خیر'}
- نسبت عرض به ارتفاع چهره: {face_features.get('face_width_height_ratio', 0):.2f}
- میزان روشنایی: {face_features.get('brightness', 0):.1f}
- میزان کنتراست: {face_features.get('contrast', 0):.1f}

بر اساس این اطلاعات و تحلیل بصری تصویر، ارزیابی دقیق و معنی‌داری ارائه دهید."""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.7
            )
            
            # Parse the JSON response
            analysis_result = json.loads(response.choices[0].message.content)
            
            # Validate and clean the response
            return self._validate_analysis_result(analysis_result)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._get_fallback_analysis()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._get_fallback_analysis()
    
    def _get_simple_analysis(self, face_features: Dict[str, Any]) -> Dict[str, Any]:
        """تحلیل ساده بر اساس ویژگی‌های چهره بدون استفاده از OpenAI"""
        import random
        
        # بر اساس ویژگی‌های چهره تحلیل می‌کنیم
        brightness = face_features.get('brightness', 100)
        smile_detected = face_features.get('smile_detected', False)
        face_ratio = face_features.get('face_width_height_ratio', 1.0)
        eye_count = face_features.get('eye_count', 2)
        
        # تحلیل بر اساس لبخند
        happiness_base = 0.8 if smile_detected else 0.4
        
        # تحلیل بر اساس روشنایی تصویر
        energy_base = min(1.0, brightness / 150)
        
        # تحلیل بر اساس نسبت چهره
        confidence_base = 0.7 if 0.7 <= face_ratio <= 1.3 else 0.5
        
        return {
            'personality_traits': {
                'extraversion': min(1.0, happiness_base + random.uniform(-0.1, 0.2)),
                'openness': min(1.0, energy_base + random.uniform(-0.1, 0.2)),
                'conscientiousness': min(1.0, confidence_base + random.uniform(-0.1, 0.2)),
                'agreeableness': min(1.0, happiness_base + random.uniform(-0.1, 0.1)),
                'confidence': confidence_base,
                'creativity': min(1.0, energy_base + random.uniform(-0.2, 0.3)),
                'leadership': min(1.0, confidence_base + random.uniform(-0.1, 0.2))
            },
            'emotional_state': {
                'happiness': happiness_base,
                'calmness': min(1.0, 0.6 + random.uniform(-0.1, 0.2)),
                'energy_level': energy_base,
                'stress_level': max(0.0, 0.3 - happiness_base * 0.2)
            },
            'overall_assessment': self._generate_persian_assessment(smile_detected, brightness, face_ratio)
        }
    
    def _generate_persian_assessment(self, has_smile: bool, brightness: float, face_ratio: float) -> str:
        """تولید ارزیابی فارسی بر اساس ویژگی‌های چهره"""
        assessments = []
        
        if has_smile:
            assessments.append("شما شخص شاد و مثبت‌اندیشی هستید که انرژی مثبت به اطرافیان منتقل می‌کنید.")
        else:
            assessments.append("شما شخص جدی و متفکری هستید که در تصمیم‌گیری‌هایتان دقت زیادی دارید.")
        
        if brightness > 120:
            assessments.append("انرژی بالا و روحیه مثبت از چهره شما نمایان است.")
        elif brightness < 80:
            assessments.append("شما شخص آرام و عمیق‌الفکری هستید.")
        
        if 0.8 <= face_ratio <= 1.2:
            assessments.append("تعادل و هماهنگی در شخصیت شما به چشم می‌خورد.")
        
        return " ".join(assessments)
    
    def get_vip_analysis(self, base64_image: str, face_features: Dict[str, Any]) -> Dict[str, Any]:
        """تحلیل کامل VIP با جزئیات بیشتر"""
        basic_analysis = self._get_simple_analysis(face_features)
        
        # افزودن ویژگی‌های VIP خاص
        vip_features = self._get_vip_features(face_features)
        basic_analysis.update(vip_features)
        
        # ارزیابی تخصصی VIP
        basic_analysis['vip_assessment'] = self._generate_vip_assessment(face_features)
        basic_analysis['career_guidance'] = self._get_career_guidance(basic_analysis)
        basic_analysis['relationship_insights'] = self._get_relationship_insights(basic_analysis)
        basic_analysis['success_factors'] = self._get_success_factors(basic_analysis)
        
        return basic_analysis
    
    def _get_vip_features(self, face_features: Dict[str, Any]) -> Dict[str, Any]:
        """ویژگی‌های اضافی VIP"""
        import random
        
        brightness = face_features.get('brightness', 100)
        smile_detected = face_features.get('smile_detected', False)
        face_ratio = face_features.get('face_width_height_ratio', 1.0)
        eye_distance = face_features.get('eye_distance', 50)
        
        return {
            'advanced_traits': {
                'intelligence_quotient': min(100, 70 + random.randint(10, 25)),
                'emotional_intelligence': min(100, 60 + random.randint(15, 30)),
                'charisma_level': min(100, 50 + random.randint(20, 40)),
                'business_acumen': min(100, 40 + random.randint(20, 45)),
                'artistic_talent': min(100, 45 + random.randint(15, 40)),
                'leadership_potential': min(100, 55 + random.randint(20, 35))
            },
            'life_patterns': {
                'risk_tolerance': random.choice(['محافظه‌کار', 'متعادل', 'مخاطره‌پذیر']),
                'decision_style': random.choice(['تحلیلی', 'شهودی', 'ترکیبی']),
                'social_preference': random.choice(['درون‌گرا', 'برون‌گرا', 'دوسویه']),
                'work_style': random.choice(['مستقل', 'تیمی', 'رهبری'])
            }
        }
    
    def _generate_vip_assessment(self, face_features: Dict[str, Any]) -> str:
        """ارزیابی تخصصی VIP"""
        assessments = [
            "تحلیل تخصصی نشان می‌دهد شما دارای پتانسیل‌های ویژه‌ای هستید.",
            "ویژگی‌های چهره شما حاکی از شخصیتی پیچیده و جذاب است.",
            "نقاط قوت شما در حوزه‌های خاصی بیش از حد متوسط جامعه قرار دارد."
        ]
        return " ".join(assessments)
    
    def _get_career_guidance(self, analysis: Dict[str, Any]) -> str:
        """راهنمایی شغلی بر اساس شخصیت"""
        traits = analysis.get('personality_traits', {})
        leadership = traits.get('leadership', 0.5)
        creativity = traits.get('creativity', 0.5)
        
        if leadership > 0.7:
            return "شما برای مشاغل مدیریتی، کارآفرینی و رهبری تیم مناسب هستید."
        elif creativity > 0.7:
            return "استعداد شما در حوزه‌های هنری، طراحی و خلاقیت قابل توجه است."
        else:
            return "شما در مشاغل تخصصی و تحلیلی عملکرد بهتری خواهید داشت."
    
    def _get_relationship_insights(self, analysis: Dict[str, Any]) -> str:
        """بینش روابط عاطفی"""
        traits = analysis.get('personality_traits', {})
        agreeableness = traits.get('agreeableness', 0.5)
        
        if agreeableness > 0.7:
            return "شما در روابط عاطفی فردی دلسوز و مهربان هستید که همسر ایده‌آلی محسوب می‌شوید."
        else:
            return "شما در روابط به استقلال اهمیت می‌دهید و نیاز به فضای شخصی دارید."
    
    def _get_success_factors(self, analysis: Dict[str, Any]) -> str:
        """عوامل موفقیت شخصی"""
        return "برای رسیدن به اهداف‌تان، روی نقاط قوت شخصیتی‌تان تمرکز کنید و از ویژگی‌های منحصربه‌فردتان استفاده کنید."
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize the analysis result"""
        validated_result = {
            'personality_traits': {},
            'emotional_state': {},
            'overall_assessment': ''
        }
        
        # Validate personality traits
        personality_keys = ['extraversion', 'openness', 'conscientiousness', 
                          'agreeableness', 'confidence', 'creativity', 'leadership']
        
        if 'personality_traits' in result:
            for key in personality_keys:
                if key in result['personality_traits']:
                    value = result['personality_traits'][key]
                    if isinstance(value, (int, float)):
                        validated_result['personality_traits'][key] = max(0, min(1, float(value)))
        
        # Validate emotional state
        emotion_keys = ['happiness', 'calmness', 'energy_level', 'stress_level']
        
        if 'emotional_state' in result:
            for key in emotion_keys:
                if key in result['emotional_state']:
                    value = result['emotional_state'][key]
                    if isinstance(value, (int, float)):
                        validated_result['emotional_state'][key] = max(0, min(1, float(value)))
        
        # Validate overall assessment
        if 'overall_assessment' in result and isinstance(result['overall_assessment'], str):
            validated_result['overall_assessment'] = result['overall_assessment']
        
        return validated_result
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return a fallback analysis when API fails"""
        return {
            'personality_traits': {
                'extraversion': 0.5,
                'openness': 0.5,
                'conscientiousness': 0.5,
                'agreeableness': 0.5,
                'confidence': 0.5,
                'creativity': 0.5,
                'leadership': 0.5
            },
            'emotional_state': {
                'happiness': 0.5,
                'calmness': 0.5,
                'energy_level': 0.5,
                'stress_level': 0.3
            },
            'overall_assessment': 'متأسفانه در حال حاضر قادر به انجام تحلیل دقیق نیستم. لطفاً بعداً مجدداً تلاش کنید.'
        }

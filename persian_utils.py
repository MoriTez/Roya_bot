def format_personality_report(analysis_data: dict) -> str:
    """Format personality analysis results in Persian"""
    
    personality_traits = analysis_data.get('personality_traits', {})
    emotional_state = analysis_data.get('emotional_state', {})
    overall_assessment = analysis_data.get('overall_assessment', '')
    
    report = "✨ **نتیجه تحلیل جادویی شخصیت شما!** 🎭\n\n"
    
    # Personality traits section
    if personality_traits:
        report += "🧠 **ویژگی‌های شخصیتی شما:**\n"
        
        trait_descriptions = {
            'extraversion': '🎉 برون‌گرایی',
            'openness': '🌈 انعطاف‌پذیری',
            'conscientiousness': '📋 وظیفه‌شناسی',
            'agreeableness': '🤝 توافق‌پذیری',
            'neuroticism': '😟 نوروز‌گرایی',
            'confidence': '💪 اعتماد به نفس',
            'creativity': '🎨 خلاقیت',
            'leadership': '👑 رهبری',
            'empathy': '❤️ همدلی'
        }
        
        for trait, value in personality_traits.items():
            persian_name = trait_descriptions.get(trait, trait)
            if isinstance(value, (int, float)):
                percentage = int(value * 100) if value <= 1 else int(value)
                report += f"• {persian_name}: {percentage}%\n"
            else:
                report += f"• {persian_name}: {value}\n"
        
        report += "\n"
    
    # Emotional state section
    if emotional_state:
        report += "😊 **وضعیت عاطفی:**\n"
        
        emotion_descriptions = {
            'happiness': 'شادی',
            'sadness': 'غم',
            'anger': 'خشم',
            'fear': 'ترس',
            'surprise': 'تعجب',
            'disgust': 'انزجار',
            'neutral': 'خنثی',
            'stress_level': 'سطح استرس',
            'energy_level': 'سطح انرژی'
        }
        
        for emotion, value in emotional_state.items():
            persian_name = emotion_descriptions.get(emotion, emotion)
            if isinstance(value, (int, float)):
                percentage = int(value * 100) if value <= 1 else int(value)
                report += f"• {persian_name}: {percentage}%\n"
            else:
                report += f"• {persian_name}: {value}\n"
        
        report += "\n"
    
    # Overall assessment
    if overall_assessment:
        report += "📝 **ارزیابی کلی:**\n"
        report += f"{overall_assessment}\n\n"
    
    # VIP features if available
    if 'advanced_traits' in analysis_data:
        report += "🎯 **ویژگی‌های پیشرفته (VIP):**\n"
        advanced_traits = analysis_data['advanced_traits']
        
        vip_descriptions = {
            'intelligence_quotient': '🧠 ضریب هوشی',
            'emotional_intelligence': '💝 هوش عاطفی', 
            'charisma_level': '✨ جذابیت شخصی',
            'business_acumen': '💼 هوش تجاری',
            'artistic_talent': '🎨 استعداد هنری',
            'leadership_potential': '👑 پتانسیل رهبری'
        }
        
        for trait, value in advanced_traits.items():
            persian_name = vip_descriptions.get(trait, trait)
            report += f"• {persian_name}: {value}% \n"
        
        report += "\n"
    
    # Life patterns for VIP
    if 'life_patterns' in analysis_data:
        report += "🔮 **الگوهای زندگی (VIP):**\n"
        life_patterns = analysis_data['life_patterns']
        
        pattern_descriptions = {
            'risk_tolerance': '⚡ تحمل ریسک',
            'decision_style': '🎯 سبک تصمیم‌گیری',
            'social_preference': '👥 ترجیح اجتماعی',
            'work_style': '💪 سبک کاری'
        }
        
        for pattern, value in life_patterns.items():
            persian_name = pattern_descriptions.get(pattern, pattern)
            report += f"• {persian_name}: {value}\n"
        
        report += "\n"
    
    # VIP assessments
    if 'career_guidance' in analysis_data:
        report += "💼 **راهنمایی شغلی (VIP):**\n"
        report += f"{analysis_data['career_guidance']}\n\n"
    
    if 'relationship_insights' in analysis_data:
        report += "💕 **بینش روابط (VIP):**\n"
        report += f"{analysis_data['relationship_insights']}\n\n"
    
    if 'success_factors' in analysis_data:
        report += "🎯 **عوامل موفقیت (VIP):**\n"
        report += f"{analysis_data['success_factors']}\n\n"
    
    # Disclaimer
    if 'advanced_traits' in analysis_data:
        report += "👑 **تبریک! شما عضو VIP هستید و از تحلیل‌های تخصصی بهره می‌برید.**\n\n"
    
    report += "⚠️ **توجه:** این تحلیل بر اساس ویژگی‌های ظاهری چهره انجام شده و صرفاً جنبه تفریحی دارد. برای ارزیابی دقیق شخصیت به متخصصان مراجعه کنید."
    
    return report

def get_error_message(error_type: str) -> str:
    """Get error messages in Persian"""
    error_messages = {
        'no_face': '🔍 اوه! تو عکس چهره‌ای پیدا نکردم! 😅\n📸 یه عکس واضح از خودت بفرست تا بتونم شخصیتت رو بخونم! ✨',
        'multiple_faces': '👥 وای! چندتا چهره تو عکس دیدم! 😊\n👤 لطفاً یه عکس فقط از خودت بفرست تا روی تو تمرکز کنم! 💫',
        'poor_quality': '📷 کیفیت عکس کمی ضعیفه عزیزم! 😔\n✨ یه عکس واضح‌تر و روشن‌تر بفرست تا بهتر تحلیلت کنم! 📸',
        'file_too_large': '📊 حجم عکست خیلی زیاده! 😅\n💾 لطفاً عکسی کمتر از ۱۰ مگابایت بفرست! 🔄',
        'unsupported_format': '🖼️ این فرمت عکس رو نمی‌شناسم! 😊\n📱 لطفاً عکست رو به فرمت JPG یا PNG بفرست! ✅',
        'analysis_failed': '🔮 اوپس! یه مشکل کوچولو پیش اومد! 😅\n🔄 دوباره امتحان کن، حتماً این بار جواب میده! 💪',
        'rate_limit': '⏰ عزیزم، یکم عجله داری! 😊\n🕐 {} ثانیه دیگه صبر کن، بعدش دوباره عکست رو بفرست! ⏳',
        'api_error': '🌐 یه مشکل موقت با سرور پیش اومد! 😔\n🔄 چند دقیقه دیگه دوباره تلاش کن! ⭐',
        'processing_error': '⚡ مشکلی تو پردازش عکس بود! 😅\n📸 یه عکس دیگه امتحان کن، حتماً این بار موفق می‌شیم! 🎯'
    }
    
    return error_messages.get(error_type, '❌ خطای نامشخص رخ داده است.')

def get_subscription_offer_message() -> str:
    """پیام تشویق برای خرید اشتراک"""
    return """💎 **تحلیل رایگان شما تمام شد!** ✨

🔥 **اما این تازه شروع کار بود!** 
می‌خوای بدونی چه رازهای عمیق‌تری تو شخصیتت پنهان شده؟

🎯 **با اشتراک VIP دریافت کن:**
🧠 ضریب هوشی و هوش عاطفی دقیق
💼 راهنمایی شغلی تخصصی 
💕 تحلیل روابط عاطفی
✨ سطح جذابیت و کاریزما
🎨 استعدادهای پنهان هنری
👑 پتانسیل رهبری و موفقیت
🔮 الگوهای زندگی و تصمیم‌گیری

💰 **فقط ۱۰۰ هزار تومان برای یک ماه کامل!**
🔄 **تحلیل نامحدود + ویژگی‌های VIP**

🚀 **برای خرید اشتراک دکمه /vip رو بزن!**"""

def get_vip_purchase_message() -> str:
    """پیام خرید اشتراک VIP"""
    return """👑 **خرید اشتراک VIP** 💎

🎯 **شما در حال خرید اشتراک ماهانه VIP هستید:**

💰 **قیمت:** ۱۰۰,۰۰۰ تومان
⏰ **مدت:** ۳۰ روز
🔄 **تحلیل:** نامحدود در طول ماه

✨ **ویژگی‌های VIP شامل:**
🧠 تحلیل ضریب هوشی
💝 سنجش هوش عاطفی
💼 راهنمایی شغلی تخصصی
💕 بینش روابط عاطفی
🎨 کشف استعدادهای هنری
👑 ارزیابی پتانسیل رهبری
🔮 تحلیل الگوهای زندگی

🔗 **لینک پرداخت امن زرین‌پال رو دریافت می‌کنید...**"""

def get_payment_success_message() -> str:
    """پیام موفقیت پرداخت"""
    return """🎉 **تبریک! پرداخت موفق بود!** 💎

👑 **حالا شما عضو VIP هستید!** ✨

🔥 **از الان می‌تونید:**
📸 تحلیل‌های نامحدود انجام بدید
🎯 از همه ویژگی‌های پیشرفته استفاده کنید
💎 گزارش‌های کامل و تخصصی دریافت کنید

🚀 **یه عکس جدید بفرست تا تحلیل VIP رو ببینی!** 📷✨"""

def get_already_used_free_message() -> str:
    """پیام برای کاربری که قبلاً از تحلیل رایگان استفاده کرده"""
    return """🔒 **شما قبلاً از تحلیل رایگان استفاده کردید!** 

💎 **برای ادامه نیاز به اشتراک VIP دارید:**

🎯 **ویژگی‌های فوق‌العاده VIP:**
🧠 تحلیل عمیق ضریب هوشی
💼 راهنمایی شغلی حرفه‌ای
💕 بینش روابط عاطفی
✨ سنجش جذابیت شخصی
🎨 کشف استعدادهای مخفی
👑 ارزیابی پتانسیل رهبری

💰 **فقط ۱۰۰ هزار تومان - یک ماه کامل**
🔄 **تحلیل نامحدود + ویژگی‌های حرفه‌ای**

🚀 **دکمه /vip رو بزن و الان شروع کن!** 💎"""

def get_welcome_message() -> str:
    """Get welcome message in Persian"""
    return """🌟 **سلام عزیز! به ربات جادویی تحلیل شخصیت خوش آمدید** 🎭

✨ من یک روانشناس مجازی هستم که با قدرت هوش مصنوعی، از روی چهره شما می‌توانم شخصیت‌تان را تحلیل کنم! 🔮

💎 **از منوی زیر گزینه مورد نظرتان را انتخاب کنید:** 👇"""

def get_main_menu_keyboard():
    """منوی اصلی با دکمه‌های شیشه‌ای"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = [
        [KeyboardButton("📸 تحلیل شخصیت"), KeyboardButton("👑 اشتراک VIP")],
        [KeyboardButton("📊 وضعیت من"), KeyboardButton("❓ راهنما")],
        [KeyboardButton("📞 پشتیبانی"), KeyboardButton("🎯 درباره ربات")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False,
        input_field_placeholder="از منو انتخاب کنید..."
    )

def get_help_message() -> str:
    """پیام راهنما"""
    return """📖 **راهنمای استفاده از ربات** 

🎯 **گزینه‌های منو:**

📸 **تحلیل شخصیت:**
• اولین بار رایگان!
• عکس واضح از چهره بفرستید
• تحلیل فوری در کمتر از 30 ثانیه

👑 **اشتراک VIP:**
• تحلیل‌های نامحدود
• ویژگی‌های پیشرفته
• قیمت: 100 هزار تومان/ماه

📊 **وضعیت من:**
• بررسی اشتراک شما
• تاریخچه تحلیل‌ها

❓ **راهنما:** همین صفحه
📞 **پشتیبانی:** ارتباط با تیم پشتیبانی
🎯 **درباره ربات:** اطلاعات بیشتر

🚀 **شروع کنید!** از منوی اصلی گزینه مورد نظر را انتخاب کنید."""

def get_about_message() -> str:
    """پیام درباره ربات"""
    return """🎭 **درباره ربات تحلیل شخصیت**

🔬 **تکنولوژی پیشرفته:**
• هوش مصنوعی GPT-4o
• تشخیص چهره OpenCV
• تحلیل ویژگی‌های بصری

💎 **ویژگی‌های کاربر VIP:**
🧠 تحلیل ضریب هوشی دقیق
💼 راهنمایی شغلی تخصصی
💕 بینش روابط عاطفی عمیق
✨ سنجش کاریزما و جذابیت
🎨 کشف استعدادهای هنری
👑 ارزیابی پتانسیل رهبری
🔮 تحلیل الگوهای تصمیم‌گیری

⚡ **سرعت و دقت:**
• تحلیل در کمتر از 30 ثانیه
• دقت بالا بر اساس علم روانشناسی
• گزارش‌های کامل فارسی

🌟 **ساخته شده با عشق برای شما!** 💖"""

def get_support_message() -> str:
    """پیام پشتیبانی"""
    return """📞 **پشتیبانی ربات تحلیل شخصیت**

🆘 **نیاز به کمک دارید؟**

💬 **راه‌های ارتباط:**
📧 ایمیل: support@personality-bot.ir
📱 تلگرام: @PersonalitySupport
🕐 پاسخگویی: 24/7

🔧 **مشکلات رایج:**
• عکس تشخیص داده نمی‌شود؟ → عکس واضح‌تر بفرستید
• پرداخت انجام نشد؟ → با پشتیبانی تماس بگیرید
• ربات پاسخ نمی‌دهد؟ → /start کنید

💡 **نکات مهم:**
✅ عکس باید واضح و با کیفیت باشد
✅ فقط یک چهره در تصویر باشد
✅ نوردهی مناسب داشته باشد

🚀 **ما همیشه آماده کمک هستیم!** 💪"""

def get_status_message(is_vip: bool, has_used_free: bool, vip_expires=None) -> str:
    """پیام وضعیت کاربر"""
    if is_vip:
        expire_text = ""
        if vip_expires:
            expire_text = f"\n📅 انقضاء: {vip_expires.strftime('%Y/%m/%d')}"
        
        return f"""👑 **وضعیت شما: VIP فعال** ✨

🎯 **امکانات فعال شما:**
✅ تحلیل‌های نامحدود
✅ ویژگی‌های پیشرفته VIP
✅ گزارش‌های تخصصی کامل{expire_text}

💎 **از اشتراک VIP لذت ببرید!**
📸 عکس بفرستید و تحلیل کامل دریافت کنید."""
    
    elif has_used_free:
        return """🔒 **وضعیت شما: تحلیل رایگان استفاده شده**

📊 **وضعیت فعلی:**
✅ یک تحلیل رایگان انجام شده
❌ برای ادامه نیاز به اشتراک VIP

💰 **ارتقاء به VIP:**
👑 تحلیل‌های نامحدود
🎯 ویژگی‌های پیشرفته
💎 فقط 100 هزار تومان/ماه

🚀 دکمه "👑 اشتراک VIP" را بزنید!"""
    
    else:
        return """🆓 **وضعیت شما: تحلیل رایگان موجود**

🎁 **شما یک تحلیل رایگان دارید!**
✨ بلافاصله استفاده کنید
📸 عکس واضح از چهره بفرستید

💡 **بعد از تحلیل رایگان:**
👑 امکان ارتقاء به VIP
🎯 ویژگی‌های پیشرفته
💎 تحلیل‌های نامحدود

🚀 دکمه "📸 تحلیل شخصیت" را بزنید!"""

def get_processing_message() -> str:
    """Get processing message in Persian"""
    return "🔮 **جادو شروع شد! در حال تحلیل چهره‌تان...** ✨\n\n🧠 دارم ویژگی‌های شخصیتی‌تان رو میخونم...\n💫 صبر کنید تا نتیجه جالب رو ببینید!"

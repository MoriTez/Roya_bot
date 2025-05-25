import logging
import asyncio
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN
from face_analyzer import FaceAnalyzer
from personality_analyzer import PersonalityAnalyzer
from persian_utils import (
    format_personality_report, 
    get_error_message, 
    get_welcome_message, 
    get_processing_message,
    get_subscription_offer_message,
    get_vip_purchase_message,
    get_already_used_free_message,
    get_main_menu_keyboard,
    get_help_message,
    get_about_message,
    get_support_message,
    get_status_message
)
from rate_limiter import RateLimiter
from models import get_user, is_user_vip, has_used_free_analysis, mark_free_analysis_used, save_analysis
from zarinpal import create_subscription_payment_link

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PersonalityBot:
    def __init__(self):
        self.face_analyzer = FaceAnalyzer()
        self.personality_analyzer = PersonalityAnalyzer()
        self.rate_limiter = RateLimiter()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            welcome_message = get_welcome_message()
            keyboard = get_main_menu_keyboard()
            await update.message.reply_text(
                welcome_message, 
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            logger.info(f"Start command from user {update.effective_user.id}")
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text("خطا در شروع ربات. لطفاً مجدداً تلاش کنید.")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages and perform personality analysis"""
        user_id = update.effective_user.id
        
        try:
            # Check rate limiting
            if not self.rate_limiter.is_allowed(user_id):
                wait_time = self.rate_limiter.get_wait_time(user_id)
                error_msg = get_error_message('rate_limit').format(wait_time)
                await update.message.reply_text(error_msg)
                return
            
            # Get user from database
            user = get_user(user_id)
            is_vip = is_user_vip(user_id)
            has_used_free = has_used_free_analysis(user_id)
            
            # Check if user can use the service
            if not is_vip and has_used_free:
                # User has used free analysis and is not VIP
                await update.message.reply_text(get_already_used_free_message(), parse_mode='Markdown')
                return
            
            # Send processing message
            processing_msg = await update.message.reply_text(get_processing_message(), parse_mode='Markdown')
            
            # Get the largest photo
            photo = update.message.photo[-1]
            
            # Download the photo
            photo_file = await photo.get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            logger.info(f"Processing photo from user {user_id}, size: {len(photo_bytes)} bytes")
            
            # Analyze face and detect features
            success, error_type, face_data = self.face_analyzer.detect_faces(bytes(photo_bytes))
            
            if not success:
                error_msg = get_error_message(error_type)
                await processing_msg.edit_text(error_msg)
                return
            
            # Perform personality analysis
            try:
                if is_vip:
                    # VIP analysis with full features
                    analysis_result = self.personality_analyzer.get_vip_analysis(
                        face_data['base64_image'], 
                        face_data['face_features']
                    )
                    analysis_type = "vip"
                else:
                    # Free analysis (limited)
                    analysis_result = self.personality_analyzer._get_simple_analysis(
                        face_data['face_features']
                    )
                    analysis_type = "free"
                    # Mark free analysis as used
                    mark_free_analysis_used(user_id)
                
                # Save analysis to database
                save_analysis(user_id, analysis_type, json.dumps(analysis_result))
                
                # Format and send the personality report
                report = format_personality_report(analysis_result)
                await processing_msg.edit_text(report, parse_mode='Markdown')
                
                # If this was a free analysis, offer subscription
                if analysis_type == "free":
                    await update.message.reply_text(get_subscription_offer_message(), parse_mode='Markdown')
                
                logger.info(f"Successfully analyzed photo for user {user_id} (type: {analysis_type})")
                
            except Exception as e:
                logger.error(f"Personality analysis error for user {user_id}: {e}")
                error_msg = get_error_message('analysis_failed')
                await processing_msg.edit_text(error_msg)
        
        except Exception as e:
            logger.error(f"Photo handling error for user {user_id}: {e}")
            try:
                error_msg = get_error_message('processing_error')
                await update.message.reply_text(error_msg)
            except:
                pass  # Avoid secondary errors
    
    async def handle_other_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle menu button messages"""
        try:
            message_text = update.message.text
            user_id = update.effective_user.id
            
            if message_text == "📸 تحلیل شخصیت":
                help_message = """📸 **آماده تحلیل شخصیت هستید!** ✨

🎯 **مراحل انجام:**
📷 عکس واضح از چهره‌تان بفرستید
✨ مطمئن شوید عکس با کیفیت و روشن باشد
👤 فقط یک چهره در تصویر باشد

🚀 **الان عکستان را بفرستید!** 💫"""
                
            elif message_text == "👑 اشتراک VIP":
                await self.vip_command(update, context)
                return
                
            elif message_text == "📊 وضعیت من":
                user = get_user(user_id)
                is_vip = is_user_vip(user_id)
                has_used_free = has_used_free_analysis(user_id)
                # Get vip_expires from user model if needed
                help_message = get_status_message(is_vip, has_used_free)
                
            elif message_text == "❓ راهنما":
                help_message = get_help_message()
                
            elif message_text == "🎯 درباره ربات":
                help_message = get_about_message()
                
            elif message_text == "📞 پشتیبانی":
                help_message = get_support_message()
                
            else:
                help_message = """📱 **از منوی زیر انتخاب کنید:** 👇

💡 روی دکمه‌های منو کلیک کنید تا به بخش مورد نظر بروید."""
            
            keyboard = get_main_menu_keyboard()
            await update.message.reply_text(
                help_message, 
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Error handling other messages: {e}")
    
    async def vip_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /vip command for subscription purchase"""
        user_id = update.effective_user.id
        
        try:
            # Check if user is already VIP
            if is_user_vip(user_id):
                await update.message.reply_text(
                    "👑 **شما الان عضو VIP هستید!** ✨\n\n📸 می‌تونید عکس‌هاتون رو بفرستید و از تحلیل‌های کامل استفاده کنید! 💎",
                    parse_mode='Markdown'
                )
                return
            
            # Send purchase message
            await update.message.reply_text(get_vip_purchase_message(), parse_mode='Markdown')
            
            # Create payment link
            success, payment_link = create_subscription_payment_link(user_id)
            
            if success:
                await update.message.reply_text(
                    f"💳 **لینک پرداخت آماده شد!** 🔗\n\n{payment_link}\n\n✅ بعد از پرداخت، بلافاصله عضو VIP می‌شوید!",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ **مشکلی در ایجاد لینک پرداخت پیش اومد!**\n\n🔄 لطفاً چند دقیقه دیگه دوباره تلاش کنید.",
                    parse_mode='Markdown'
                )
            
            logger.info(f"VIP command from user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in VIP command: {e}")
            await update.message.reply_text(
                "❌ **خطایی رخ داد!**\n\n🔄 لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
                parse_mode='Markdown'
            )

def main():
    """Main function to run the bot"""
    try:
        # Initialize bot
        bot = PersonalityBot()
        
        # Build application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", bot.start_command))
        application.add_handler(CommandHandler("vip", bot.vip_command))
        application.add_handler(MessageHandler(filters.PHOTO, bot.handle_photo))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_other_messages))
        
        logger.info("Starting Persian Personality Analysis Bot...")
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()

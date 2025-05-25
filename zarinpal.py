import requests
import json
import os
from models import SessionLocal, Payment

class ZarinPal:
    def __init__(self):
        self.merchant_id = os.getenv("ZARINPAL_MERCHANT_ID", "YOUR_MERCHANT_ID")
        self.sandbox = True  # برای تست - در محیط واقعی False کنید
        
        if self.sandbox:
            self.request_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
            self.verify_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
            self.gateway_url = "https://sandbox.zarinpal.com/pg/StartPay/"
        else:
            self.request_url = "https://api.zarinpal.com/pg/v4/payment/request.json"
            self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"
            self.gateway_url = "https://www.zarinpal.com/pg/StartPay/"
    
    def create_payment_request(self, amount: int, description: str, user_telegram_id: int, callback_url: str):
        """ایجاد درخواست پرداخت"""
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "description": description,
            "callback_url": callback_url
        }
        
        try:
            response = requests.post(self.request_url, json=data, timeout=10)
            result = response.json()
            
            if result.get("data", {}).get("code") == 100:
                authority = result["data"]["authority"]
                
                # ذخیره در دیتابیس
                db = SessionLocal()
                try:
                    payment = Payment(
                        user_telegram_id=user_telegram_id,
                        amount=amount,
                        authority=authority,
                        status="pending"
                    )
                    db.add(payment)
                    db.commit()
                finally:
                    db.close()
                
                payment_url = f"{self.gateway_url}{authority}"
                return True, payment_url, authority
            else:
                return False, "خطا در ایجاد درخواست پرداخت", None
                
        except Exception as e:
            return False, f"خطا در اتصال به درگاه پرداخت: {str(e)}", None
    
    def verify_payment(self, authority: str, amount: int):
        """تایید پرداخت"""
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority
        }
        
        try:
            response = requests.post(self.verify_url, json=data, timeout=10)
            result = response.json()
            
            if result.get("data", {}).get("code") == 100:
                ref_id = result["data"]["ref_id"]
                
                # به‌روزرسانی وضعیت پرداخت
                db = SessionLocal()
                try:
                    payment = db.query(Payment).filter(Payment.authority == authority).first()
                    if payment:
                        payment.status = "verified"
                        payment.verified_at = datetime.utcnow()
                        db.commit()
                finally:
                    db.close()
                
                return True, ref_id
            else:
                return False, "پرداخت تایید نشد"
                
        except Exception as e:
            return False, f"خطا در تایید پرداخت: {str(e)}"

def create_subscription_payment_link(user_telegram_id: int) -> tuple[bool, str]:
    """ایجاد لینک پرداخت اشتراک ماهانه"""
    zarinpal = ZarinPal()
    
    amount = 100000  # 100 هزار تومان
    description = "اشتراک ماهانه ربات تحلیل شخصیت VIP"
    callback_url = "https://your-domain.com/payment/verify"  # آدرس وب‌سایت شما
    
    success, result, authority = zarinpal.create_payment_request(
        amount=amount,
        description=description,
        user_telegram_id=user_telegram_id,
        callback_url=callback_url
    )
    
    return success, result
import httpx
import json

def test_voucher_flow():
    print("1. Creating Voucher in Database...")
    create_res = httpx.post("https://gestronomy-api.onrender.com/api/vouchers", json={
        "amount_total": 65.0,
        "customer_name": "Max Mustermann",
        "customer_email": "delivered@resend.dev",
        "notes": "Automated End-to-End Test"
    }, timeout=30.0)
    
    if create_res.status_code != 200:
        print("Failed to create voucher!", create_res.status_code, create_res.text)
        return
        
    voucher = create_res.json()
    print("✅ Created Voucher:", voucher["code"], "- Balance:", voucher["amount_total"])
    print("✅ QR Code Generated:", "Yes (Base64 string)" if voucher.get("qr_code_base64") else "No")
    
    print("\n2. Triggering Next.js Resend Dispatcher...")
    try:
        email_res = httpx.post("https://gestronomy-web.onrender.com/api/send-voucher", json={
            "customerEmail": voucher["customer_email"],
            "customerName": voucher["customer_name"],
            "amountTotal": str(voucher["amount_total"]),
            "voucherCode": voucher["code"],
            "qrCodeBase64": voucher.get("qr_code_base64"),
            "notes": voucher.get("notes")
        }, timeout=30.0)
        
        print("Response Code:", email_res.status_code)
        print("Response Body:", email_res.text)
        
        if email_res.status_code == 200:
            print("✅ Email dispatched correctly! Resend ID:", email_res.json().get("id"))
        else:
            print("❌ Email Dispatch Failed.")
            
    except Exception as e:
        print("❌ Network Error during email dispatch:", e)

if __name__ == "__main__":
    test_voucher_flow()

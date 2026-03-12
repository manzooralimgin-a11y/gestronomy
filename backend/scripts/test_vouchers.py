import httpx

def run_tests():
    print("Testing Webhooks Endpoints for Digital Vouchers...")

    base_url = "http://localhost:8002/api/vouchers"

    # Test 1: Create a Voucher
    payload = {
        "amount_total": 50.00,
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "notes": "Birthday Gift"
    }

    try:
        response = httpx.post(base_url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("✅ CREATE Voucher Success")
        print(f"   Code: {data['code']}")
        print(f"   QR Code Base64 encoded payload received: {'Yes' if data.get('qr_code_base64') else 'No'}")
        
        test_code = data['code']
    except Exception as e:
        print(f"❌ CREATE Voucher Failed: {e}")
        return

    # Test 2: Validate the Voucher
    try:
        val_response = httpx.post(f"{base_url}/validate", json={"code": test_code})
        val_response.raise_for_status()
        val_data = val_response.json()
        
        print(f"✅ VALIDATE Voucher Success:")
        print(f"   Status Valid: {val_data['valid']}")
        print(f"   Balance Remaining: {val_data['voucher']['amount_remaining']}")
    except Exception as e:
        print(f"❌ VALIDATE Voucher Failed: {e}")
        return

if __name__ == "__main__":
    run_tests()

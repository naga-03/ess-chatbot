import random
import re
from typing import Tuple, Dict, Any

class PhoneValidator:
    """Validates Indian phone numbers."""
    
    @staticmethod
    def is_valid_indian_phone(phone: str) -> bool:
        """
        Validate Indian phone number format.
        
        Accepted formats:
        - 10 digits: 9876543210
        - With +91: +919876543210
        - With +91 and dash: +91-9876543210
        - With country code: 919876543210
        """
        # Remove all non-digit characters except leading +
        if phone.startswith('+'):
            cleaned = '+' + re.sub(r'\D', '', phone)
        else:
            cleaned = re.sub(r'\D', '', phone)
        
        # Check if it matches Indian phone format
        # Indian numbers: 10 digits starting with 6-9
        indian_10_digit = re.match(r'^[6-9]\d{9}$', cleaned)
        
        # With country code +91
        with_country = re.match(r'^\+91[6-9]\d{9}$', cleaned)
        
        return bool(indian_10_digit or with_country)
    
    @staticmethod
    def format_indian_phone(phone: str) -> str:
        """Format phone number to standard Indian format: +91-XXXXXXXXXX"""
        cleaned = re.sub(r'\D', '', phone)
        
        # Get last 10 digits
        if len(cleaned) >= 10:
            last_10 = cleaned[-10:]
        else:
            return phone
        
        return f"+91-{last_10}"
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP."""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    @staticmethod
    def verify_otp(provided_otp: str, stored_otp: str) -> bool:
        """Verify if provided OTP matches stored OTP."""
        return provided_otp.strip() == stored_otp

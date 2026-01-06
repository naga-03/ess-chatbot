import json
import re
import random
import os

class ProfileManager:
    def __init__(self, data_file_path=None):
        # Determine the path to employees.json
        if data_file_path:
            self.data_file = data_file_path
        else:
            # Default to relative path: ../data/employees.json from this script
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_file = os.path.join(base_dir, 'data', 'employees.json')
            


    def _load_employees(self):
        with open(self.data_file, 'r') as f:
            return json.load(f)

    def _save_employees(self, data):
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def validate_indian_phone(self, phone_number):
        """
        Validates if the phone number is in a valid Indian format.
        Accepts: +91-9876543210, +91 9876543210, 9876543210
        """
        # Remove spaces and dashes for validation
        clean_number = re.sub(r'[\s\-]', '', phone_number)
        # Regex: Optional +91, followed by digit 6-9, then 9 digits
        pattern = r"^(\+91)?[6-9]\d{9}$"
        return bool(re.match(pattern, clean_number))

    def update_phone_number(self, employee_id, new_phone):
        """
        Updates the employee's phone number directly.
        """
        if not self.validate_indian_phone(new_phone):
            return {
                "status": "error",
                "message": "Invalid format. Please enter a valid Indian phone number (e.g., +91 9876543210)."
            }

        data = self._load_employees()
        updated = False
        for emp in data['employees']:
            if emp['employee_id'] == employee_id:
                emp['phone'] = new_phone
                updated = True
                break

        if updated:
            self._save_employees(data)
            return {"status": "success", "message": "Phone number updated successfully."}
        else:
            return {"status": "error", "message": "Employee not found."}

    def update_emergency_contact_number(self, employee_id, new_phone):
        """
        Updates the emergency contact phone number directly (no OTP required per requirements).
        """
        data = self._load_employees()
        updated = False
        for emp in data['employees']:
            if emp['employee_id'] == employee_id:
                if 'emergency_contact' in emp:
                    emp['emergency_contact']['phone'] = new_phone
                    updated = True
                break
        
        if updated:
            self._save_employees(data)
            return {"status": "success", "message": "Emergency contact number updated."}
        else:
            return {"status": "error", "message": "Employee or emergency contact not found."}

import json
import os
from typing import Optional, Dict, Any

class AuthManager:
    """Handles employee authentication and session management."""
    
    def __init__(self, employees_file: str = "data/employees.json"):
        """
        Initialize authentication manager.
        
        Args:
            employees_file: Path to employees JSON file
        """
        self.employees_file = employees_file
        self.employees = self._load_employees()
        self.logged_in_user: Optional[Dict[str, Any]] = None
    
    def _load_employees(self) -> Dict[str, Dict[str, Any]]:
        """Load employee data from JSON file."""
        if not os.path.exists(self.employees_file):
            raise FileNotFoundError(f"Employee file not found: {self.employees_file}")
        
        with open(self.employees_file, 'r') as f:
            data = json.load(f)
        
        # Create a dictionary indexed by employee_id for quick lookup
        employees_dict = {}
        for emp in data.get('employees', []):
            employees_dict[emp['employee_id']] = emp
        
        return employees_dict
    
    def login(self, employee_id: str, password: str) -> tuple[bool, str]:
        """
        Authenticate an employee.
        
        Args:
            employee_id: Employee ID
            password: Employee password
            
        Returns:
            (success: bool, message: str)
        """
        if employee_id not in self.employees:
            return False, f"Employee ID '{employee_id}' not found."
        
        employee = self.employees[employee_id]
        if employee.get('password') != password:
            return False, "Invalid password."
        
        self.logged_in_user = employee
        return True, f"Welcome, {employee['name']}!"
    
    def logout(self) -> tuple[bool, str]:
        """
        Logout the current user.
        
        Returns:
            (success: bool, message: str)
        """
        if self.logged_in_user is None:
            return False, "No user is currently logged in."
        
        user_name = self.logged_in_user['name']
        self.logged_in_user = None
        return True, f"Goodbye, {user_name}!"
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently logged in."""
        return self.logged_in_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the currently logged-in user's information."""
        return self.logged_in_user
    
    def get_current_user_id(self) -> Optional[str]:
        """Get the currently logged-in user's ID."""
        return self.logged_in_user['employee_id'] if self.logged_in_user else None
    
    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get employee information by ID."""
        return self.employees.get(employee_id)
    
    def get_all_employees(self) -> Dict[str, Dict[str, Any]]:
        """Get all employees data."""
        return self.employees

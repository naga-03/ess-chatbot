import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.auth import AuthManager
from src.entity_extractor import EntityExtractor
from data.profile_manager import ProfileManager

class BusinessLogicHandler:
    """Handles business logic for different intents."""
    
    def __init__(self, employees_file: str = "data/employees.json"):
        """
        Initialize business logic handler.
        
        Args:
            employees_file: Path to employees JSON file
        """
        self.employees_file = employees_file
        self.company_data = self._load_company_data()
        self.entity_extractor = EntityExtractor()
        self.profile_manager = ProfileManager(employees_file)
    
    def _load_company_data(self) -> Dict[str, Any]:
        """Load company data from employees file."""
        if not os.path.exists(self.employees_file):
            raise FileNotFoundError(f"Employee file not found: {self.employees_file}")
        
        with open(self.employees_file, 'r') as f:
            data = json.load(f)
        
        return {
            'employees': {emp['employee_id']: emp for emp in data.get('employees', [])},
            'company_info': data.get('company_info', {})
        }
    
    def _save_company_data(self) -> bool:
        """Save company data back to employees file."""
        try:
            # Reconstruct the employees list from the dict
            employees_list = list(self.company_data['employees'].values())
            data = {
                'employees': employees_list,
                'company_info': self.company_data['company_info']
            }
            
            with open(self.employees_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def handle_intent(self, intent_id: str, auth_manager: AuthManager, 
                     query: str = "", entities: Dict[str, Any] = None,
                     conversation_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle an intent and return response data.
        
        Args:
            intent_id: The detected intent ID
            auth_manager: Authentication manager instance
            query: The original user query
            entities: Extracted entities from the query
            conversation_state: Dictionary to manage conversation state
            
        Returns:
            Dictionary with response data
        """
        if conversation_state is None:
            conversation_state = {}

        # Handle stateful conversation for phone update
        if conversation_state.get('next_action') == 'prompt_for_phone':
            return self._handle_enter_phone_number(auth_manager, query)

        # Handle general intents
        if intent_id == "leave_policy":
            return self._handle_leave_policy()
        
        elif intent_id == "holidays":
            return self._handle_holidays()
        
        elif intent_id == "hr_contact":
            return self._handle_hr_contact()
        
        elif intent_id == "company_info":
            return self._handle_company_info()
        
        elif intent_id == "benefits":
            return self._handle_benefits()
        
        # Handle employee-specific intents
        elif intent_id == "leave_balance":
            return self._handle_leave_balance(auth_manager)
        
        elif intent_id == "check_leave_eligibility":
            return self._handle_check_leave_eligibility(auth_manager, entities or {})
        
        elif intent_id == "my_manager":
            return self._handle_my_manager(auth_manager)
        
        elif intent_id == "my_department":
            return self._handle_my_department(auth_manager)
        
        elif intent_id == "attendance":
            return self._handle_attendance(auth_manager)
        
        elif intent_id == "leave_request":
            return self._handle_leave_request(auth_manager, entities or {})
        
        elif intent_id == "salary_info":
            return self._handle_salary_info(auth_manager)
        
        elif intent_id == "payslip":
            return self._handle_payslip(auth_manager)
        
        elif intent_id == "tax_info":
            return self._handle_tax_info(auth_manager)
        
        elif intent_id == "leave_history":
            return self._handle_leave_history(auth_manager)
        
        elif intent_id == "leave_approval":
            return self._handle_leave_approval(auth_manager)
        
        elif intent_id == "birthday_anniversary":
            return self._handle_birthday_anniversary(auth_manager)
        
        elif intent_id == "skills":
            return self._handle_skills(auth_manager)
        
        elif intent_id == "appraisal_cycle":
            return self._handle_appraisal_cycle(auth_manager)
        
        elif intent_id == "goals_objectives":
            return self._handle_goals_objectives(auth_manager)
        
        elif intent_id == "update_phone":
            return self._handle_update_phone(auth_manager)

        elif intent_id == "enter_phone_number":
            return self._handle_enter_phone_number(auth_manager, query)



        elif intent_id == "update_emergency_contact":
            return self._handle_update_emergency_contact(auth_manager, query)

        elif intent_id == "greeting":
            return self._handle_greeting()

        elif intent_id == "my_profile":
            return self._handle_my_profile(auth_manager)

        elif intent_id == "general_inquiry":
            return self._handle_general_inquiry()

        else:
            return {
                'success': False,
                'data': None,
                'message': f'Intent "{intent_id}" is not implemented yet.'
            }
    
    # General intent handlers
    def _handle_leave_policy(self) -> Dict[str, Any]:
        """Handle leave policy query."""
        policy = {
            'annual_leave': 20,
            'sick_leave': 10,
            'casual_leave': 5,
            'maternity_leave': 90,
            'paternity_leave': 10
        }
        policy_details = [
            f"Annual Leave: {policy['annual_leave']} days",
            f"Sick Leave: {policy['sick_leave']} days",
            f"Casual Leave: {policy['casual_leave']} days",
            f"Maternity Leave: {policy['maternity_leave']} days",
            f"Paternity Leave: {policy['paternity_leave']} days"
        ]
        return {
            'success': True,
            'data': {'policy': policy},
            'message': f"Our leave policy includes:\n{chr(10).join([f'• {detail}' for detail in policy_details])}"
        }
    
    def _handle_holidays(self) -> Dict[str, Any]:
        """Handle company holidays query."""
        holidays = self.company_data['company_info'].get('holidays', [])
        if holidays:
            holiday_list = [f"• {holiday}" for holiday in holidays]
            return {
                'success': True,
                'data': {'holidays': holidays},
                'message': f'Company holidays this year:\n{chr(10).join(holiday_list)}'
            }
        else:
            return {
                'success': True,
                'data': {'holidays': holidays},
                'message': 'No company holidays are currently scheduled for this year.'
            }
    
    def _handle_hr_contact(self) -> Dict[str, Any]:
        """Handle HR contact query."""
        company_info = self.company_data['company_info']
        hr_phone = company_info.get('hr_phone', 'Not available')
        hr_email = company_info.get('hr_email', 'Not available')
        return {
            'success': True,
            'data': {
                'hr_phone': hr_phone,
                'hr_email': hr_email
            },
            'message': f'HR Contact Information:\n• Phone: {hr_phone}\n• Email: {hr_email}'
        }
    
    def _handle_company_info(self) -> Dict[str, Any]:
        """Handle company information query."""
        company_info = self.company_data['company_info']
        name = company_info.get('name', 'Not available')
        mission = company_info.get('mission', 'Not available')
        return {
            'success': True,
            'data': {
                'name': name,
                'mission': mission
            },
            'message': f'Company Information:\n• Name: {name}\n• Mission: {mission}'
        }
    
    def _handle_benefits(self) -> Dict[str, Any]:
        """Handle employee benefits query."""
        benefits = {
            'health_insurance': 'Comprehensive health insurance coverage',
            'retirement_plan': '401(k) matching up to 5%',
            'pto': 'Paid time off (20 days annually)',
            'professional_development': 'Annual training budget of $2000',
            'remote_work': 'Flexible remote work policy'
        }
        benefits_list = [f"• {desc}" for desc in benefits.values()]
        return {
            'success': True,
            'data': {'benefits': benefits},
            'message': f'Here are the available employee benefits:\n{chr(10).join(benefits_list)}'
        }
    
    # Employee-specific intent handlers
    def _handle_leave_balance(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle leave balance query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to check your leave balance.'
            }
        
        leave_balance = user.get('leave_balance', {})
        
        # Handle both old format (single number) and new format (dict by type)
        if isinstance(leave_balance, dict):
            total = leave_balance.get('total', 0)
            return {
                'success': True,
                'data': {
                    'employee_id': user['employee_id'],
                    'name': user['name'],
                    'leave_balance': leave_balance
                },
                'message': f"{user['name']}, you have a total of {total} leaves remaining. Breakdown: Sick ({leave_balance.get('sick', 0)}), Casual ({leave_balance.get('casual', 0)}), Earned ({leave_balance.get('earned', 0)})."
            }
        else:
            # Old format compatibility
            return {
                'success': True,
                'data': {
                    'employee_id': user['employee_id'],
                    'name': user['name'],
                    'leave_balance': leave_balance
                },
                'message': f"{user['name']}, you have {leave_balance} leaves remaining."
            }
    
    def _handle_check_leave_eligibility(self, auth_manager: AuthManager, 
                                       entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle leave eligibility check."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to check your leave eligibility.'
            }
        
        # Extract leave type from entities or query
        leave_types = entities.get('leave_types', [])
        leave_type = leave_types[0] if leave_types else 'general'
        
        leave_balance = user.get('leave_balance', {})
        
        # Handle both old and new format
        if isinstance(leave_balance, dict):
            available = leave_balance.get(leave_type, 0)
            total = leave_balance.get('total', 0)
            
            if available > 0:
                return {
                    'success': True,
                    'data': {
                        'employee_name': user['name'],
                        'leave_type': leave_type,
                        'available_leaves': available,
                        'eligible': True
                    },
                    'message': f"Yes, you are eligible to take {leave_type} leave. You have {available} {leave_type} leave(s) available."
                }
            else:
                return {
                    'success': True,
                    'data': {
                        'employee_name': user['name'],
                        'leave_type': leave_type,
                        'available_leaves': 0,
                        'eligible': False
                    },
                    'message': f"Sorry, you do not have any {leave_type} leave available at the moment."
                }
        else:
            # Old format - just check if they have any leaves
            if leave_balance > 0:
                return {
                    'success': True,
                    'data': {
                        'employee_name': user['name'],
                        'leave_type': leave_type,
                        'available_leaves': leave_balance,
                        'eligible': True
                    },
                    'message': f"Yes, you are eligible to take {leave_type} leave. You have {leave_balance} leave(s) available."
                }
            else:
                return {
                    'success': True,
                    'data': {
                        'employee_name': user['name'],
                        'leave_type': leave_type,
                        'available_leaves': 0,
                        'eligible': False
                    },
                    'message': f"Sorry, you do not have any {leave_type} leave available at the moment."
                }
    
    def _handle_my_manager(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle my manager query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to check your manager.'
            }
        
        manager_name = user['manager']
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'manager': manager_name
            },
            'message': f'Your manager is {manager_name}.' if manager_name else 'You do not have a manager (you are the head).'
        }
    
    def _handle_my_department(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle my department query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to check your department.'
            }
        
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'department': user['department']
            },
            'message': f"You work in the {user['department']} department."
        }
    
    def _handle_attendance(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle attendance query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to check your attendance.'
            }

        attendance_days = user.get('attendance_days', 0)
        attendance_percentage = (attendance_days / 250) * 100 if attendance_days > 0 else 0  # Assuming 250 working days
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'attendance_days': attendance_days,
                'attendance_percentage': attendance_percentage
            },
            'message': f"You have been present for {attendance_days} days ({attendance_percentage:.1f}% attendance)."
        }
    
    def _handle_leave_request(self, auth_manager: AuthManager, 
                             entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle leave request."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to apply for leave.'
            }
        
        # Parse leave request from entities
        leave_type = entities.get('leave_types', ['casual'])[0] if entities.get('leave_types') else 'casual'
        start_date = entities.get('dates', ['not specified'])[0] if entities.get('dates') else 'not specified'
        duration = entities.get('leave_duration', {}).get('days', 1)
        
        return {
            'success': True,
            'data': {
                'employee_id': user['employee_id'],
                'employee_name': user['name'],
                'leave_type': leave_type,
                'start_date': start_date,
                'duration_days': duration,
                'status': 'pending_approval',
                'submitted_at': datetime.now().isoformat()
            },
            'message': f'Your {leave_type} leave request for {start_date} ({duration} days) has been submitted for approval.'
        }
    
    def _handle_salary_info(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle salary information query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to check your salary.'
            }
        
        salary = user.get('salary', 0)
        monthly_salary = salary / 12
        
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'annual_salary': salary,
                'monthly_salary': monthly_salary
            },
            'message': f'Your annual salary is ${salary:,.2f} (${monthly_salary:,.2f} monthly).'
        }
    
    def _handle_payslip(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle payslip query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to view payslips.'
            }
        
        payslips = user.get('payslips', [])
        if not payslips:
            return {
                'success': True,
                'data': None,
                'message': 'No payslips available.'
            }
        
        latest_payslip = payslips[0]
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'payslips': payslips
            },
            'message': f"Latest payslip ({latest_payslip['month']}): Gross ${latest_payslip['gross_salary']:,.2f}, Deductions ${latest_payslip['deductions']:,.2f}, Net ${latest_payslip['net_salary']:,.2f}"
        }
    
    def _handle_tax_info(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle tax calculation query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to view tax information.'
            }
        
        tax_info = user.get('tax_calculation', {})
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'tax_info': tax_info
            },
            'message': f"Tax for {tax_info.get('year')}: Gross income ${tax_info.get('gross_income'):,.2f}, Tax deducted ${tax_info.get('tax_deducted'):,.2f} ({tax_info.get('tax_rate')})"
        }
    
    def _handle_leave_history(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle leave history query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to view leave history.'
            }
        
        leave_history = user.get('leave_history', [])
        if not leave_history:
            return {
                'success': True,
                'data': None,
                'message': 'You have no leave history for this year.'
            }
        
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'leave_history': leave_history,
                'total_leaves_taken': sum(l['days'] for l in leave_history)
            },
            'message': f"You have taken {sum(l['days'] for l in leave_history)} leave days. Total records: {len(leave_history)}"
        }
    
    def _handle_leave_approval(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle leave approval status query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to check leave approval.'
            }
        
        leave_history = user.get('leave_history', [])
        pending = [l for l in leave_history if l['status'] == 'pending']
        approved = [l for l in leave_history if l['status'] == 'approved']
        
        if pending:
            pending_info = ", ".join([f"{l['type']} ({l['days']} days)" for l in pending])
            return {
                'success': True,
                'data': {
                    'employee_name': user['name'],
                    'pending_leaves': pending,
                    'approved_leaves': approved
                },
                'message': f"You have {len(pending)} pending leave(s): {pending_info}"
            }
        else:
            return {
                'success': True,
                'data': {
                    'employee_name': user['name'],
                    'approved_leaves': approved
                },
                'message': f"All your {len(approved)} leave request(s) have been approved."
            }
    
    def _handle_birthday_anniversary(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle birthday and anniversary query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to view your dates.'
            }
        
        birthday = user.get('birthday', 'Not provided')
        anniversary = user.get('anniversary', 'Not provided')
        
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'birthday': birthday,
                'anniversary': anniversary
            },
            'message': f"Birthday: {birthday}, Work Anniversary: {anniversary}"
        }
    
    def _handle_skills(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle skills query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to view your skills.'
            }
        
        skills = user.get('skills', [])
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'skills': skills
            },
            'message': f"Your skills: {', '.join(skills)}"
        }
    
    def _handle_appraisal_cycle(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle appraisal cycle query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to check appraisal cycle.'
            }
        
        appraisal_cycle = user.get('appraisal_cycle', 'Not scheduled')
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'appraisal_cycle': appraisal_cycle
            },
            'message': f"Your appraisal cycle: {appraisal_cycle}"
        }
    
    def _handle_goals_objectives(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle goals and objectives query."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to view your goals.'
            }

        goals = user.get('goals', [])
        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'goals': goals
            },
            'message': f"Your goals: {chr(10).join([f'• {g}' for g in goals])}"
        }

    def _handle_update_phone(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle phone update initiation."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to update your phone number.'
            }

        return {
            'success': True,
            'data': {
                'employee_name': user['name']
            },
            'message': 'Contact HR or see your profile for phone number updates.'
        }

    def _handle_enter_phone_number(self, auth_manager: AuthManager, query: str) -> Dict[str, Any]:
        """Handle phone number entry."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to update your phone number.'
            }

        # Extract phone number from query
        entities = self.entity_extractor.extract_entities(query)
        phone_numbers = entities.get('phone_numbers', [])

        if not phone_numbers:
            return {
                'success': False,
                'data': None,
                'message': 'Please provide the new phone number.'
            }

        new_phone = phone_numbers[0]

        # Validate phone number
        from src.phone_validator import PhoneValidator
        validator = PhoneValidator()
        if not validator.validate_phone(new_phone):
            return {
                'success': False,
                'data': None,
                'message': 'Invalid phone number format. Please use +91 followed by 10 digits.'
            }

        # Update phone number directly without OTP
        result = self.profile_manager.update_phone_number(user['employee_id'], new_phone)
        if result['status'] == 'success':
            return {
                'success': True,
                'data': {
                    'employee_name': user['name'],
                    'updated_phone': new_phone
                },
                'message': f'Phone number updated successfully to {new_phone}.'
            }
        else:
            return {
                'success': False,
                'data': None,
                'message': result['message']
            }



    def _handle_update_emergency_contact(self, auth_manager: AuthManager, query: str) -> Dict[str, Any]:
        """Handle emergency contact update."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to update your emergency contact.'
            }

        # Extract phone number from query
        entities = self.entity_extractor.extract_entities(query)
        phone_numbers = entities.get('phone_numbers', [])

        if not phone_numbers:
            return {
                'success': False,
                'data': None,
                'message': 'Please provide the new emergency contact phone number.'
            }

        new_emergency_contact = phone_numbers[0]

        # Validate phone number
        from src.phone_validator import PhoneValidator
        validator = PhoneValidator()
        if not validator.validate_phone(new_emergency_contact):
            return {
                'success': False,
                'data': None,
                'message': 'Invalid phone number format. Please use +91 followed by 10 digits.'
            }

        # Update emergency contact
        result = self.profile_manager.update_emergency_contact_number(user['employee_id'], new_emergency_contact)
        if result['status'] == 'success':
            return {
                'success': True,
                'data': {
                    'employee_name': user['name'],
                    'updated_emergency_contact': new_emergency_contact
                },
                'message': f'Emergency contact updated successfully to {new_emergency_contact}.'
            }
        else:
            return {
                'success': False,
                'data': None,
                'message': result['message']
            }

    def _handle_enter_emergency_contact(self, auth_manager: AuthManager, query: str) -> Dict[str, Any]:
        """Handle emergency contact entry (alternative flow)."""
        return self._handle_update_emergency_contact(auth_manager, query)

    def _handle_greeting(self) -> Dict[str, Any]:
        """Handle greeting queries."""
        greetings = [
            "Hello! I'm your Employee Self-Service assistant. How can I help you today?",
            "Hi there! I'm here to assist you with your employee-related queries.",
            "Greetings! I'm your ESS chatbot. What can I do for you?",
            "Hello! Welcome to the Employee Self-Service system. How may I assist you?"
        ]
        import random
        return {
            'success': True,
            'data': {'greeting_type': 'general'},
            'message': random.choice(greetings)
        }

    def _handle_my_profile(self, auth_manager: AuthManager) -> Dict[str, Any]:
        """Handle my profile queries."""
        user = auth_manager.get_current_user()
        if not user:
            return {
                'success': False,
                'data': None,
                'message': 'You must be logged in to view your profile information.'
            }

        profile_info = {
            'employee_id': user['employee_id'],
            'name': user['name'],
            'department': user['department'],
            'manager': user.get('manager', 'Not assigned'),
            'phone': user.get('phone', 'Not provided'),
            'email': user.get('email', 'Not provided')
        }

        return {
            'success': True,
            'data': {
                'employee_name': user['name'],
                'profile_info': profile_info
            },
            'message': f"Hello {user['name']}! Your Employee ID is {user['employee_id']}, you work in {user['department']} department, and your manager is {user.get('manager', 'Not assigned')}."
        }

    def _handle_general_inquiry(self) -> Dict[str, Any]:
        """Handle general inquiry about chatbot capabilities."""
        capabilities = [
            "leave balance and eligibility",
            "leave requests and history",
            "salary and payslip information",
            "profile and personal details",
            "company policies and benefits",
            "HR contact information",
            "phone number updates",
            "attendance records"
        ]

        return {
            'success': True,
            'data': {'capabilities': capabilities},
            'message': f"I can help you with various employee-related tasks including: {', '.join(capabilities)}. You can ask me questions like 'How many leaves do I have?', 'What is my salary?', or 'Update my phone number'. If you need help with something specific, just let me know!"
        }
    




                

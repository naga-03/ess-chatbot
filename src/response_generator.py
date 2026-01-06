from typing import Dict, Any, Optional
import json
import os

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables
    GEMINI_AVAILABLE = bool(os.getenv('GOOGLE_API_KEY'))
except ImportError:
    GEMINI_AVAILABLE = False

class LLMResponseGenerator:
    """Generates natural language responses using Gemini LLM or business logic fallback."""

    def __init__(self, gemini_model: str = "gemini-2.5-flash-lite"):
        """
        Initialize the LLM response generator.

        Args:
            gemini_model: Name of Gemini model to use
        """
        self.gemini_model = gemini_model
        self.use_llm = GEMINI_AVAILABLE

        # Initialize Gemini if available
        if GEMINI_AVAILABLE:
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

    def generate_response(self, intent: Dict[str, Any], entities: Dict[str, Any],
                         user_data: Optional[Dict[str, Any]] = None,
                         conversation_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a natural language response using Gemini or business logic fallback.

        Args:
            intent: Detected intent information
            entities: Extracted entities
            user_data: User-specific data (if authenticated)
            conversation_context: Previous conversation context

        Returns:
            Natural language response string
        """
        intent_id = intent.get('intent_id', '')

        # Use business logic only for intents that require precise data operations
        # Allow Gemini to handle most intents for better natural language responses
        business_logic_only_intents = [
            'leave_request', 'update_phone', 'enter_phone_number',
            'update_emergency_contact', 'enter_emergency_contact'
        ]

        # Use Gemini for all intents when available, except for data operation intents
        print(f"Using LLM: {self.use_llm}")
        if self.use_llm and intent_id not in business_logic_only_intents:
            try:
                return self._generate_gemini_response(intent, entities, user_data, conversation_context)
            except Exception as e:
                print(f"Gemini failed, falling back to business logic: {e}")
                return self._get_business_logic_response(intent, user_data)
        else:
            # Use business logic for data operations or when Gemini is not available
            return self._get_business_logic_response(intent, user_data)

    def _build_context(self, intent: Dict[str, Any], entities: Dict[str, Any],
                      user_data: Optional[Dict[str, Any]], conversation_context: Optional[Dict[str, Any]]) -> str:
        """Build context information for the LLM prompt."""

        context_parts = []

        # Intent information
        context_parts.append(f"Intent: {intent.get('name', 'Unknown')} ({intent.get('intent_id', 'unknown')})")

        # User authentication status
        if user_data:
            context_parts.append(f"User: {user_data.get('name', 'Unknown')} (ID: {user_data.get('employee_id', 'Unknown')})")
        else:
            context_parts.append("User: Not authenticated")

        # Entity information
        if entities:
            entity_info = []
            if entities.get('dates'):
                entity_info.append(f"Dates mentioned: {', '.join(entities['dates'])}")
            if entities.get('leave_duration', {}).get('days'):
                entity_info.append(f"Leave duration: {entities['leave_duration']['days']} days")
            if entities.get('leave_duration', {}).get('weeks'):
                entity_info.append(f"Leave duration: {entities['leave_duration']['weeks']} weeks")
            if entities.get('leave_types'):
                entity_info.append(f"Leave types: {', '.join(entities['leave_types'])}")
            if entities.get('phone_number'):
                entity_info.append(f"Phone number: {entities['phone_number']}")


            if entity_info:
                context_parts.append("Entities extracted: " + "; ".join(entity_info))

        # Conversation context
        if conversation_context:
            context_parts.append(f"Conversation state: {json.dumps(conversation_context)}")

        # Add specific business logic data based on intent
        intent_id = intent.get('intent_id')
        if intent_id == 'leave_balance' and user_data:
            leave_balance = user_data.get('leave_balance', {})
            context_parts.append(f"User's leave balance: {json.dumps(leave_balance)}")

        elif intent_id == 'my_manager' and user_data:
            manager = user_data.get('manager', 'Not specified')
            context_parts.append(f"User's manager: {manager}")

        elif intent_id == 'my_department' and user_data:
            department = user_data.get('department', 'Not specified')
            context_parts.append(f"User's department: {department}")

        elif intent_id == 'salary_info' and user_data:
            salary = user_data.get('salary', 'Not specified')
            context_parts.append(f"User's salary: {salary}")

        elif intent_id == 'holidays':
            # Load company holidays from data
            try:
                with open('data/employees.json', 'r') as f:
                    company_data = json.load(f)
                holidays = company_data.get('company_info', {}).get('holidays', [])
                context_parts.append(f"Company holidays: {json.dumps(holidays)}")
            except Exception as e:
                context_parts.append("Company holidays: Not available")

        elif intent_id == 'hr_contact':
            # Load HR contact from data
            try:
                with open('data/employees.json', 'r') as f:
                    company_data = json.load(f)
                hr_info = company_data.get('company_info', {})
                hr_phone = hr_info.get('hr_phone', 'Not available')
                hr_email = hr_info.get('hr_email', 'Not available')
                context_parts.append(f"HR contact - Phone: {hr_phone}, Email: {hr_email}")
            except Exception as e:
                context_parts.append("HR contact: Not available")

        elif intent_id == 'company_info':
            # Load company info from data
            try:
                with open('data/employees.json', 'r') as f:
                    company_data = json.load(f)
                company_info = company_data.get('company_info', {})
                name = company_info.get('name', 'Not specified')
                mission = company_info.get('mission', 'Not specified')
                context_parts.append(f"Company name: {name}, Mission: {mission}")
            except Exception as e:
                context_parts.append("Company info: Not available")

        # Include full user profile for profile-related intents
        if intent_id in ['my_profile', 'birthday_anniversary', 'skills', 'appraisal_cycle', 'goals_objectives'] and user_data:
            context_parts.append(f"User profile data: {json.dumps(user_data)}")

        return "\n".join(context_parts)

    def _generate_gemini_response(self, intent: Dict[str, Any], entities: Dict[str, Any],
                                 user_data: Optional[Dict[str, Any]], conversation_context: Optional[Dict[str, Any]]) -> str:
        """Generate response using Google Gemini."""
        print("Trying Gemini")
        try:
            # Build context for the LLM
            context = self._build_context(intent, entities, user_data, conversation_context)

            prompt = f"""You are a helpful Employee Self-Service chatbot for a company. You have access to specific employee data and must use it to provide accurate responses.

{context}

IMPORTANT: Answer ONLY the specific question asked by the user. Do not provide comprehensive profile information unless specifically asked. Use the exact data provided in the context above to give a direct, concise answer.

For example:
- If asked "Who is my manager?", respond with just the manager's name
- If asked "What is my department?", respond with just the department name
- If asked for leave balance, provide only the leave information
- If asked for holidays, list only the holiday dates

Respond naturally but keep it focused on the specific query. Use the actual data from the context."""

            model = genai.GenerativeModel(self.gemini_model)
            response = model.generate_content(prompt)

            return response.text.strip()

        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            # Fall back to business logic
            return self._get_business_logic_response(intent, user_data)

    def _get_business_logic_response(self, intent: Dict[str, Any], user_data: Optional[Dict[str, Any]] = None) -> str:
        """Get a response using business logic handlers with enhanced natural language fallbacks."""
        from src.business_logic import BusinessLogicHandler
        from src.auth import AuthManager

        intent_id = intent.get('intent_id', 'unknown')

        # Initialize business logic handler
        business_logic = BusinessLogicHandler()

        # Create a mock auth manager with the user data
        class MockAuthManager:
            def __init__(self, user_data):
                self.current_user = user_data

            def get_current_user(self):
                return self.current_user

        auth_manager = MockAuthManager(user_data)

        # Handle the intent using business logic
        try:
            result = business_logic.handle_intent(intent_id, auth_manager)
            return result.get('message', "I'm here to help with your employee-related questions.")
        except Exception as e:
            print(f"Error in business logic: {e}")
            # Enhanced fallback responses with more natural language
            fallbacks = {
                'greeting': "Hello! I'm your friendly Employee Self-Service assistant. I'm here to help you with all your work-related questions and tasks. How can I assist you today?",
                'leave_policy': "I'd be happy to help you understand our leave policy! We offer several types of leave including annual leave (usually 20 days), sick leave (10 days), casual leave (5 days), and maternity/paternity leave. Each type has specific rules and eligibility criteria. Would you like me to explain any particular type in more detail?",
                'holidays': "I'd love to share our company holiday calendar with you! We celebrate various national and cultural holidays throughout the year. This helps ensure everyone gets time to rest and spend with family. Would you like me to show you the complete list of holidays for this year?",
                'hr_contact': "For any HR-related questions or concerns, our dedicated HR team is always ready to help. You can reach them through multiple channels - by phone, email, or in person. I can provide the specific contact details if you'd like. Is there something specific you'd like to discuss with HR?",
                'company_info': "I'm excited to tell you about our wonderful company! We're committed to creating a positive work environment where every employee can thrive and grow. Our mission is to deliver exceptional value to our customers while supporting our team's professional development. We believe in work-life balance, innovation, and continuous learning. Is there a specific aspect of the company you'd like to know more about?",
                'benefits': "We offer a comprehensive and competitive benefits package designed to support your well-being and financial security. This includes health insurance coverage, retirement savings plans, paid time off, professional development opportunities, and various perks. Each benefit is carefully chosen to help you focus on what matters most. Would you like me to elaborate on any specific benefit or compare options?",
                'general_inquiry': "I'm your go-to assistant for all things related to employee services! I can help you with leave management, salary information, company policies, HR contacts, and much more. For personal details like your profile or leave balance, you'll need to log in first. What would you like to know? Feel free to ask me anything - I'm here to make your work life easier!",
                'leave_balance': "I can help you check your current leave balance once you're logged in. This includes your annual leave, sick leave, and other leave types. Knowing your balance helps you plan your time off effectively. Would you like me to guide you through checking your leave balance?",
                'my_manager': "I can tell you about your reporting manager and their contact information once you're logged in. Your manager plays an important role in your professional development and day-to-day guidance. Would you like me to show you how to find your manager's details?",
                'my_department': "Your department information is an important part of your employee profile. It shows which team you belong to and helps coordinate work activities. I can display this information for you once you're logged in. Would you like to see your department details?",
                'attendance': "Tracking your attendance helps both you and the company monitor work patterns and ensure accurate payroll processing. I can show you your attendance record, including days present and any patterns. This information is available once you're logged in. Would you like me to help you check your attendance?",
                'salary_info': "Your salary information is confidential and secure. I can show you your current salary, breakdown of components, and payment schedule once you're logged in. This helps you understand your compensation structure. Would you like me to guide you through viewing your salary details?",
                'payslip': "Payslips contain important information about your earnings, deductions, and net pay. I can help you view your latest payslip or historical payslips once you're logged in. This ensures transparency in your compensation. Would you like me to show you how to access your payslips?",
                'leave_history': "Your leave history shows all the leave you've taken throughout the year, including dates, types, and approval status. This helps you track your leave usage and plan future time off. I can display this information once you're logged in. Would you like to review your leave history?",
                'leave_approval': "Checking your leave approval status helps you know whether your time off requests have been approved. I can show you the status of pending, approved, and rejected leave requests once you're logged in. This keeps you informed about your leave plans. Would you like me to check your leave approval status?",
                'birthday_anniversary': "Important dates like your birthday and work anniversary are special milestones! I can show you these dates along with other important reminders once you're logged in. This helps you celebrate these occasions. Would you like to see your important dates?",
                'skills': "Your skills and competencies are valuable assets that contribute to your professional growth. I can display your skill set as recorded in our HRMS once you're logged in. This helps you understand your strengths and areas for development. Would you like to review your skills?",
                'appraisal_cycle': "Performance appraisals are important for your career development. I can show you the current appraisal cycle schedule, timelines, and your progress once you're logged in. This helps you prepare and track your performance reviews. Would you like to check the appraisal cycle information?",
                'goals_objectives': "Your goals and objectives (OKRs) guide your work and measure your achievements. I can display your current goals, progress, and targets once you're logged in. This helps you stay focused and motivated. Would you like to review your goals and objectives?",
                'update_phone': "Keeping your contact information current is important for effective communication. I can help you update your phone number securely once you're logged in. This ensures you receive important notifications and updates. Would you like me to guide you through updating your phone number?",
                'show_emergency_contact': "Your emergency contact information is crucial for safety and security purposes. I can display your current emergency contact details once you're logged in. This helps ensure we can reach someone in case of emergencies. Would you like to view your emergency contact information?",
                'update_emergency_contact': "Updating your emergency contact ensures we have accurate information for urgent situations. I can help you change your emergency contact details securely once you're logged in. This is important for your safety. Would you like me to help you update your emergency contact?",
                'my_profile': "Your employee profile contains all your important work-related information in one place. I can show you your complete profile including personal details, job information, and contact details once you're logged in. This gives you a comprehensive view of your employment information. Would you like to see your profile?",
                'leave_request': "Applying for leave is easy and straightforward! I can guide you through the process of submitting a leave request once you're logged in. This includes selecting dates, leave type, and providing a reason. Would you like me to help you apply for leave?",
                'tax_info': "Tax information is important for financial planning. I can show you your tax calculations, deductions, and related details once you're logged in. This helps you understand your tax obligations and plan accordingly. Would you like to review your tax information?"
            }
            return fallbacks.get(intent_id, "I'm here to help with your employee-related questions and make your work life easier. I can assist with leave management, salary information, company policies, and much more. For personal information, please log in first. What would you like to know?")

from typing import Dict, Any, Optional, Tuple
from src.auth import AuthManager
from src.intent_detector import IntentDetector
from src.entity_extractor import EntityExtractor
from src.business_logic import BusinessLogicHandler
from src.response_generator import LLMResponseGenerator

class ESSChatbot:
    """Main chatbot orchestrator for Employee Self-Service."""

    def __init__(self,
                 employees_file: str = "data/employees.json",
                 intents_file: str = "config/intents.json",
                 model_name: str = "llama2",
                 gemini_model: str = "gemini-2.5-flash-lite"):
        """
        Initialize the ESS Chatbot.

        Args:
            employees_file: Path to employees database
            intents_file: Path to intents configuration
            model_name: Name of Ollama model to use
            gemini_model: Name of Gemini model to use
        """
        self.auth_manager = AuthManager(employees_file)
        self.intent_detector = IntentDetector(intents_file, model_name)
        self.entity_extractor = EntityExtractor(model_name)
        self.business_logic = BusinessLogicHandler(employees_file)
        self.response_generator = LLMResponseGenerator(gemini_model)
        self.conversation_state: Dict[str, Any] = {}
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            user_input: The user's message
            
        Returns:
            Dictionary with response details
        """
        # Special commands
        if user_input.lower().startswith("/login"):
            return self._handle_login_command(user_input)
        
        if user_input.lower() == "/logout":
            return self._handle_logout_command()
        
        if user_input.lower() == "/help":
            return self._handle_help_command()
        
        if user_input.lower() == "/status":
            return self._handle_status_command()
        
        # Regular query processing
        return self._process_query(user_input)
    
    def _process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a regular user query.
        
        Args:
            query: User query
            
        Returns:
            Response dictionary
        """
        # Step 1: Detect intent
        intent, confidence = self.intent_detector.get_intent(query, threshold=0.5)

        if intent is None:
            # When intent detection fails, use Gemini for general queries if available
            entities = {}
            user_data = None
            if self.auth_manager.is_authenticated():
                user_data = self.auth_manager.get_current_user()

            # Try to generate a response using Gemini for unrecognized queries
            try:
                gemini_response = self.response_generator.generate_response(
                    {'intent_id': 'general_inquiry', 'name': 'General Inquiry'},
                    entities, user_data, self.conversation_state
                )
                return {
                    'success': True,
                    'intent': 'general_inquiry',
                    'entities': entities,
                    'message': gemini_response,
                    'requires_auth': False
                }
            except Exception as e:
                print(f"Gemini fallback failed: {e}")
                return {
                    'success': False,
                    'intent': None,
                    'entities': {},
                    'message': "I couldn't understand your query. Could you rephrase that?"
                }
        
        # Step 2: Extract entities
        entities = self.entity_extractor.extract_entities(query)
        
        # Step 3: Check permissions for private intents
        intent_id = intent['intent_id']
        is_private = self.intent_detector.is_private_intent(intent_id)
        
        if is_private and not self.auth_manager.is_authenticated():
            return {
                'success': False,
                'intent': intent_id,
                'entities': entities,
                'message': f"This information is private. Please login first using /login <employee_id> <password>"
            }
        
        # Step 4: Get user data for authenticated requests
        user_data = None
        if self.auth_manager.is_authenticated():
            user_data = self.auth_manager.get_current_user()

        # Step 5: Handle business logic for state management and data operations
        business_response = self.business_logic.handle_intent(
            intent_id, self.auth_manager, query, entities, self.conversation_state
        )

        # Step 6: Generate natural language response using LLM for generic intents, business logic for employee-specific
        final_message = self.response_generator.generate_response(
            intent, entities, user_data, self.conversation_state
        )

        # Step 7: Update conversation state
        if business_response.get('data') and business_response['data'].get('next_action'):
            self.conversation_state['next_action'] = business_response['data']['next_action']
            if 'new_phone' in business_response['data']:
                self.conversation_state['new_phone'] = business_response['data']['new_phone']
        else:
            # Clear state if conversation is over
            self.conversation_state = {}

        return {
            'success': business_response.get('success', True),  # Default to success for LLM responses
            'intent': intent_id,
            'intent_name': intent.get('name'),
            'confidence': float(confidence),
            'entities': entities,
            'data': business_response.get('data'),
            'message': final_message,
            'requires_auth': is_private
        }
    
    def _handle_login_command(self, command: str) -> Dict[str, Any]:
        """Handle /login command."""
        parts = command.split()
        
        if len(parts) < 3:
            return {
                'success': False,
                'message': 'Usage: /login <employee_id> <password>'
            }
        
        employee_id = parts[1]
        password = parts[2]
        
        success, message = self.auth_manager.login(employee_id, password)
        
        return {
            'success': success,
            'message': message,
            'user': self.auth_manager.get_current_user()
        }
    
    def _handle_logout_command(self) -> Dict[str, Any]:
        """Handle /logout command."""
        success, message = self.auth_manager.logout()
        
        return {
            'success': success,
            'message': message
        }
    
    def _handle_help_command(self) -> Dict[str, Any]:
        """Handle /help command."""
        help_text = """
**Available Commands:**
- /login <employee_id> <password> - Login to your account
- /logout - Logout from your account
- /status - Check login status
- /help - Show this help message

**General Queries (No login required):**
- What is the leave policy?
- When are the company holidays?
- How do I contact HR?
- Tell me about the company
- What benefits are available?

**Employee-Specific Queries (Login required):**
- How many leaves do I have?
- Who is my manager?
- What is my department?
- What is my attendance record?
- I want to apply for leave
- What is my salary?
- What is my emergency contact?

**Demo Login Credentials:**
- Employee ID: E001, Password: pass123
- Employee ID: E002, Password: pass456
- Employee ID: E003, Password: pass789
"""
        return {
            'success': True,
            'message': help_text
        }
    
    def _handle_status_command(self) -> Dict[str, Any]:
        """Handle /status command."""
        if self.auth_manager.is_authenticated():
            user = self.auth_manager.get_current_user()
            return {
                'success': True,
                'message': f"Logged in as: {user['name']} ({user['employee_id']})"
            }
        else:
            return {
                'success': True,
                'message': "Not logged in. Use /login <employee_id> <password> to login."
            }
    
    def get_available_intents(self) -> Dict[str, list]:
        """Get available intents grouped by category."""
        return {
            'general': self.intent_detector.get_general_intents(),
            'employee_specific': self.intent_detector.get_employee_intents()
        }

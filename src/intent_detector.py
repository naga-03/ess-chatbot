import json
import os
import re
from typing import List, Dict, Any, Tuple, Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class IntentDetector:
    """Detects user intent using keyword matching."""

    def __init__(self, intents_file: str = "config/intents.json", model_name: str = "llama2"):
        """
        Initialize intent detector with keyword matching.

        Args:
            intents_file: Path to intents JSON file
            model_name: Name of Ollama model to use (deprecated)
        """
        self.intents_file = intents_file
        self.model_name = model_name
        self.intents = self._load_intents()
        self.use_llm = False  # Always use keyword matching

    def _load_intents(self) -> List[Dict[str, Any]]:
        """Load intents from JSON file."""
        if not os.path.exists(self.intents_file):
            raise FileNotFoundError(f"Intents file not found: {self.intents_file}")

        with open(self.intents_file, 'r') as f:
            data = json.load(f)

        return data.get('intents', [])

    def get_intent(self, query: str, threshold: float = 0.3) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Detect the intent of a user query using keyword matching.

        Args:
            query: User query string
            threshold: Minimum confidence score (0-1)

        Returns:
            (intent_dict, confidence_score)
        """
        return self._keyword_intent_detection(query, threshold)

    def _keyword_intent_detection(self, query: str, threshold: float = 0.3) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Improved intent detection using enhanced keyword matching and semantic similarity.

        Args:
            query: User query string
            threshold: Minimum confidence score (0-1)

        Returns:
            (intent_dict, confidence_score)
        """
        query_lower = query.lower().strip()
        query_words = set(query_lower.split())
        best_match = None
        best_score = 0.0

        # Sort intents by priority - more specific intents first
        # This ensures general_inquiry is checked before greeting
        intent_priority = {
            'general_inquiry': 1,  # Highest priority for capability questions
            'leave_policy': 2,
            'leave_balance': 2,
            'my_manager': 2,
            'my_department': 2,
            'greeting': 10  # Lower priority for generic greetings
        }

        sorted_intents = sorted(self.intents, key=lambda x: intent_priority.get(x['intent_id'], 5))

        for intent in sorted_intents:
            score = 0.0
            keywords = intent.get('keywords', [])
            examples = intent.get('examples', [])

            # Check keywords with exact and partial matching
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in query_lower:
                    score += 0.4  # Increased weight for keywords
                elif any(word in query_words for word in keyword_lower.split()):
                    score += 0.2  # Partial keyword match

            # Enhanced example matching
            for example in examples:
                example_lower = example.lower()
                # Exact phrase match gets highest score
                if example_lower in query_lower:
                    score += 1.2  # Increased weight for exact matches
                else:
                    # Improved partial word matching with better scoring
                    example_words = set(example_lower.split())
                    overlap = len(example_words.intersection(query_words))

                    if overlap > 0:
                        # Calculate similarity ratio
                        similarity = overlap / len(example_words)
                        score += similarity * 0.6  # Better scaling

                        # Bonus for high overlap
                        if similarity > 0.8:
                            score += 0.3

                    # Check for substring matches (handles typos and variations)
                    if len(example_lower) > 3 and example_lower in query_lower:
                        score += 0.4

            # Boost score for exact intent name matches
            intent_name_lower = intent['name'].lower()
            if intent_name_lower in query_lower:
                score += 0.4

            # Enhanced special handling for specific intents
            intent_id = intent['intent_id']

            # General inquiry patterns - prioritize over greeting for capability questions
            if intent_id == 'general_inquiry':
                # Look for capability-related patterns that distinguish from greetings
                capability_indicators = ['can', 'do', 'help', 'capabilities', 'features', 'services', 'provide', 'assist']
                capability_matches = sum(1 for word in capability_indicators if word in query_words)

                # Must have at least one capability indicator and "what" or "how"
                question_words = ['what', 'how', 'tell']
                question_matches = sum(1 for word in question_words if word in query_words)

                if capability_matches >= 1 and question_matches >= 1:
                    score += 1.0  # Higher boost for clear capability questions
                elif capability_matches >= 2:
                    score += 0.8  # Still boost if multiple capability words

            # Manager-related patterns
            elif intent_id == 'my_manager':
                manager_keywords = ['manager', 'reporting', 'report', 'boss', 'supervisor', 'lead']
                if any(word in query_lower for word in manager_keywords):
                    score += 0.6

            # Department patterns
            elif intent_id == 'my_department':
                dept_keywords = ['department', 'team', 'group', 'division', 'unit', 'work']
                if any(word in query_lower for word in dept_keywords):
                    score += 0.6

            # Goals/Objectives patterns
            elif intent_id == 'goals_objectives':
                goal_keywords = ['goals', 'objectives', 'targets', 'objectives', 'okr', 'performance']
                if any(word in query_lower for word in goal_keywords):
                    score += 0.6

            # Profile patterns
            elif intent_id == 'my_profile':
                profile_keywords = ['profile', 'information', 'details', 'info', 'about', 'myself', 'who']
                if any(word in query_lower for word in profile_keywords):
                    score += 0.6

            # Leave-related patterns
            elif intent_id.startswith('leave_') or intent_id == 'check_leave_eligibility':
                leave_keywords = ['leave', 'vacation', 'holiday', 'off', 'absent', 'sick', 'casual', 'annual']
                if any(word in query_lower for word in leave_keywords):
                    score += 0.4

            # Salary patterns
            elif intent_id.startswith('salary') or intent_id == 'payslip':
                salary_keywords = ['salary', 'pay', 'wage', 'compensation', 'payslip', 'earnings']
                if any(word in query_lower for word in salary_keywords):
                    score += 0.5

            # Phone update patterns
            elif intent_id.startswith('update_phone') or intent_id.startswith('enter_phone'):
                phone_keywords = ['phone', 'number', 'contact', 'mobile', 'update', 'change']
                if any(word in query_lower for word in phone_keywords):
                    score += 0.5

            # Emergency contact patterns
            elif intent_id.startswith('update_emergency') or intent_id.startswith('enter_emergency') or intent_id == 'show_emergency_contact':
                emergency_keywords = ['emergency', 'contact', 'urgent', 'backup']
                if any(word in query_lower for word in emergency_keywords):
                    score += 0.5

            # Greeting patterns
            elif intent_id == 'greeting':
                greeting_keywords = ['hello', 'hi', 'hey', 'good', 'morning', 'afternoon', 'evening', 'howdy', 'sup']
                if any(word in query_lower for word in greeting_keywords):
                    score += 0.8

            # Company info patterns
            elif intent_id == 'company_info':
                company_keywords = ['company', 'organization', 'about', 'mission', 'vision', 'who', 'what']
                if any(word in query_lower for word in company_keywords):
                    score += 0.5

            # HR contact patterns
            elif intent_id == 'hr_contact':
                hr_keywords = ['hr', 'human', 'resources', 'contact', 'reach', 'call', 'email']
                if any(word in query_lower for word in hr_keywords):
                    score += 0.5

            # Benefits patterns
            elif intent_id == 'benefits':
                benefit_keywords = ['benefits', 'perks', 'insurance', 'health', 'retirement', 'pto']
                if any(word in query_lower for word in benefit_keywords):
                    score += 0.5

            # Holiday patterns
            elif intent_id == 'holidays':
                holiday_keywords = ['holiday', 'vacation', 'calendar', 'festive', 'celebration']
                if any(word in query_lower for word in holiday_keywords):
                    score += 0.5

            # Attendance patterns
            elif intent_id == 'attendance':
                attendance_keywords = ['attendance', 'present', 'absent', 'working', 'days']
                if any(word in query_lower for word in attendance_keywords):
                    score += 0.5

            # Skills patterns
            elif intent_id == 'skills':
                skill_keywords = ['skills', 'expertise', 'competencies', 'abilities', 'talents']
                if any(word in query_lower for word in skill_keywords):
                    score += 0.5

            # Appraisal patterns
            elif intent_id == 'appraisal_cycle':
                appraisal_keywords = ['appraisal', 'review', 'performance', 'evaluation', 'rating']
                if any(word in query_lower for word in appraisal_keywords):
                    score += 0.5

            # Birthday/Anniversary patterns
            elif intent_id == 'birthday_anniversary':
                date_keywords = ['birthday', 'anniversary', 'celebration', 'important', 'dates']
                if any(word in query_lower for word in date_keywords):
                    score += 0.5

            # Normalize score to prevent over-scoring
            score = min(score, 2.0)

            if score > best_score:
                best_score = score
                best_match = intent

        # Lower threshold for better matching
        adjusted_threshold = min(threshold, 0.4)

        if best_match and best_score >= adjusted_threshold:
            # Normalize confidence score
            confidence = min(best_score / 1.5, 1.0)
            return best_match, confidence
        else:
            return None, best_score

    def get_intent_by_id(self, intent_id: str) -> Optional[Dict[str, Any]]:
        """Get intent details by ID."""
        for intent in self.intents:
            if intent['intent_id'] == intent_id:
                return intent
        return None

    def get_all_intents(self) -> List[Dict[str, Any]]:
        """Get all intents."""
        return self.intents

    def get_general_intents(self) -> List[Dict[str, Any]]:
        """Get only general (non-private) intents."""
        return [i for i in self.intents if i['category'] == 'general']

    def get_employee_intents(self) -> List[Dict[str, Any]]:
        """Get only employee-specific (private) intents."""
        return [i for i in self.intents if i['category'] == 'employee_specific']

    def is_private_intent(self, intent_id: str) -> bool:
        """Check if an intent is private/requires authentication."""
        intent = self.get_intent_by_id(intent_id)
        return intent['is_private'] if intent else False

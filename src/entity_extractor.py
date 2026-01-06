import re
import spacy
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class EntityExtractor:
    """Extracts entities like dates, months, and leave duration from user queries."""

    def __init__(self, model_name: str = "llama2"):
        """Initialize entity extractor with fallback methods."""
        self.model_name = model_name
        self.use_llm = False  # Always use fallback methods
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extract all entities from a user query using regex and spaCy.

        Args:
            query: User query string

        Returns:
            Dictionary containing extracted entities
        """
        return self._fallback_entity_extraction(query)

    def _fallback_entity_extraction(self, query: str) -> Dict[str, Any]:
        """
        Fallback entity extraction using regex and spaCy.

        Args:
            query: User query string

        Returns:
            Dictionary containing extracted entities
        """
        entities = self._get_empty_entities()

        # Extract phone number
        entities['phone_number'] = self._extract_phone_number(query)



        # Extract dates
        entities['dates'] = self._extract_dates(query)

        # Extract months
        months = self._extract_months(query)
        if months:
            entities['dates'].extend(months)

        # Extract leave duration
        entities['leave_duration'] = self._extract_leave_duration(query)

        # Extract leave types
        entities['leave_types'] = self._extract_leave_types(query)

        # Extract named entities
        entities['named_entities'] = self._extract_named_entities(query)

        # Extract numbers
        entities['numbers'] = re.findall(r'\b\d+\b', query)

        return entities

    def _extract_phone_number(self, query: str) -> Optional[str]:
        """Extract a 10-digit phone number from the query."""
        # This regex looks for a 10-digit number that doesn't have any digits before or after it.
        match = re.search(r'\b\d{10}\b', query)
        if match:
            return match.group(0)
        return None


    
    def _extract_dates(self, query: str) -> List[str]:
        """Extract dates from query using regex and date patterns."""
        dates = []
        
        # Pattern for dates like "15 Jan", "Jan 15", "01-15", "2025-01-15"
        date_patterns = [
            r'\d{1,2}\s+(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)',
            r'(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{1,2}/\d{1,2}/\d{2,4}',
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                dates.append(match.group())
        
        return list(set(dates))
    
    def _extract_months(self, query: str) -> List[str]:
        """Extract month names from query."""
        months = []
        month_names = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        ]
        
        query_lower = query.lower()
        for month in month_names:
            if month in query_lower:
                months.append(month)
        
        return list(set(months))
    
    def _extract_leave_duration(self, query: str) -> Dict[str, Any]:
        """Extract leave duration (days, weeks) from query."""
        duration = {
            'days': None,
            'weeks': None,
            'raw': []
        }
        
        # Pattern for "X days"
        days_pattern = r'(\d+)\s*(?:day|days|d)\b'
        days_matches = re.finditer(days_pattern, query, re.IGNORECASE)
        for match in days_matches:
            duration['days'] = int(match.group(1))
            duration['raw'].append(match.group())
        
        # Pattern for "X weeks"
        weeks_pattern = r'(\d+)\s*(?:week|weeks|w)\b'
        weeks_matches = re.finditer(weeks_pattern, query, re.IGNORECASE)
        for match in weeks_matches:
            duration['weeks'] = int(match.group(1))
            duration['raw'].append(match.group())
        
        return duration
    
    def _extract_leave_types(self, query: str) -> List[str]:
        """Extract leave types from query."""
        leave_types = []
        leave_keywords = {
            'sick': ['sick', 'illness', 'unwell', 'ill'],
            'casual': ['casual', 'day off'],
            'earned': ['earned', 'annual'],
            'maternity': ['maternity', 'maternal'],
            'paternity': ['paternity', 'paternal'],
            'unpaid': ['unpaid', 'without pay'],
            'emergency': ['emergency', 'urgent']
        }
        
        query_lower = query.lower()
        for leave_type, keywords in leave_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    leave_types.append(leave_type)
                    break
        
        return list(set(leave_types))
    
    def _extract_named_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy."""
        entities = {
            'person': [],
            'date': [],
            'other': []
        }
        
        if self.nlp is None:
            return entities
        
        doc = self.nlp(query)
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                entities['person'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['date'].append(ent.text)
            else:
                entities['other'].append((ent.text, ent.label_))
        
        return entities
    
    def parse_leave_request(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a leave request with extracted entities.
        
        Returns:
            Dictionary with leave request details
        """
        request = {
            'start_date': None,
            'end_date': None,
            'duration_days': entities['leave_duration'].get('days'),
            'duration_weeks': entities['leave_duration'].get('weeks'),
            'leave_type': entities['leave_types'][0] if entities['leave_types'] else None,
            'reason': None
        }
        
        # Try to extract dates
        if entities['dates']:
            request['start_date'] = entities['dates'][0]

        return request

    def _get_empty_entities(self) -> Dict[str, Any]:
        """Return empty entities structure for fallback."""
        return {
            'dates': [],
            'leave_duration': {'days': None, 'weeks': None, 'raw': []},
            'leave_types': [],
            'phone_number': None,

            'named_entities': {'person': [], 'date': [], 'other': []},
            'numbers': []
        }

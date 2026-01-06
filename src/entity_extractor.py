import re
from typing import Dict, List, Any, Optional


class EntityExtractor:
    """
    Extracts structured entities like dates, months, leave duration,
    leave types, phone numbers, and numbers using regex-based methods.
    """

    def __init__(self):
        """Initialize entity extractor (regex-based, cloud-safe)."""
        pass

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract all entities from a user query."""
        entities = self._get_empty_entities()

        entities["phone_number"] = self._extract_phone_number(query)
        entities["dates"] = self._extract_dates(query)
        entities["months"] = self._extract_months(query)
        entities["leave_duration"] = self._extract_leave_duration(query)
        entities["leave_types"] = self._extract_leave_types(query)
        entities["numbers"] = re.findall(r"\b\d+\b", query)

        return entities

    # -------------------- Extractors --------------------

    def _extract_phone_number(self, query: str) -> Optional[str]:
        """Extract a 10-digit phone number."""
        match = re.search(r"\b\d{10}\b", query)
        return match.group(0) if match else None

    def _extract_dates(self, query: str) -> List[str]:
        """Extract date-like patterns."""
        date_patterns = [
            r"\d{1,2}\s+(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)",
            r"(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}",
            r"\d{4}-\d{2}-\d{2}",
            r"\d{2}/\d{2}/\d{4}",
            r"\d{1,2}/\d{1,2}/\d{2,4}",
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            dates.extend(match.group() for match in matches)

        return list(set(dates))

    def _extract_months(self, query: str) -> List[str]:
        """Extract month names."""
        months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec",
        ]

        query_lower = query.lower()
        return list({month for month in months if month in query_lower})

    def _extract_leave_duration(self, query: str) -> Dict[str, Any]:
        """Extract leave duration in days or weeks."""
        duration = {"days": None, "weeks": None, "raw": []}

        for match in re.finditer(r"(\d+)\s*(?:day|days|d)\b", query, re.IGNORECASE):
            duration["days"] = int(match.group(1))
            duration["raw"].append(match.group())

        for match in re.finditer(r"(\d+)\s*(?:week|weeks|w)\b", query, re.IGNORECASE):
            duration["weeks"] = int(match.group(1))
            duration["raw"].append(match.group())

        return duration

    def _extract_leave_types(self, query: str) -> List[str]:
        """Extract leave types from keywords."""
        leave_keywords = {
            "sick": ["sick", "ill", "illness", "unwell"],
            "casual": ["casual", "day off"],
            "earned": ["earned", "annual"],
            "maternity": ["maternity", "maternal"],
            "paternity": ["paternity", "paternal"],
            "unpaid": ["unpaid", "without pay"],
            "emergency": ["emergency", "urgent"],
        }

        query_lower = query.lower()
        found_types = []

        for leave_type, keywords in leave_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                found_types.append(leave_type)

        return list(set(found_types))

    # -------------------- Helpers --------------------

    def parse_leave_request(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Parse structured leave request details."""
        return {
            "start_date": entities["dates"][0] if entities["dates"] else None,
            "duration_days": entities["leave_duration"].get("days"),
            "duration_weeks": entities["leave_duration"].get("weeks"),
            "leave_type": entities["leave_types"][0] if entities["leave_types"] else None,
        }

    def _get_empty_entities(self) -> Dict[str, Any]:
        """Return empty entity structure."""
        return {
            "dates": [],
            "months": [],
            "leave_duration": {"days": None, "weeks": None, "raw": []},
            "leave_types": [],
            "phone_number": None,
            "numbers": [],
        }

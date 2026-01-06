# 🚀 Quick Start Guide - ESS Chatbot

## One-Command Setup

```bash
cd c:\Users\nagal\ess-new
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

## What Just Happened?

✅ **Step 1-2:** Project Setup
- Created Python virtual environment
- Installed all dependencies (Flask, FastAPI, sentence-transformers, spaCy, scikit-learn, Streamlit)
- Downloaded spaCy English model

✅ **Step 3:** ESS Use Cases Defined
- **6 General Intents:** leave_policy, holidays, hr_contact, company_info, benefits
- **5 Employee-Specific Intents:** leave_balance, my_manager, my_department, attendance, leave_request, salary_info

✅ **Step 4-5:** Intent Configuration
- Created `config/intents.json` with 11 intents
- Each intent has 3-5 example sentences for training the ML model

✅ **Step 5:** Mock Database
- Created `data/employees.json` with 5 dummy employees
- Includes: employee_id, name, department, manager, leave_balance, attendance_days, salary

✅ **Step 6:** Authentication System
- `src/auth.py` - Login validation with employee ID and password
- Session management to track logged-in users

✅ **Step 7:** AI Intent Detection
- `src/intent_detector.py` - Sentence transformers for semantic understanding
- Uses all-MiniLM-L6-v2 model
- Cosine similarity to find best matching intent
- No training required!

✅ **Step 8:** Entity Extraction
- `src/entity_extractor.py` - Extract dates, months, leave duration
- Uses spaCy for NLP and regex patterns

✅ **Step 9:** Permission Layer
- Private intents require authentication
- Automatic permission checks before returning sensitive data

✅ **Step 10:** Business Logic
- `src/business_logic.py` - Handlers for all intents
- Fetch employee data, compute leave balance, etc.

✅ **Step 11:** Chat Interface
- `app.py` - Streamlit UI for user interaction
- Chat history, login interface, command support

## Demo Credentials

Try these to test:
```
Employee ID: E001
Password: pass123
Name: Alice Johnson
```

## First Query to Try

1. **Without Login:**
   - "What is the leave policy?"
   - "When are company holidays?"

2. **After Login (E001/pass123):**
   - "How many leaves do I have?"
   - "Who is my manager?"
   - "Show my attendance"

## Architecture Overview

```
User Input
    ↓ (Streamlit)
Intent Detection (Sentence-Transformers + Cosine Similarity)
    ↓
Entity Extraction (spaCy + Regex)
    ↓
Permission Check (Auth Manager)
    ↓
Business Logic (Handler)
    ↓
Response Generation
    ↓
Display to User
```

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit chat UI |
| `src/auth.py` | Employee login & session |
| `src/intent_detector.py` | AI intent detection |
| `src/entity_extractor.py` | Extract dates, duration, etc. |
| `src/business_logic.py` | Intent handlers |
| `src/chatbot.py` | Main orchestrator |
| `config/intents.json` | Intent definitions & examples |
| `data/employees.json` | Employee database |

## Troubleshooting

**Module not found errors?**
```bash
pip install -r requirements.txt
```

**spaCy model missing?**
```bash
python -m spacy download en_core_web_sm
```

**Port already in use?**
```bash
streamlit run app.py --server.port 8502
```

## Next Steps

1. Try asking queries without logging in
2. Log in with demo credentials (E001/pass123)
3. Ask employee-specific questions
4. Try leave request: "I want leave on Jan 15 for 3 days"
5. Explore entity extraction and intent confidence scores

## Commands You Can Use

- `/login E001 pass123` - Login
- `/logout` - Logout
- `/status` - Check login status
- `/help` - Show help

---

**All 11 Steps Complete!** ✨

Your ESS Chatbot is fully functional with:
- ✅ Project setup & environment
- ✅ Intent definitions & examples
- ✅ Mock employee database
- ✅ Authentication system
- ✅ AI-based intent detection
- ✅ Entity extraction
- ✅ Permission checks
- ✅ Business logic handlers
- ✅ Streamlit chat UI

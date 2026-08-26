import re
from typing import Dict, Any

class NLPEngine:
    def __init__(self):
        self.categories = [
            'food', 'housing', 'transport', 'subscriptions', 
            'shopping', 'healthcare', 'utilities', 'entertainment', 'salary'
        ]
        
        self.intent_patterns = {
            'FORECAST_REQUEST': [
                r'\bforecast\b', r'\bpredict\b', r'\bupcoming\b', 
                r'next\s+(month|week|year)', r'how much will (i|we) spend'
            ],
            'RECOMMENDATION': [
                r'\bsave\b', r'\bsavings\b', r'\brecommend\b', 
                r'\breduce\b', r'\bcut down\b'
            ],
            'SPENDING_SUMMARY': [
                r'how much did (i|we) spend', r'\bsummary\b', 
                r'\btotal\b', r'last\s+(month|week|year)', r'\brecently\b'
            ],
            'BUDGET_REMAINING': [
                r'\bleft in\b', r'\bremaining\b', r'\bbudget left\b'
            ],
            'BUDGET_STATUS': [
                r'\bover budget\b', r'\bunder budget\b', r'\bstatus\b', r'\bclosest to.*budget\b', r'\boverspending\b'
            ],
            'BUDGET_SUMMARY': [
                r'\bbudget\b', r'\blimit\b'
            ],
            'GOAL_SUMMARY': [
                r'\bgoals\b', r'\bfinancial goals\b', r'\bwhat are my.*goals\b'
            ],
            'GOAL_PROGRESS': [
                r'\bgoal progress\b', r'\bhow much have i saved\b', r'\bsaved for\b'
            ],
            'GOAL_REMAINING': [
                r'\bhow much more do i need\b', r'\bremaining amount for\b'
            ],
            'GOAL_SAVINGS_REQUIRED': [
                r'\bhow much should i save\b', r'\bhow much do i need to save\b'
            ],
            'GOAL_STATUS': [
                r'\bam i on track\b', r'\bgoal status\b'
            ],
            'GOAL_COMPLETION': [
                r'\bwhen will i reach\b', r'\bwill i reach\b'
            ],
            'GOAL_RECOMMENDATION': [
                r'\bwhich goal should i prioritize\b'
            ],
            'FINANCIAL_HEALTH_SCORE': [
                r'\bfinancial health score\b', r'\bfinancially healthy\b'
            ],
            'FINANCIAL_HEALTH_BREAKDOWN': [
                r'\bfinancial health breakdown\b', r'\bwhy is my financial health score\b', 
                r'\bwhat is hurting my financial health\b', r'\bwhat am i doing well financially\b',
                r'\bweakest financial areas\b'
            ],
            'FINANCIAL_HEALTH_IMPROVEMENT': [
                r'\bimprove my financial health\b', r'\bimprove my score\b'
            ],
            'FINANCIAL_HEALTH_HISTORY': [
                r'\bhow has my financial health changed\b', r'\bfinancial health history\b'
            ],
            'WHAT_IF_SCENARIO': [
                r'\bwhat if\b', r'\bwhat happens if\b', r'\bsimulate\b', r'\bscenario\b'
            ],
            'PURCHASE_AFFORDABILITY': [
                r'\bcan i afford\b', r'\baffordability\b'
            ],
            'GOAL_PLANNING_CALCULATOR': [
                r'\bhow much do i need to save every month to reach\b', 
                r'\bhow much should i save every month for\b'
            ]
        }
        
        self.time_patterns = {
            r'last week': 7,
            r'next week': 7,
            r'last month': 30,
            r'next month': 30,
            r'this month': 30,
            r'recently': 30
        }

    def process_query(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        intent = self._extract_intent(query_lower)
        category = self._extract_category(query_lower)
        time_range = self._extract_time_range(query_lower)
        
        # If no specific intent matched, default to SPENDING_SUMMARY
        if not intent:
            intent = 'SPENDING_SUMMARY'
            
        return {
            'intent': intent,
            'category': category,
            'time_range_days': time_range
        }
        
    def _extract_intent(self, query: str) -> str:
        # Check goal intents
        for pattern in self.intent_patterns['GOAL_SUMMARY']:
            if re.search(pattern, query):
                return 'GOAL_SUMMARY'
                
        for pattern in self.intent_patterns['GOAL_PROGRESS']:
            if re.search(pattern, query):
                return 'GOAL_PROGRESS'
                
        for pattern in self.intent_patterns['GOAL_REMAINING']:
            if re.search(pattern, query):
                return 'GOAL_REMAINING'
                
        for pattern in self.intent_patterns['GOAL_SAVINGS_REQUIRED']:
            if re.search(pattern, query):
                return 'GOAL_SAVINGS_REQUIRED'
                
        for pattern in self.intent_patterns['GOAL_STATUS']:
            if re.search(pattern, query):
                return 'GOAL_STATUS'
                
        for pattern in self.intent_patterns['GOAL_COMPLETION']:
            if re.search(pattern, query):
                return 'GOAL_COMPLETION'
                
        for pattern in self.intent_patterns['GOAL_RECOMMENDATION']:
            if re.search(pattern, query):
                return 'GOAL_RECOMMENDATION'

        for pattern in self.intent_patterns['FINANCIAL_HEALTH_SCORE']:
            if re.search(pattern, query):
                return 'FINANCIAL_HEALTH_SCORE'
                
        for pattern in self.intent_patterns['FINANCIAL_HEALTH_BREAKDOWN']:
            if re.search(pattern, query):
                return 'FINANCIAL_HEALTH_BREAKDOWN'
                
        for pattern in self.intent_patterns['FINANCIAL_HEALTH_IMPROVEMENT']:
            if re.search(pattern, query):
                return 'FINANCIAL_HEALTH_IMPROVEMENT'
                
        for pattern in self.intent_patterns['FINANCIAL_HEALTH_HISTORY']:
            if re.search(pattern, query):
                return 'FINANCIAL_HEALTH_HISTORY'

        # Check Planning intents
        for pattern in self.intent_patterns['WHAT_IF_SCENARIO']:
            if re.search(pattern, query):
                return 'WHAT_IF_SCENARIO'
                
        for pattern in self.intent_patterns['PURCHASE_AFFORDABILITY']:
            if re.search(pattern, query):
                return 'PURCHASE_AFFORDABILITY'
                
        for pattern in self.intent_patterns['GOAL_PLANNING_CALCULATOR']:
            if re.search(pattern, query):
                return 'GOAL_PLANNING_CALCULATOR'

        # Check specific budget intents first
        for pattern in self.intent_patterns['BUDGET_REMAINING']:
            if re.search(pattern, query):
                return 'BUDGET_REMAINING'
                
        for pattern in self.intent_patterns['BUDGET_STATUS']:
            if re.search(pattern, query):
                return 'BUDGET_STATUS'
                
        for pattern in self.intent_patterns['BUDGET_SUMMARY']:
            if re.search(pattern, query):
                return 'BUDGET_SUMMARY'
                
        for pattern in self.intent_patterns['RECOMMENDATION']:
            if re.search(pattern, query):
                return 'RECOMMENDATION'
                
        for pattern in self.intent_patterns['FORECAST_REQUEST']:
            if re.search(pattern, query):
                return 'FORECAST_REQUEST'
                
        for pattern in self.intent_patterns['SPENDING_SUMMARY']:
            if re.search(pattern, query):
                return 'SPENDING_SUMMARY'
                
        return None
        
    def _extract_category(self, query: str) -> str:
        for cat in self.categories:
            if cat in query:
                return cat
        return None
        
    def _extract_time_range(self, query: str) -> int:
        for pattern, days in self.time_patterns.items():
            if re.search(pattern, query):
                return days
        return 30 # Default to 30 days if not specified

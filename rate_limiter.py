import time
from collections import defaultdict, deque
from config import RATE_LIMIT_WINDOW, RATE_LIMIT_MAX_REQUESTS

class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(deque)
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make a request based on rate limiting"""
        current_time = time.time()
        user_queue = self.user_requests[user_id]
        
        # Remove old requests outside the time window
        while user_queue and user_queue[0] < current_time - RATE_LIMIT_WINDOW:
            user_queue.popleft()
        
        # Check if user has exceeded the limit
        if len(user_queue) >= RATE_LIMIT_MAX_REQUESTS:
            return False
        
        # Add current request timestamp
        user_queue.append(current_time)
        return True
    
    def get_wait_time(self, user_id: int) -> int:
        """Get how many seconds user needs to wait before next request"""
        current_time = time.time()
        user_queue = self.user_requests[user_id]
        
        if not user_queue:
            return 0
        
        oldest_request = user_queue[0]
        wait_time = RATE_LIMIT_WINDOW - (current_time - oldest_request)
        return max(0, int(wait_time))

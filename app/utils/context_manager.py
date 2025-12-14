# app/utils/context_manager.py

class ContextManager:
    def __init__(self, max_tokens: int = 3000):
        self.max_tokens = max_tokens
    
    def truncate_messages(self, messages: List[Dict]) -> List[Dict]:
        """Keep only recent messages that fit in context"""
        total_tokens = 0
        truncated = []
        
        # Iterate from most recent to oldest
        for message in reversed(messages):
            msg_tokens = self._count_tokens(message["content"])
            
            if total_tokens + msg_tokens <= self.max_tokens:
                truncated.insert(0, message)
                total_tokens += msg_tokens
            else:
                break
        
        return truncated
    
    def _count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # More accurate: use tiktoken library
        return len(text.split()) * 1.3  # 1 word ≈ 1.3 tokens
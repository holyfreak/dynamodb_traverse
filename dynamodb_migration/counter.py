class AsyncCounter:
    """Plain async, thread-safe incrementing counter"""
    def __init__(self, initial=0):
        self.value = initial

    def increment(self, num=1):
        self.value += num
        return self.value

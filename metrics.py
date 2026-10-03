from prometheus_client import Gauge, Histogram, start_http_server
import time

# start a global server (only once)
try:
    start_http_server(9123)  # /metrics endpoint
except Exception:
    pass

# Global histograms to capture latency per agent
agent_latency = Histogram(
    'dorama_agent_latency_seconds',
    'Processing latency in seconds per agent',
    ['agent'],
)

# Decorator to instrument functions

def instrument_agent(agent_name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            agent_latency.labels(agent=agent_name).observe(time.time() - start)
            return result
        return wrapper
    return decorator

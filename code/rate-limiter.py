import time
from flask import Flask, request, jsonify

# ---------------------------------------
# In-Memory Token Bucket Implementation
# ---------------------------------------
class InMemoryTokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = {}
        self.timestamps = {}

    def allow_request(self, identifier):
        now = time.time()
        tokens = self.tokens.get(identifier, self.capacity)
        last_refill = self.timestamps.get(identifier, now)

        new_tokens = min(self.capacity, tokens + (now - last_refill) * self.refill_rate)
        if new_tokens < 1:
            return False

        self.tokens[identifier] = new_tokens - 1
        self.timestamps[identifier] = now
        return True

# ---------------------------------------
# In-Memory Leaky Bucket Implementation
# ---------------------------------------
class InMemoryLeakyBucket:
    def __init__(self, capacity, leak_rate):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water_level = {}
        self.last_checked = {}

    def allow_request(self, identifier):
        now = time.time()
        level = self.water_level.get(identifier, 0)
        last_time = self.last_checked.get(identifier, now)

        leaked = (now - last_time) * self.leak_rate
        level = max(0, level - leaked)

        if level + 1 > self.capacity:
            return False

        self.water_level[identifier] = level + 1
        self.last_checked[identifier] = now
        return True

# ---------------------------------------
# Flask App with Toggle
# ---------------------------------------
app = Flask(__name__)

# Change this to 'token' or 'leaky'
RATE_LIMIT_ALGO = 'leaky'

if RATE_LIMIT_ALGO == 'token':
    rate_limiter = InMemoryTokenBucket(capacity=5, refill_rate=1)
else:
    rate_limiter = InMemoryLeakyBucket(capacity=5, leak_rate=1)

@app.route("/api")
def api():
    user_id = request.args.get("user", "anonymous")
    if rate_limiter.allow_request(user_id):
        return jsonify({"message": "Request allowed"})
    return jsonify({"error": "Rate limit exceeded"}), 429

@app.route("/")
def home():
    return "<h3>Rate Limiter is Running ({} Bucket)</h3>".format(RATE_LIMIT_ALGO.title())

if __name__ == "__main__":
    app.run(debug=True)

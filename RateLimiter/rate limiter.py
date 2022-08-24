Coding : Design an API that allows users to execute_endpoint(customer, tm). 
The system should not allow user to enter too many data points in a short time, say no more than 5 in 2 seconds.


考的题就是地里的面经， rate limiter。但是楼主昨天时间不够，做了其他的题。就漏了这题，结果考了。。。
楼主只做到了第三问。
第一问： 2秒之内只能发5个request， 怎么limit
第二问： 如果request 里面有customer id, 怎么让这个rate limit是customer specific的 （就是 customer 1 的limit超过了 并不影响 customer 2 的 request）
第三问： 有的request 会比其他的request 更 expensive。那么如果 input 里面还有一个关于 request weight 的信息，怎么改这个function。（比如 request 1 要占两个request的位置，怎么改）
-这个要自己多加一点test case， 就什么limit是 5 request/2s, 那么一个weight 是6 的request就直接fail之类的。



实现一个 RateLimiter
要求和 Guava 里的 RateLimiter 略有不同. 比如 1s 限制 5 个请求, 可以在 1s 的开始就获取全部 5 个请求; 而不是必须等待 200ms 才能获取一个请求.
时间是滑动窗口.
需要自己写测试用例.
第一步不用考虑多线程.
后续问题:
如何实现多线程版本.
写测试用例如何避免 sleep , 比如题目是 1s 限制 5 个请求, 怎么测试能尽快验证超过 1s 的情况 (用 mock, mock 当前系统时间)


经典rate limiter。followup是implement成一个class然后用system.nanotime跑一遍。


# (not valid) token bucket vs sliding window ? can we have all 5 requests at same time or it has to wait every 200ms one request
# (not valid) Is the request coming in chronological order ? if yes we can just use deque if no we need to use heap/priority queue every time when new request come keep pop heap until the time is in same window
# is it possible multiple requests coming in same timestamp
# does each customer have their own rate_limiter ?

# use a queue to store request, when new request coming compare current time with first request's time in queue and pop it until find request is in same time window with current request
# then check queue size


from collections import deque

class RateLimiter:

    def __init__(self, user_id, max_hits, time_window):
            self.user_deque = deque()
            self.user_id = user_id
            self.max_hits = max_hits
            self.time_window = time_window

    def execute_endpoint(self, request, curr_time):

        # get request count for current window
        curr_count = self.get_request_count(self.user_deque, curr_time)

        if curr_count < self.max_hits:
            self.user_deque.append(curr_time)
            return self.forward(self.user_id, request, curr_time)
        else:
            return self.drop(self.user_id, request, curr_time)

    def get_request_count(self, user_deque, curr_time):
        
        # pop all requests that are not in same window
        while user_deque:
            if curr_time - user_deque[0] > self.time_window:
                user_deque.popleft()
            else:
                break
        
        return len(user_deque)

    def forward(self, user_id, request, curr_time):
        return f"{user_id}'s {request} forwarded at {curr_time}"

    def drop(self, user_id, request, curr_time):
        return f"{user_id}'s {request} dropped at {curr_time}"


def test_rate_limiter():
    user_1_rate_limiter = RateLimiter("user_1", 2, 5)

    msg = user_1_rate_limiter.execute_endpoint("request_1", 1)
    assert msg == "user_1's request_1 forwarded at 1"
    msg = user_1_rate_limiter.execute_endpoint("request_2", 2)
    assert msg == "user_1's request_2 forwarded at 2"
    msg = user_1_rate_limiter.execute_endpoint("request_3", 3)
    assert msg == "user_1's request_3 dropped at 3"

    # now in next time_window
    msg = user_1_rate_limiter.execute_endpoint("request_4", 6.1)
    assert msg == "user_1's request_4 forwarded at 6.1"
test_rate_limiter()
print(f"----- test_rate_limiter FINISH")

def test_rate_limiter_w_multiple_users():
    user_1_rate_limiter = RateLimiter("user_1", 2, 5)
    user_2_rate_limiter = RateLimiter("user_2", 1, 1)

    msg = user_1_rate_limiter.execute_endpoint("request_1", 1)
    assert msg == "user_1's request_1 forwarded at 1"
    msg = user_2_rate_limiter.execute_endpoint("request_1", 1)
    assert msg == "user_2's request_1 forwarded at 1"

    msg = user_2_rate_limiter.execute_endpoint("request_2", 1.5)
    assert msg == "user_2's request_2 dropped at 1.5"

    msg = user_1_rate_limiter.execute_endpoint("request_2", 3)
    assert msg == "user_1's request_2 forwarded at 3"
    msg = user_1_rate_limiter.execute_endpoint("request_3", 3)
    assert msg == "user_1's request_3 dropped at 3"
    msg = user_2_rate_limiter.execute_endpoint("request_3", 3)
    assert msg == "user_2's request_3 forwarded at 3"
test_rate_limiter_w_multiple_users()
print(f"----- test_rate_limiter_w_multiple_users FINISH")








第三问： 有的request 会比其他的request 更 expensive。那么如果 input 里面还有一个关于 request weight 的信息，怎么改这个function。（比如 request 1 要占两个request的位置，怎么改）
-这个要自己多加一点test case， 就什么limit是 5 request/2s, 那么一个weight 是6 的request就直接fail之类的。


# same as above, but need to check total_request_weight instead of queue size within time_window

from collections import deque

class RateLimiter:

    def __init__(self, user_id, max_weight, time_window):
            self.user_deque = deque()
            self.user_id = user_id
            self.max_weight = max_weight
            self.time_window = time_window

    def execute_endpoint(self, request, weight, curr_time):

        # get request count for current window
        curr_weight = self.get_total_weight(self.user_deque, curr_time)

        if curr_weight + weight <= self.max_weight:
            self.user_deque.append((curr_time, weight))
            return self.forward(self.user_id, request, weight, curr_time)
        else:
            return self.drop(self.user_id, request, weight, curr_time)

    def get_total_weight(self, user_deque, curr_time):
        total_weight = 0
        
        # pop all requests that are not in same window
        while user_deque:
            if curr_time - user_deque[0][0] > self.time_window:
                user_deque.popleft()
            else:
                break

        # add all weight within same window if any
        if user_deque:
            for r in user_deque:
                total_weight += r[1]

        return total_weight

    def forward(self, user_id, request, weight, curr_time):
        return f"{user_id}'s {request} with weight {weight} forwarded at {curr_time}"

    def drop(self, user_id, request, weight, curr_time):
        return f"{user_id}'s {request} with weight {weight} dropped at {curr_time}"


def test_execute_endpoint():
    user_1_rate_limiter = RateLimiter("user_1", 5, 2)

    msg = user_1_rate_limiter.execute_endpoint("request_1", 6, 1)
    assert msg == "user_1's request_1 with weight 6 dropped at 1"

    msg = user_1_rate_limiter.execute_endpoint("request_2", 1, 2)
    assert msg == "user_1's request_2 with weight 1 forwarded at 2"
    msg = user_1_rate_limiter.execute_endpoint("request_3", 4, 2)
    assert msg == "user_1's request_3 with weight 4 forwarded at 2"

    msg = user_1_rate_limiter.execute_endpoint("request_4", 5, 4.5)
    assert msg == "user_1's request_4 with weight 5 forwarded at 4.5"

test_execute_endpoint()
print(f"----- test_execute_endpoint() FINISH")









Token bucket:

import time

class RateLimiter:

    class TokenBucket:
        def __init__(self, tokens, time_unit, forward_call, drop_call):
            self.tokens = tokens
            self.time_unit = time_unit
            self.forward_call = forward_call
            self.drop_call = drop_call
            self.bucket = tokens
            self.last_check = time.time()

        def handle(self, request):
            current = time.time()
            time_passed = current - self.last_check
            # print(f"last_check: {self.last_check} current: {current}")
            self.last_check = current

            # Refill tokens
            self.bucket = min(self.tokens, self.bucket + time_passed * (self.tokens / self.time_unit))
            
            print(f"processing {request}, current bucket has {self.bucket} tokens.")
            
            if self.bucket < 1:
                self.drop_call(request)
            else:
                self.bucket = self.bucket - 1
                self.forward_call(request)
    
    def __init__(self, max_hits, time_window):
        self.user_rate_limiter = {}
        self.max_hits = max_hits
        self.time_window = time_window

    def forward(self, request):
        print("Request Forwarded: " + str(request))

    def drop(self, request):
        print("Request Dropped: " + str(request))

    def execute_endpoint(self, user_id, request):
        if user_id not in self.user_rate_limiter:
            self.user_rate_limiter[user_id] = self.TokenBucket(self.max_hits, self.time_window, self.forward, self.drop)

        user_rate_limiter = self.user_rate_limiter[user_id]
        user_rate_limiter.handle(request)

rate_limiter = RateLimiter(2, 5)

rate_limiter.execute_endpoint("user_1", "request_1")
rate_limiter.execute_endpoint("user_1", "request_2")
rate_limiter.execute_endpoint("user_1", "request_3")
rate_limiter.execute_endpoint("user_1", "request_4")

rate_limiter.execute_endpoint("user_2", "request_1")
rate_limiter.execute_endpoint("user_2", "request_2")
rate_limiter.execute_endpoint("user_2", "request_3")

time.sleep(5)
rate_limiter.execute_endpoint("user_1", "request_5")
rate_limiter.execute_endpoint("user_2", "request_4")



Rate limiting in distributed systems
Synchronization Policies
https://konghq.com/blog/how-to-design-a-scalable-rate-limiting-algorithm
If you want to enforce a global rate limit when using a cluster of multiple nodes, you must set up a policy to enforce it. If each node were to track its rate limit, 
a consumer could exceed a global rate limit when sending requests to different nodes. The greater the number of nodes, the more likely the user will exceed the global limit.
solution:
1. sticky session one user always go to same server
2. central data store






Sliding window log ? :

import threading
import time

class RateLimiter:

    class HitCounter:

        def __init__(self, window_size):
            self.times = [0] * window_size
            self.hits = [0] * window_size
            self.window_size = window_size
            self.lock = threading.Lock()

        def hit(self, timestamp: int) -> None:
            idx = timestamp % self.window_size
            if self.times[idx] != timestamp:
                self.lock.acquire()
                self.times[idx] = timestamp
                self.hits[idx] = 1
                self.lock.release()
            else:
                self.lock.acquire()
                self.hits[idx] += 1
                self.lock.release()

        def getHits(self, timestamp: int) -> int:
            total = 0
            for i in range(self.window_size):
                if timestamp - self.times[i] < self.window_size:
                    total += self.hits[i]
            return total

    def __init__(self, max_hits, time_window):
        self.user_counter = {}
        self.max_hits = max_hits
        self.time_window = time_window

    def execute_endpoint(self, user_id, timestamp):
        if user_id not in self.user_counter:
            self.user_counter[user_id] = self.HitCounter(self.time_window)

        user_hit_counter = self.user_counter[user_id]
        if user_hit_counter.getHits(timestamp) == self.max_hits:
            # Don't allow user execute endpoint if he reaches max hits
            print(f"{user_id}: you've used api for {self.max_hits} in {self.time_window}. Wait a bit")
        else:
            user_hit_counter.hit(timestamp)
            # execute endpoint
            print(f"{user_id}: you can execute the endpoint")

rate_limiter = RateLimiter(2, 5)
rate_limiter.execute_endpoint("user_1", int(time.time()))
rate_limiter.execute_endpoint("user_1", int(time.time()))
rate_limiter.execute_endpoint("user_1", int(time.time()))
rate_limiter.execute_endpoint("user_1", int(time.time()))

rate_limiter.execute_endpoint("user_2", int(time.time()))
rate_limiter.execute_endpoint("user_2", int(time.time()))
rate_limiter.execute_endpoint("user_2", int(time.time()))

time.sleep(5)
rate_limiter.execute_endpoint("user_1", int(time.time()))
rate_limiter.execute_endpoint("user_2", int(time.time()))


In real life, the window could be huge and self.times could take more memory. For rate limiting, we should stop process hit after it reaches some threshold but this hit counter will simply
accept hit all the time.









token bucket
https://dev.to/satrobit/rate-limiting-using-the-token-bucket-algorithm-3cjh

import time


class TokenBucket:

    def __init__(self, tokens, time_unit, forward_callback, drop_callback):
        self.tokens = tokens
        self.time_unit = time_unit
        self.forward_callback = forward_callback
        self.drop_callback = drop_callback
        self.bucket = tokens
        self.last_check = time.time()

    def handle(self, packet):
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current

        self.bucket = self.bucket + \
            time_passed * (self.tokens / self.time_unit)

        if (self.bucket > self.tokens):
            self.bucket = self.tokens

        if (self.bucket < 1):
            self.drop_callback(packet)
        else:
            self.bucket = self.bucket - 1
            self.forward_callback(packet)


def forward(packet):
    print("Packet Forwarded: " + str(packet))


def drop(packet):
    print("Packet Dropped: " + str(packet))


throttle = TokenBucket(1, 1, forward, drop)

packet = 0

while True:
    time.sleep(0.2)
    throttle.handle(packet)
    packet += 1


Packet Forwarded: 0
Packet Dropped: 1
Packet Dropped: 2
Packet Dropped: 3
Packet Dropped: 4
Packet Forwarded: 5
Packet Dropped: 6
Packet Dropped: 7
Packet Dropped: 8
Packet Dropped: 9
Packet Forwarded: 10
Packet Dropped: 11
Packet Dropped: 12
Packet Dropped: 13
Packet Dropped: 14
Packet Forwarded: 15



this algorithm assigns token on a constant rate so at each self.tokens / self.time_unit window its capacity is really limited.





Fixed window
Obviously, fixed window counter algorithm only guarantees the average rate within each window but not across windows. 
For example, if the expected rate is 2 per minute and there are 2 requests at 00:00:58 and 00:00:59 as well as 2 requests at 00:01:01 and 00:01:02. 
Then the rate of both window [00:00, 00:01) and window [00:01, 00:02) is 2 per minute. But the rate of window [00:00:30, 00:01:30) is in fact 4 per minute.







































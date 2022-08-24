题目： load balancing。 give a list of server name, e.g.["a", "b", "c"]。 然后要求route requests， request有自己的weight, e.g. route(1) -> "a", route(1) -> "b"。 
requests 要route 到load 最轻的server， 如果多个server的load 相同，按照accending order


# how to route when multiple servers have same load ?
# we can use a min heap where the top is the minimum load, each time we add weight to the minimum load server and put it back to heap

import heapq

class LoadBalancer:

    def __init__(self, servers):
        self.servers = servers
        self.heap = []
        for name, load in servers.items():
            # heap will sort load first then name
            heapq.heappush(self.heap, (load, name))

    def route_requests(self, request_weight):
        
        # pop top element in heap (lightest load)
        least_load_server = heapq.heappop(self.heap)

        # add request_weight
        heapq.heappush(self.heap, (least_load_server[0] + request_weight, least_load_server[1]))

        return least_load_server[1]

def test_route_requests_w_same_init_load():
    servers = {"a": 0, "b": 0, "c": 0}
    lb = LoadBalancer(servers)
    assert lb.route_requests(5) == 'a'
    assert lb.route_requests(1) == 'b'
    assert lb.route_requests(1) == 'c'
    assert lb.route_requests(2) == 'b'
    assert lb.route_requests(4) == 'c'
    assert lb.route_requests(1) == 'b'
test_route_requests_w_same_init_load()
print(f"----- test_route_requests_w_same_init_load FINISH")

def test_route_requests_diff_init_load():
    servers = {"a": 10, "b": 5, "c": 0}
    lb = LoadBalancer(servers)
    assert lb.route_requests(5) == 'c'
    assert lb.route_requests(1) == 'b'
    assert lb.route_requests(6) == 'c'
    assert lb.route_requests(6) == 'b'
    assert lb.route_requests(4) == 'a'
test_route_requests_diff_init_load()
print(f"----- test_route_requests_diff_init_load FINISH")



alternative, we can create a Wrapper class and rewrite __lt__ method

import heapq

class Wrapper:
    def __init__(self, load, name):
        self.load = load
        self.name = name
        
    def __lt__(self, other):
        if self.load == other.load:
            return other.name < self.name
        else:
            return self.load < other.load

servers = {"a": 0, "b": 0, "c": 0}
heap = []
for name, load in servers.items():
    heapq.heappush(heap, Wrapper(load, name))

def route_requests(request_weight):
    least_load_server = heapq.heappop(heap)
    heapq.heappush(heap, Wrapper(least_load_server.load + request_weight, least_load_server.name))
    return least_load_server.name

print(route_requests(5))
print(route_requests(1))
print(route_requests(1))
print(route_requests(2))
print(route_requests(4))
print(route_requests(1))




refer to leetcode Top K Frequent Words










follow up：
request 增加需要process的时间，process 完server的load 要减去processed req''s weight. e.g. route(2, 0.1) -> "a", route(1, 0.3) -> "b", sleep(0.1), route(2, 0.1) -> "a"

# when multiple servers has same weight, how to choose ?

# add process_time, curr_time into route_request()
# every time when a new request coming, we'll go over all servers and drop the expired request and calculate the total load up to date, then find the lightest load server to add this request
# if multiple servers have same lighest load, it will based on their name
# when add a new request to a server we'll store (request_weight, finish_time = curr_time + process_time)

a: [], b: [], c: []
0   - a: [(2, 0.1)], b: [(1, 0.3)], c: []

0.1 - a: [], b: [(1, 0.2)], c: []
      a: [(2, 0.1)], b: [(1, 0.2)], c: []



when calling route_request(), we traverse all servers and drop all expired request and add all left requests weight. We find the least load server and give it the request.
if we have multiple server load same we use heap to find the least lexicographic one

python perf counter
The perf_counter() function always returns the float value of time in seconds. Return the value (in fractional seconds) of a performance counter, i.e. 
a clock with the highest available resolution to measure a short duration. It does include time elapsed during sleep and is system-wide. 
The reference point of the returned value is undefined, so that only the difference between the results of consecutive calls is valid. 
In between this we can use time.sleep() and likewise functions.

perf counter vs time.time()
time.time() deals with absolute time, i.e., "real-world time" (the type of time we're used to). It's measured from a fixed point in the past
time.perf_counter(), on the other hand, deals with relative time, which has no defined relationship to real-world time (i.e., the relationship is unknown to us and depends on several factors). 
It's measured using a CPU counter and, as specified in the docs, should only be used to measure time intervals




import heapq

class LoadBalancer:

    def __init__(self, servers):
        self.servers = servers

    def route_requests(self, request_weight, process_time, curr_time):

        # initial set lighest_load to infinity
        chosen_server, lightest_load, server_total_weight = "", float('inf'), {}

        # go over all servers
        for server_name, server_requests in self.servers.items():
            total_weight, new_server_requests, = 0, []

            # for each server add weight for each request if it's still in process and find the lightest load server
            # drop request that is expired
            while server_requests:
                server_request = server_requests.pop()
                weight, finish_time = server_request[0], server_request[1]
                if finish_time > curr_time:
                    total_weight += weight
                    new_server_requests.append((weight, finish_time))
            
            # update server with new requests
            self.servers[server_name] = new_server_requests
            # map server_name with total_weight
            server_total_weight[server_name] = total_weight
            # update lightest_load if necessary
            lightest_load = min(lightest_load, total_weight)
        
        heap = []
        # find which server has lightest load
        for server_name, total_weight in server_total_weight.items():
            if total_weight == lightest_load:
                heapq.heappush(heap, server_name)

        chosen_server = heapq.heappop(heap)

        # add this request to chosen_server's queue
        self.servers[chosen_server].append((request_weight, curr_time + process_time))
        # print(f"@@@@@ {servers}")
        return chosen_server

def test_route_requests_w_same_init_load():
    servers = {"a": 0, "b": 0, "c": 0}
    lb = LoadBalancer(servers)
    assert lb.route_requests(5, 1, 1) == 'a'
    assert lb.route_requests(1, 3, 1) == 'b'
    assert lb.route_requests(1, 5, 1) == 'c'
    assert lb.route_requests(2, 3, 2.1) == 'a'
    assert lb.route_requests(2, 2, 3) == 'b'
test_route_requests_w_same_init_load()
print(f"----- test_route_requests_w_same_init_load FINISH")

def test_route_requests_diff_init_load():
    servers = {"a": [(10, 1), (1, 4)], "b": [(5, 2)]}
    lb = LoadBalancer(servers)
    assert lb.route_requests(2, 2, 0.5) == 'b'
    assert lb.route_requests(3, 2, 2) == 'a'
    assert lb.route_requests(6, 2, 3) == 'b'
test_route_requests_diff_init_load()
print(f"----- test_route_requests_diff_init_load FINISH")



we can use Wrapper like question 1
class Wrapper:
    def __init__(self, name):
        self.name = name
        
    def __lt__(self, other):
        return other.name < self.name


















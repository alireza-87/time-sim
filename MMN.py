from collections import deque
from heapq import heappush, heappop
import random

import constant as cnt
from modules.plots import plot_avg_queue_len
from modules.plots import plot_queue_len_multi_server
from modules.plots import plot_delay_time
from modules.plots import plot_error_queue_len
from modules.plots import plot_error_time_spent
from random import expovariate, randint
from modules.colors import Colors

super_market = False
fifo = False  # Fifo Vs.Sjf
server_count = 1





class Arrival:

    def __init__(self, _id):
        self.time = 0.00
        self.id = _id
        self.arrival_time = 0
        self.service_time = 0

    def process(self, state, arrival_rate):
        state.arrivals[self.id] = state.t
        self.arrival_time = state.t + expovariate(arrival_rate)  # * save job arrival time in state.arrivals (the new
        # event will happen at time t + expovariate(LAMBDA))
        self.service_time = state.t + expovariate(1)
        if not fifo:
            if self.service_time > self.arrival_time:
                self.time = self.service_time - self.arrival_time  # SJF

        # Find Queue base on the chosen algorithm
        if super_market:
            q_info = {}
            selected_server = random.sample(list(dict.fromkeys(state.queues)), k=d)
            for i in selected_server:
                q_info[i] = len(state.queues[i])
            index = min(q_info, key=lambda k: q_info[k])
        else:
            index = randint(0, server_count - 1)

        # * push the new job arrival in the event queue
        if fifo:
            state.queues[index].append(self.id)  # FIFO
        else:
            heappush(state.queues[index], (self.time, self.id))  # SJF

        for i in range(len(state.queues)):
            state.queues_length[i].append(len(state.queues[i]))

        self.id += 1
        heappush(state.events, (self.arrival_time, Arrival(self.id)))
        if len(state.queues[index]) == 1:
            heappush(state.events, (self.service_time, Completion(index)))


class Completion:
    def __init__(self, _index_queue):
        self.index_queue = _index_queue

    def process(self, state, empty):
        if fifo:
            index_job = state.queues[self.index_queue].popleft()
            state.completions[index_job] = state.t
        else:
            index_job = heappop(state.queues[self.index_queue])
            state.completions[index_job[1]] = state.t

        if len(state.queues[self.index_queue]) > 0:
            heappush(state.events, (state.t + expovariate(1), Completion(self.index_queue)))


class State:
    def __init__(self):
        self.t = 0  # current time in the simulation
        self.queues = {}
        self.queues_length = {}
        # Initialize
        for i in range(0, server_count):
            self.queues_length[i] = []
        if fifo:
            for i in range(0, server_count):
                self.queues[i] = deque()
        else:
            for i in range(0, server_count):
                self.queues[i] = []

        self.events = []
        self.arrivals = {}  # jobid -> arrival time mapping
        self.completions = {}  # jobid -> completion time mapping
        heappush(self.events, (self.t, Arrival(0)))


def simulator():
    queue_length_dict = {}  # all queue lens

    real_w = []  # real time spent in the system
    expected_w = []  # expected time spent in the system

    real_l = []  # real q len
    expected_l = []  # expected q len

    w_error = []
    l_error = []

    for item in cnt.LAMBDA:
        print(f"{Colors.OKCYAN}**************************************************{Colors.ENDC}")
        print(f"{Colors.OKBLUE}lambda : {Colors.ENDC}", str(item))
        state = State()

        events = state.events

        while events:
            t, event = heappop(events)
            if t > cnt.MAXT:
                break
            state.t = t
            event.process(state, item * server_count)

        current_expected_w = 1 / (1 - item)
        expected_w.append(current_expected_w)
        print(f"{Colors.OKGREEN}Expected average time spent : {Colors.ENDC}", str(round(current_expected_w, 2)))

        current_real_w = 0
        for i in state.completions:
            current_real_w += state.completions[i] - state.arrivals[i]
        current_real_w /= len(state.completions)
        real_w.append(current_real_w)
        print(f"{Colors.OKGREEN}Real average time spent : {Colors.ENDC}", str(round(current_real_w, 2)))

        current_w_error = abs(current_real_w - current_expected_w) / current_real_w
        w_error.append(current_w_error)
        print(f"{Colors.WARNING}Average Time spent(w) error : {Colors.ENDC}", str(round(current_w_error, 2)))

        current_expected_l = item / (1 - item)
        expected_l.append(current_expected_l)
        print(f"{Colors.OKGREEN}Expected average queue len : {Colors.ENDC}", str(round(current_expected_l, 2)))

        current_real_l = 0
        for i in state.queues_length.values():
            current_real_l += sum(i) / len(i)
        current_real_l /= len(state.queues_length)
        real_l.append(current_real_l)
        print(f"{Colors.OKGREEN}Real average queue len : {Colors.ENDC}", str(round(current_real_l, 2)))

        current_l_error = abs(current_real_l - current_expected_l) / current_real_l
        l_error.append(current_l_error)
        print(f"{Colors.WARNING}Average Queue len(l) error: {Colors.ENDC}", str(round(current_l_error, 2)))

        print(f"{Colors.OKGREEN}Arrive Len : {Colors.ENDC}", str(len(state.arrivals)))
        print(f"{Colors.OKGREEN}Complete Len : {Colors.ENDC}", str(len(state.completions)))
        queue_length_dict[item] = state.queues_length
    plot_queue_len_multi_server(queue_length_dict)
    plot_avg_queue_len(real_l, expected_l)
    plot_delay_time(real_w, expected_w)
    plot_error_queue_len(l_error)
    plot_error_time_spent(w_error)


if __name__ == '__main__':
    print(f"{Colors.HEADER}********** MMN **********{Colors.ENDC}")
    super_market = input(f"{Colors.OKCYAN}Simulate the Supermarket model(y,n)? {Colors.ENDC}") == 'y'
    if super_market:
        d_value = [int(x) for x in input(f"{Colors.OKCYAN}Enter number of queue for Supermarket model(split by ,): {Colors.ENDC}").split(",")]
    fifo = input(f"{Colors.OKCYAN}FIFO(1) or SJF(2) ? {Colors.ENDC}") == '1'
    server_count = int(input(f"{Colors.OKCYAN}Number of Server? {Colors.ENDC}"))
    if super_market:
        for d in d_value:
            print(f"{Colors.HEADER}__________________________________________________{Colors.ENDC}")
            print(f"{Colors.OKBLUE}d value : {Colors.ENDC}", d)
            simulator()
    else:
        simulator()

from collections import deque
from heapq import heappush, heappop
from random import expovariate

import constant as cnt
from modules.plots import plot_avg_queue_len
from modules.plots import plot_delay_time
from modules.plots import plot_error_queue_len
from modules.plots import plot_error_time_spent
from modules.plots import plot_queue_len
from modules.colors import Colors

queue_length = []  # current queue len
queue_length_dict = {}  # all queue lens

real_w = []  # real time spent in the system
expected_w = []  # expected time spent in the system

real_l = []  # real q len
expected_l = []  # expected q len

w_error = []
l_error = []


class Arrival:
    def __init__(self, _id):
        self.id = _id
        self.arrival_time = 0
        self.service_time = 0

    def process(self, _state, arrival_rate):
        queue_length.append(len(_state.fifo))
        _state.arrivals[self.id] = _state.t  # * save job arrival time in state.arrivals
        _state.fifo.append(self.id)  # * push the new job arrival in the event queue
        self.arrival_time = _state.t + expovariate(arrival_rate)  # (the new event will happen at time t + expovariate(LAMBDA))
        self.service_time = _state.t + expovariate(1)  # (termination will happen at time t + expovariate(1))
        self.id += 1
        heappush(_state.events, (self.arrival_time, Arrival(self.id)))
        if len(_state.fifo) == 1:
            heappush(_state.events, (self.service_time, Completion()))


class Completion:

    def process(self, _state, arrival_rate):
        job_index = _state.fifo.popleft()  # remove the first job from the FIFO queue
        _state.completions[job_index] = _state.t  # * update its completion time in state.completions
        if len(_state.fifo) > 0:
            heappush(_state.events, (_state.t + expovariate(1), Completion()))


class State:
    def __init__(self):
        self.t = 0  # current time in the simulation
        self.events = [(self.t, Arrival(0))]  # queue of events to simulate
        self.fifo = deque()  # queue at the server
        self.arrivals = {}  # jobid -> arrival time mapping
        self.completions = {}  # pair  # jobid -> completion time mapping


if __name__ == '__main__':

    for item in cnt.LAMBDA:
        print(f"{Colors.OKCYAN}**************************************************{Colors.ENDC}")
        print(f"{Colors.OKBLUE}lambda : {Colors.ENDC}", str(item))
        state = State()
        queue_length = []
        events = state.events

        while events:
            t, event = heappop(events)
            if t > cnt.MAXT:
                break
            state.t = t
            event.process(state, item)

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
        for i in queue_length:
            current_real_l += i
        current_real_l /= len(queue_length)
        real_l.append(current_real_l)
        print(f"{Colors.OKGREEN}Real average queue len : {Colors.ENDC}", str(round(current_real_l, 2)))

        current_l_error = abs(current_real_l - current_expected_l) / current_real_l
        l_error.append(current_l_error)
        print(f"{Colors.WARNING}Average Queue len(l) error : {Colors.ENDC}", str(round(current_l_error, 2)))

        print(f"{Colors.OKGREEN}Queue Len: {Colors.ENDC}", str(len(queue_length)))
        print(f"{Colors.OKGREEN}Arrive Len : {Colors.ENDC}", str(len(state.arrivals)))
        print(f"{Colors.OKGREEN}Complete Len : {Colors.ENDC}", str(len(state.completions)))
        queue_length_dict[item] = queue_length

    plot_queue_len(queue_length_dict)
    plot_avg_queue_len(real_l, expected_l)
    plot_delay_time(real_w, expected_w)
    plot_error_queue_len(l_error)
    plot_error_time_spent(w_error)

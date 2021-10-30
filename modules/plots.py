import matplotlib.pyplot as plt
import constant as cnt


def plot_queue_len(data_to_print):
    for key in data_to_print:
        x = range(1, 15)
        y = []
        for element in x:
            count = sum(map(lambda x: x >= element, data_to_print[key]))
            fraction = count / len(data_to_print[key])
            y.append(fraction)
        plt.plot(x, y, label=key)
    plt.ylim(0, 1)
    plt.ylabel('Fraction of queues with at least that size')
    plt.xlabel('Queue length 2')
    plt.legend()
    plt.show()


def plot_queue_len_multi_server(data_to_print):
    for key in data_to_print:
        x = range(1, 15)
        y = []
        for element in x:
            value = 0
            for server_q in data_to_print[key].values():
                value += len([i for i in server_q if i >= element]) / len(server_q)
            y.append(value / 50)
        plt.plot(x, y, label=key)
    plt.ylim(0, 1)
    plt.ylabel('Fraction of queues with at least that size')
    plt.xlabel('Queue length 2')
    plt.legend()
    plt.show()


def plot_avg_queue_len(real_data, expected_data):
    plt.plot(cnt.LAMBDA, real_data, 'b--')
    plt.plot(cnt.LAMBDA, real_data, 'bs', label='Simulation avg queue length')
    plt.plot(cnt.LAMBDA, expected_data, 'g--')
    plt.plot(cnt.LAMBDA, expected_data, 'go', label='Theoretical avg queue length')
    plt.xlabel('Lambda Value')
    plt.ylabel('Avg queue length')
    plt.legend()
    plt.title("Simulation Vs Theoretical :Avg queue length on M/M/1 ")
    plt.show()


def plot_delay_time(real_data, expected_data):
    plt.plot(cnt.LAMBDA, real_data, 'b--')
    plt.plot(cnt.LAMBDA, real_data, 'bs', label='Simulation delay time')
    plt.plot(cnt.LAMBDA, expected_data, 'g--')
    plt.plot(cnt.LAMBDA, expected_data, 'go', label='Theoretical delay time')
    plt.xlabel('Lambda Value')
    plt.ylabel('delay time (secs)')
    plt.legend()
    plt.title("Simulation Vs Theoretical : Avg delay time on M/M/1 ")
    plt.show()


def plot_error_queue_len(real_data):
    plt.plot(cnt.LAMBDA, real_data, 'b', label='L error')
    plt.xlabel('Lambda Value')
    plt.ylabel('Average queue len')
    plt.legend()
    plt.title("Average queue len error ")
    plt.show()


def plot_error_time_spent(real_data):
    plt.plot(cnt.LAMBDA, real_data, 'b', label='W error')
    plt.xlabel('Lambda Value')
    plt.ylabel('Average time')
    plt.legend()
    plt.title("Average w error ")
    plt.show()

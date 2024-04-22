import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import os
import glob
import numpy as np
from tqdm import tqdm

def find_edges(signal, edge_type='rising'):
    """ Finds the indices of specified edges in the signal. """
    if edge_type == 'rising':
        return signal[signal.diff() == 1].index
    elif edge_type == 'falling':
        return signal[signal.diff() == -1].index

def calculate_clock_cycle_delays(enable_falling_edges, output_signal, clock_signal):
    """ Calculates delays in terms of integer clock cycles. """
    clock_period = np.median(np.diff(clock_signal[clock_signal.diff() == 1].index))  # Median period of the clock
    delay_values = []
    for enable_fall in enable_falling_edges:
        subsequent_output_change = output_signal[enable_fall:].diff().abs().idxmax()  # First change after enable falls
        if pd.notna(subsequent_output_change):
            clock_cycles = (subsequent_output_change - enable_fall) / clock_period
            delay_values.append(int(np.round(clock_cycles)))  # Round and convert to int
    return delay_values

def calculate_propagation_delays(clock_signal, output_signal):
    """ Calculates propagation delays in nanoseconds between clock and output signals. """
    clock_edges = find_edges(clock_signal, 'rising')
    delay_values = []
    for clock_edge in clock_edges:
        subsequent_output_change = output_signal[clock_edge:].diff().abs().idxmax()
        if pd.notna(subsequent_output_change):
            time_delay = (subsequent_output_change - clock_edge) * (1 / 50e6) * 1e6  # assuming 50 MHz clock frequency
            if 3 <= time_delay <= 8:  # Filtering delays to be within 3 to 8 nanoseconds
                delay_values.append(time_delay)
    return delay_values

if __name__ == "__main__":
    directory_path = r'C:\Users\Jeremy Hong\Documents\EE-4550\Final_Project\HWT\Trojan_Buffer_Chain\10MHz'
    print(f'Processing files in directory: {directory_path}')
    fpga_clock_delays = {}
    fpga_cycle_delays = {}

    for file_path in tqdm(glob.glob(os.path.join(directory_path, '*.csv'))):
        data = pd.read_csv(file_path, header=None, skiprows=8)
        clock_signal = data.iloc[:, 4]
        output_signal = data.iloc[:, 3]
        enable_signal = data.iloc[:, 2]

        cycle_delays = calculate_clock_cycle_delays(find_edges(enable_signal, 'falling'), output_signal, clock_signal)
        prop_delays = calculate_propagation_delays(clock_signal, output_signal)
        fpga_id = os.path.basename(file_path).split('_')[1]

        if cycle_delays:
            fpga_cycle_delays.setdefault(fpga_id, []).extend(cycle_delays)
        if prop_delays:
            fpga_clock_delays.setdefault(fpga_id, []).extend(prop_delays)

    # Plotting clock cycle delays
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    for fpga_id, delays in fpga_cycle_delays.items():
        plt.scatter([fpga_id] * len(delays), delays, label=f'{fpga_id} Cycle Delay')
    plt.xlabel('FPGA ID')
    plt.ylabel('Delay (Clock Cycles)')
    plt.title('Delay in Clock Cycles Across FPGAs')
    plt.xticks(rotation=45)
    plt.ylim(0, 20)
    plt.grid(True)
    plt.show()

    # Plotting propagation delays using box plot
    plt.figure(figsize=(10, 6))
    data_to_plot = [delays for delays in fpga_clock_delays.values() if delays]
    plt.boxplot(data_to_plot, labels=fpga_clock_delays.keys())
    plt.xlabel('FPGA ID')
    plt.ylabel('Propagation Delay (nanoseconds)')
    plt.title('Distribution of Propagation Delays Across FPGAs')
    plt.ylim(3, 7)
    plt.grid(True)
    plt.show()

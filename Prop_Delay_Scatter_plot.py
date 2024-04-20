# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:55:13 2024

@author: Jeremy Hong
"""

import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt

def calculate_propagation_delay(file_path):
    header_lines = 8
    try:
        data = pd.read_csv(file_path, header=None, skiprows=header_lines)
    except Exception as e:
        print(f"Failed to read the CSV file {file_path} correctly: {str(e)}")
        return  # Skip this file if it can't be read properly

    time = data.iloc[:, 0]
    input_signal = data.iloc[:, 1]
    output_signal = data.iloc[:, 2]

    def find_edges(signal, time_series, edge_type):
        if edge_type == 'rising':
            edges = (signal.shift(-1) < signal) & (signal == 1)
        elif edge_type == 'falling':
            edges = (signal.shift(-1) > signal) & (signal.shift(-1) == 1)
        return time_series[edges].values

    delays = {}
    for edge_type in ['rising', 'falling']:
        input_edges = find_edges(input_signal, time, edge_type)
        output_edges = find_edges(output_signal, time, edge_type)
        min_edges = min(len(input_edges), len(output_edges))
        if min_edges > 0:
            delay_values = output_edges[:min_edges] - input_edges[:min_edges]
            positive_delays = delay_values[delay_values >= 0]
            if positive_delays.size > 0:
                average_delay = np.mean(positive_delays) * 1e9  # Convert to nanoseconds
                delays[edge_type] = average_delay
            else:
                delays[edge_type] = None  # Mark as None if no positive delays found
        else:
            delays[edge_type] = None  # Mark as None if no edges found

    return delays

if __name__ == "__main__":
    directory_path = r'C:\Users\Jeremy Hong\Documents\EE-4550\Final_Project\Buffers\FPGA_Prop_Delay\Test_Data'
    print(f'Processing files in directory: {directory_path}')
    fpga_avg_delays = {}

    for file_path in glob.glob(os.path.join(directory_path, '*.csv')):
        delays = calculate_propagation_delay(file_path)
        fpga_id = os.path.basename(file_path).split('_')[1]  # Extract FPGA ID from filename

        # Aggregate data for each FPGA
        for edge_type, delay in delays.items():
            if delay is not None:  # Only add valid delays
                if fpga_id not in fpga_avg_delays:
                    fpga_avg_delays[fpga_id] = {edge_type: [delay]}
                else:
                    if edge_type in fpga_avg_delays[fpga_id]:
                        fpga_avg_delays[fpga_id][edge_type].append(delay)
                    else:
                        fpga_avg_delays[fpga_id][edge_type] = [delay]

    # Calculate and print average delays for each FPGA, only if both rise and fall have valid data
    for fpga_id, delay_lists in fpga_avg_delays.items():
        if 'rising' in delay_lists and 'falling' in delay_lists and delay_lists['rising'] and delay_lists['falling']:  # Check both lists have data
            avg_rise = np.mean(delay_lists['rising'])
            avg_fall = np.mean(delay_lists['falling'])
            print(f'FPGA {fpga_id} - Average Prop Delay Rise Time: {avg_rise:.5f} nanoseconds, Average Prop Delay Fall Time: {avg_fall:.5f} nanoseconds')


    # Prepare data for plotting
    data_for_plot = {'FPGA': [], 'Delay': [], 'Edge Type': []}
    for fpga_id, delay_lists in fpga_avg_delays.items():
        if 'rising' in delay_lists and 'falling' in delay_lists:
            data_for_plot['FPGA'].extend([fpga_id] * len(delay_lists['rising']))
            data_for_plot['Delay'].extend(delay_lists['rising'])
            data_for_plot['Edge Type'].extend(['Rising'] * len(delay_lists['rising']))
            
            data_for_plot['FPGA'].extend([fpga_id] * len(delay_lists['falling']))
            data_for_plot['Delay'].extend(delay_lists['falling'])
            data_for_plot['Edge Type'].extend(['Falling'] * len(delay_lists['falling']))

    # Convert to DataFrame for easier plotting
    plot_data = pd.DataFrame(data_for_plot)

    # Plotting
    plt.figure(figsize=(10, 6))
    for edge_type, group_data in plot_data.groupby('Edge Type'):
        plt.scatter(group_data['FPGA'], group_data['Delay'], label=edge_type, alpha=0.6)

    plt.xlabel('FPGA ID')
    plt.ylabel('Propagation Delay (nanoseconds)')
    plt.title('Propagation Delay Across FPGAs')
    plt.legend()
    plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability
    plt.grid(True)
    plt.show()

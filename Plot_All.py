# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 16:59:45 2024

@author: Jeremy Hong
"""

import os
import matplotlib.pyplot as plt
import skrf as rf
from matplotlib.lines import Line2D  # for custom legend entries

def plot_return_loss(directories):
    plt.figure(figsize=(10, 6))

    # Define colors and labels for each category
    categories = {
        'HWT_OFF': {'color': 'blue', 'label': 'FPGA w/HWT power off'},
        'HWT_ON': {'color': 'green', 'label': 'FPGA w/HWT power on'},
        'OFF': {'color': 'black', 'label': 'FPGA power on'},
        'ON': {'color': 'red', 'label': 'FPGA power off'}
    }
    legend_added = {key: False for key in categories}  # Track which legends have been added

    for directory in directories:
        for file in os.listdir(directory):
            if file.endswith('.s1p') and ('FPGA' in file):
                full_path = os.path.join(directory, file)
                network = rf.Network(full_path)

                # Determine which category the file belongs to
                category = None
                for cat in categories:
                    if cat in file:
                        category = cat
                        break

                if category is None:
                    continue  # Skip files that don't match the expected naming

                color = categories[category]['color']
                label = categories[category]['label'] if not legend_added[category] else None
                legend_added[category] = True

                # Plot the return loss
                network.plot_s_db(m=0, n=0, label=label, color=color)

    # Create custom legend handles based on the categories defined
    legend_handles = [Line2D([0], [0], color=info['color'], lw=4, label=info['label']) for info in categories.values()]

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Return Loss (dB)')
    plt.title('Return Loss Plot Across On/Off Conditions')
    plt.legend(handles=legend_handles)
    plt.grid(True)
    plt.show()

# Example usage:
directories = [r'C:\Users\Jeremy Hong\Documents\EE-4550\Final_Project\Silicon_Echoes\HWT_S_Params', r'C:\Users\Jeremy Hong\Documents\EE-4550\Final_Project\Silicon_Echoes\No_HWT_S_Params']
plot_return_loss(directories)

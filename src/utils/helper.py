import pandas as pd
import numpy as np


def create_bin_ranges(lower_bound: int, upper_bound: int, bin_size: int) -> list:
    """
    Create a list of string ranges from lower_bound up to upper_bound,
    in steps of bin_size.

    Example:
        lower_bound = 1, upper_bound = 10, bin_size = 3
        Output = ['1-3', '4-6', '7-9', '10-10']
    """
    bins = []
    start = lower_bound

    while start <= upper_bound - 1:
        end = min(start + bin_size - 1, upper_bound)
        bins.append(f"{int(start)} to {int(end)}")
        start += bin_size

    return bins


def adjust_raw_histogram_to_specified_range(raw_histogram, lower_bound, upper_bound, bin_size):
    bin_names = [x[1] for x in raw_histogram]
    requested_bin_names = create_bin_ranges(lower_bound, upper_bound, bin_size)
    raw_histogram = np.array(raw_histogram)[:, 2].astype('float')
    histogram = {}
    for i in range(len(bin_names)):
        histogram[bin_names[i]] = raw_histogram[i]
    requested_histogram = pd.DataFrame(data=[[0.0] * len(requested_bin_names)], columns=requested_bin_names)
    histogram = pd.DataFrame(histogram, index=[0])
    for col in histogram.columns:
        if col in requested_histogram.columns:
            requested_histogram.at[0, col] = histogram.at[0, col]
    return requested_histogram

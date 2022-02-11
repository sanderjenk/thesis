import numpy as np

def get_individuals_by_bit_array(df, bit_array):
    indices = np.array(bit_array == 1)
    return df.iloc[indices]
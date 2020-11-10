import numpy as np
import matplotlib.pyplot as plt
import random

# Sine wave
SR = 20 # No. samples in one period
N = 50 # No. periods
t = np.arange(N * SR)
signal = np.sin(2*np.pi/SR*t) * 10
print(list(signal))

plt.plot(t, signal)
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.show()

# # normal distribution with spike
# mean = 10
# std = 1
# spike_std = 2
# spike_number = 4
# list_length = 500
# out = [round(x, 4) for x in list(np.random.normal(mean, std, list_length))]
# for i in range(3):
# 	out[random.randint(0, list_length-1)] = mean + np.random.normal(mean, spike_std, 1)[0]
# print(out)
import matplotlib.pyplot as plt
import numpy as np
import pandas
import argparse
import io
import base64

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, type=str,
                        help='Configuration file for this simulation')
    args = parser.parse_args()

    df = pandas.read_csv(args.file, header=None)
    df.loc[:, 1] = (df.loc[:, 1].ffill()+df.loc[:, 1].bfill())/2
    df.loc[:, 2] = (df.loc[:, 2].ffill()+df.loc[:, 2].bfill())/2
    # df.loc[:, 3] = (df.loc[:, 3].ffill()+df.loc[:, 3].bfill())/2
    # df.loc[:, 4] = (df.loc[:, 4].abs().ffill()+df.loc[:, 4].abs().bfill())/2
    print(list(df.loc[:, 0]))


    fig, ax1 = plt.subplots()
    color = 'tab:blue'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('data value', color='tab:blue')
    line_1, = ax1.plot(df.loc[:, 1], color=color, label='temperature')
    line_2, = ax1.plot(df.loc[:, 2], color='tab:green', label='moving average temperature')
    plt.legend(handles=[line_1, line_2])
    # ax1.plot(df.loc[:, 1], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    # color = 'tab:orange'
    # ax2.set_ylabel('anomaly score', color=color)  # we already handled the x-label with ax1
    # line_1, = ax2.plot(df.loc[:, 3], color=color, label='anomaly score')
    # # line_2, = ax2.plot(df.loc[:, 4], color='tab:green', label='delta anomaly score')
    # ax2.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    # plt.legend(handles=[line_1, line_2])
    # plt.show()

    # print(df.loc[:, 0])
    # plt.plot(df.loc[:, 0], label='data', )
    # plt.plot(df.loc[:, 2], label='anomaly')

    # plt.xlabel('x')
    # plt.ylabel('y')
    # plt.title('Data and anomaly score')
    # plt.legend()
    # plt.show()

if __name__ == '__main__':
    main()

import os
import json
import requests
import logging
import io
import pandas as pd
import base64

import torch
import torch.nn as nn
import torch.utils.data
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt


logger = logging.getLogger(__name__)
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

class LSTM(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=50, output_size=1, layers=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.input_size = input_size
        self.lstm = nn.LSTM(input_size, self.hidden_layer_size,
                            num_layers=layers).to(device)
        self.linear = nn.Linear(hidden_layer_size, output_size).to(device)

    def forward(self, input_seq):
        lstm_out, _ = self.lstm(input_seq)
        predictions = self.linear(lstm_out)
        return predictions


def model_fn(model_dir):
    logger.info('Loading the model.')
    print('!!!!!!!!!!!! Model dir:')
    print(model_dir)
    model = LSTM()
    with open('model.pth', 'rb') as f:
        model.load_state_dict(torch.load(f, map_location=torch.device(device)))
    model.to(device).eval()
    logger.info('Done loading model')
    return model


def input_fn(request_body, content_type='text/csv'):
    print('!!!!!!!!!!!!!!!!!! Deserializing the input data.')
    print(request_body)
    if content_type == 'text/csv':
        df = pd.read_csv(io.BytesIO(request_body.encode('utf-8')), encoding='utf8', header=None)
        concat_data = None
        for i in range(len(df.dtypes)):
            print(i)
            if df.dtypes[i] == 'float64':
                if concat_data is None:
                    concat_data = torch.FloatTensor(df.iloc[:,i]).view(1, df.iloc[:,i].shape[0])
                else:
                    print(concat_data.shape)
                    print(torch.FloatTensor(df.iloc[:,i]).view(1, df.iloc[:,i].shape[0]).shape)
                    concat_data = torch.cat((concat_data, torch.FloatTensor(df.iloc[:,i]).view(1, df.iloc[:,i].shape[0]) ), 0)
        data_out = concat_data.transpose(0,1).view(concat_data.shape[1] ,concat_data.shape[0])
        return data_out
    raise Exception(f'Requested unsupported ContentType in content_type {content_type}')

def predict_fn(input_data, model):
    if (input_data is None or model is None):
        logger.info(input_data)
        logger.info(model)
        logger.info('Empty input data or model.')
    scaler = MinMaxScaler(feature_range=(-1, 1))
    normalized_input = torch.FloatTensor(scaler.fit_transform(input_data))
    print(normalized_input)
    normalized_input = normalized_input.view(normalized_input.shape[0] ,normalized_input.shape[1], 1)
    # print(normalized_input)
    readings_data = normalized_input[:-1, :, :]
    readings_labels = normalized_input[1:, :, :]
    data_loss = []
    print(readings_data.shape, readings_labels.shape)
    #     return None
    if torch.cuda.is_available():
        readings_data = readings_data.to(device)
        readings_labels = readings_labels.to(device)
    test_pred = model(readings_data)
    loss_function = nn.MSELoss()
    for i in range(readings_labels.shape[1]):
        data_loss.append(loss_function(test_pred[:, i, :], readings_labels[:, i, :]).item())
    return (test_pred, readings_labels, data_loss)

def output_fn(prediction_output, accept='application/json'):
    test_pred, readings_labels, data_loss = prediction_output
    plt.figure(figsize=(10,5))
    plt.grid(True)
    plt.title('Ingested Data and Prediction Plot')
    plt.autoscale(axis='x', tight=True)
    legend_handles = []
    for i in range(readings_labels.shape[1]):
        normal_real, = plt.plot(readings_labels.cpu().detach()[:, i, :], label='Real_{}'.format(i))
        normal_pred, = plt.plot(test_pred.cpu().detach()[:, i, :], label='Predicted_{}'.format(i))
        legend_handles.append(normal_real)
        legend_handles.append(normal_pred)
    plt.legend(handles=legend_handles)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    result = {
        "prediction_loss_by_colum_index": data_loss,
        "plot": base64.b64encode(buf.read()).decode("utf-8")
    }
    if accept == 'application/json':
        return json.dumps(result), accept
    raise Exception(f'Requested unsupported ContentType in Accept:{accept}')

import numpy as np
import pandas as pd
import xlrd 
import matplotlib.pyplot as plt
from keras.layers import Dense, Activation, Dropout
from keras.models import Sequential
from keras.models import model_from_json
from sklearn.preprocessing import StandardScaler
from keras.callbacks import EarlyStopping
from keras import backend
from keras import optimizers
import h5py
import sklearn.metrics, math
from sklearn import model_selection
from sklearn.linear_model import LinearRegression  
from sklearn.utils import check_array
from keras import regularizers

import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
RESOURCES = os.path.join(APP_ROOT, '../resources/inputs/')

#-----------------------------------------------------------------------------
#  Custom Loss Functions
#-----------------------------------------------------------------------------

# root mean squared error (rmse) for regression
def rmse(y_obs, y_pred):
    return backend.sqrt(backend.mean(backend.square(y_pred - y_obs), axis=-1))

# mean squared error (mse) for regression
def mse(y_obs, y_pred):
    return backend.mean(backend.square(y_pred - y_obs), axis=-1)

# coefficient of determination (R^2) for regression
def r_square(y_obs, y_pred):
    SS_res =  backend.sum(backend.square(y_obs - y_pred)) 
    SS_tot = backend.sum(backend.square(y_obs - backend.mean(y_obs))) 
    return (1 - SS_res/(SS_tot + backend.epsilon()))

def mean_absolute_percentage_error(y_obs, y_pred): 
    #y_obs, y_pred = np.array(y_obs), np.array(y_pred)
    y_obs=y_obs.reshape(-1,1)
    #y_obs, y_pred =check_array(y_obs, y_pred)
    return  np.mean(np.abs((y_obs - y_pred) / y_obs)) * 100

def execute_model_12(data):

    #data = pd.read_csv('DAFD_transfer_learning_regime_1.csv', delimiter=';')
    #print('*******************', filename)
    #data = pd.read_csv(filename, delimiter=delimiter)
    #print(data)

    X1 = data[['Orifice width', 'Aspect ratio', 'Expansion ratio', 'Normalized orifice length',
                'Normalized water inlet', 'Normalized oil inlet', 'Flow rate ratio', 'capillary']]
    Y12 = data['Size']

    #for col in X1.columns:
    #    if col != 'Orifice width' and col != 'Expansion ratio':
    #        X1[col] = X1[col].str.replace(',', '.')

    ###train-test split
    validation_size = 0.20

    X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X1, Y12, test_size=validation_size) #Regime 1 Output 2

    ###data scaling
    scaler=StandardScaler().fit(X_train)
    X_train=scaler.transform(X_train)
    X_test=scaler.transform(X_test)

    X_train =np.array(X_train)
    Y_train=np.array(Y_train)
    X_test =np.array(X_test)
    Y_test =np.array(Y_test)
    Y12 = np.array(Y12)

    #-----------------------------------------------------------------------------
    #   Training Nueral Network Model
    #-----------------------------------------------------------------------------

    ### Initializing NN and Define initial structure as the saved model
    TLmodel = Sequential()
    ### load first layer weights and keep unchanged to avoid over-fitting
    TLmodel.add(Dense(units = 16, input_dim=8, activation='relu', name='dense_1', trainable=False))
    ### load second layer weights and keep unchanged to avoid over-fitting
    TLmodel.add(Dense(units = 16, activation='relu', name='dense_2', trainable=False))
    #TLmodel.add(Dropout(0.4))
    ### update 3rd layer weights to fit the data
    TLmodel.add(Dense(units = 8, activation='relu', name='new_dense_3'))
    #TLmodel.add(Dropout(0.4))
    ### update last layer weights to fit the data
    TLmodel.add(Dense(units = 1, name='new_dense4'))#, kernel_regularizer=regularizers.l2(0.001)))

    #-----------------------------------------------------------------------------
    #   Load the Pre-Trained Nueral Network Model
    #-----------------------------------------------------------------------------
    #Load saved weights
    TLmodel.load_weights(os.path.join(RESOURCES, 'Y12_weights.h5'), by_name=True)

    ### Optimizer
    adam=optimizers.Adam(lr=0.006)#(lr=0.001,beta_1=0.9, beta_2=0.999, amsgrad=False)

    ### Compiling the NN
    TLmodel.compile(optimizer = adam, loss = 'mean_squared_error',metrics=['mean_squared_error', rmse, r_square] )

    ### Early stopping
    earlystopping=EarlyStopping(monitor="mean_squared_error", patience=5, verbose=1, mode='auto')

    ### Fitting the model to the train set
    result = TLmodel.fit(X_train, Y_train, validation_data=(X_test, Y_test), batch_size = 1, epochs = 700, callbacks=[earlystopping])

    #-----------------------------------------------------------------------------
    #   Predictions of the Trained Nueral Network Model
    #-----------------------------------------------------------------------------
    ### Test-set prediction
    y_pred = TLmodel.predict(X_test)
    ### train-set prediction
    y_pred_train = TLmodel.predict(X_train)

    ##-----------------------------------------------------------------------------
    ##  statistical Summary
    ##-----------------------------------------------------------------------------
    
    mae_score = sklearn.metrics.mean_absolute_error(Y_test,y_pred)
    mse_score = sklearn.metrics.mean_squared_error(Y_test,y_pred)
    rmse_score = math.sqrt(sklearn.metrics.mean_squared_error(Y_test,y_pred))
    r2_score = sklearn.metrics.r2_score(Y_test,y_pred)

    print("\n")
    print("Mean absolute error (MAE) for test-set:      %f" % sklearn.metrics.mean_absolute_error(Y_test,y_pred))
    print("Mean squared error (MSE) for test-set:       %f" % sklearn.metrics.mean_squared_error(Y_test,y_pred))
    print("Root mean squared error (RMSE) for test-set: %f" % math.sqrt(sklearn.metrics.mean_squared_error(Y_test,y_pred)))
    print("R square (R^2) for test-set:                 %f" % sklearn.metrics.r2_score(Y_test,y_pred))

    print("\n")
    print("Mean absolute error (MAE) for train-set:      %f" % sklearn.metrics.mean_absolute_error(Y_train, y_pred_train))
    print("Mean squared error (MSE) for train-set:       %f" % sklearn.metrics.mean_squared_error(Y_train, y_pred_train))
    print("Root mean squared error (RMSE) for train-set: %f" % math.sqrt(sklearn.metrics.mean_squared_error(Y_train, y_pred_train)))
    print("R square (R^2) for train-set:                 %f" % sklearn.metrics.r2_score(Y_train, y_pred_train))

    return mae_score, mse_score, rmse_score, r2_score

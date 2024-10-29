# import libraries
import os
import pandas as pd
import numpy as np
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import keras
import matplotlib as mp
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import MetaTrader5 as mt5
from dotenv import load_dotenv
    # Load environment variables from .env file (optional)
load_dotenv()
ACCOUNT = os.getenv('ACCOUNT')
SERVER = os.getenv('SERVER')
PASSWORD = os.getenv("PASSWORD")

# set parameters for results graphs
mp.rcParams.update({'font.family':'serif',
'font.serif':'Clear Sans',
'axes.labelsize':'medium',
'legend.fontsize':'small',
'figure.figsize':[6.0,4.0],
'xtick.labelsize':'small',
'ytick.labelsize':'small',
'axes.titlesize': 'x-large',
'axes.titlecolor': '#333333',
'axes.labelcolor': '#333333',
'axes.edgecolor': '#333333'
})
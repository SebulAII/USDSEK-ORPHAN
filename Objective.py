import backtrader as bt
import datetime
from strategiesTestowa import TestStrategy
import matplotlib
import itertools 
# from backtrader_plotting import Bokeh
# from backtrader_plotting.schemes import Tradimo
import numpy as np
import backtrader.analyzers as btanalyzers
import pandas as pd


def objective(trial):

    av_VIX_days = trial.suggest_int('av_VIX_days', 3,100)
    open_VIX = trial.suggest_float('open_VIX', 0.7, 1.5)
    close_vix = trial.suggest_float('close_vix', 1.001, 3)

    cerebro = bt.Cerebro()

    cerebro.broker.set_cash(1000000)

    instruments = ['USDSEK','VIX']


    for instrument in instruments:
        datapath = f"{instrument}.csv"
        # Create a Data Feed
        data = bt.feeds.GenericCSVData(
            dataname=datapath,
            fromdate=datetime.datetime(2005, 1, 3),
            todate=datetime.datetime(2022, 9, 17),
            reverse=False,
            dtformat="%Y-%m-%d",
            #dtformat = "%d%m%Y",
            openinterest=-1)
        cerebro.adddata(data, name=instrument)

    cerebro.addstrategy(TestStrategy, av_VIX_days=av_VIX_days, open_VIX =open_VIX, close_vix=close_vix)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    value = cerebro.run() 

    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.addwriter(bt.WriterFile, csv=True)

    profit = cerebro.broker.getvalue()

    # Mateusz: wartość minimalizujemy, więc musi być "minus" profit czy "minus" SR.
    return (-1) * value[0].profit_sum

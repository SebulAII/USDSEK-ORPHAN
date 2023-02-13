import backtrader
import numpy as np
import statistics as stats


class TestStrategy(backtrader.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # Mateusz: Dodałem alpha do innitu.
    def __init__(self, av_VIX_days, open_VIX, close_vix):
        self.dataclose = self.datas[0].close
        self.order = None
        #lists
        self.zmiana_w_pipsach_1 = []
        self.zmiana_w_pipsach_2 = []
        self.zmiana_w_pipsach_1_wersja2 = []
        self.zmiana_w_pipsach_2_wersja2 = []
        self.zmiennosc = []
        self.es_volatility = []
        self.differencePips = []
        self.ticketLong = None
        self.ticketShort = None
        self.ES_zmiany = []
        self.warmup = 42

        self.pair1ProfitList = []
        self.pair2ProfitList = []

        self.OrphanTicket = None
        self.OrphanValue = None
        #self.SL = SL
        #self.TP = 1.1

        self.pair1ProfitList = []
        self.pair2ProfitList = []

        self.SL_Long_list = []
        self.SL_Short_list = []
        self.opening_date = None
        self.OrphanLen = None

        self.av_VIX_days = av_VIX_days
        self.av_VIX_list = []
        self.open_VIX = open_VIX
        self.close_vix = close_vix


    def next(self):
        print(len(self))
        self.VIX= self.datas[1].close[0]
        self.av_VIX_list.append(self.VIX)

        if len(self) > self.av_VIX_days:
            self.profit_sum = sum(self.pair1ProfitList) + sum(self.pair2ProfitList)
            self.vol1open = 100000 #wolumen otwarcia 1 pozycji
            self.vol2open = -100000 #wolumen otwarcia 2 pozycj
            self.av_VIX = np.mean(self.av_VIX_list[:self.av_VIX_days])
            self.open_VIX_threshold = self.av_VIX * self.open_VIX
            self.close_VIX_threshold = self.av_VIX * self.close_vix

            self.low_vol = self.VIX <= self.open_VIX_threshold
            self.high_vol = self.VIX >= self.close_VIX_threshold

            if self.ticketLong is None and  self.ticketShort is None and self.opening_date is None: 
                if self.low_vol: 
                    self.ticketLong = 1
                    self.ticketShort = 1
                    self.opening_date = len(self)
            if self.ticketLong is not None or self.ticketShort is not None:
                if self.VIX > self.close_VIX_threshold:
                    self.OrphanLen = None
                    self.ticketLong = None
                    self.ticketShort = None
                    
            #Pozycje i brak sieroty
            if self.opening_date is not None:
                if len(self) >= self.opening_date +1:
                    if self.ticketLong is not None and self.ticketShort is not None:
                        self.pair1ProfitList.append(((self.vol1open * (self.datas[0].close[0] - self.datas[0].close[-1]))/self.datas[0].close[0])) 
                        self.pair2ProfitList.append((self.vol2open * (self.datas[0].close[0] - self.datas[0].close[-1]))/self.datas[0].close[0])
                #cena rośnie: przesuń SL i zamknij Shorta
                        if self.datas[0].close[0] > self.datas[0].close[-1]:
                            self.SL_Long_list.append(self.datas[0].close[0])
                            self.SL_Short_list.append(0)
                            self.ticketShort = None
                            self.OrphanLen = len(self)                
                        #cena maleje: przesuń SL i zamknij Longa
                        if self.datas[0].close[0] < self.datas[0].close[-1]:
                            self.SL_Short_list.append(self.datas[0].close[0])
                            self.SL_Long_list.append(0)
                            #self.pair2ProfitList.append((self.vol2open * (self.datas[1].close[0] - self.datas[1].close[-1]))/self.datas[1].close[0])
                            self.ticketLong = None
                            self.OrphanLen = len(self)                

                    #zamykamy Longa
                    if self.ticketLong == 1 and self.ticketShort == None and len(self) >= self.OrphanLen+1:
                        self.pair1ProfitList.append(((self.vol1open * (self.datas[0].close[0] - self.datas[0].close[-1]))/self.datas[0].close[0])) 
                        self.pair2ProfitList.append(0)
                        if  self.datas[0].close[0] < self.datas[0].close[-1]:
                            self.SL_Long_list.append(0)
                            self.ticketLong = None
                            self.opening_date = None
                            self.OrphanLen = None

                    #zamykamy Shorta
                    if self.ticketLong == None and self.ticketShort == 1 and len(self) >= self.OrphanLen + 1:
                        self.pair1ProfitList.append(0)
                        self.pair2ProfitList.append((self.vol2open * (self.datas[0].close[0] - self.datas[0].close[-1]))/self.datas[0].close[0])
                        if self.datas[0].close[0] > self.datas[0].close[-1]:
                            self.ticketShort = None
                            self.opening_date = None
                            self.OrphanLen = None
                    

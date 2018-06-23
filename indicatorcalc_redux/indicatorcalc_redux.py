import datetime
import logging
import os
from pprint import pprint
import sys

import numpy as np
from talib.abstract import EMA, MACD, RSI, SMA, STOCH

#logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class IndicatorCalc:
    def __init__(self):
        pass


    def aroon(self, data, length):
        aroon_values = {'Exception': False, 'Error': False,
                        'result': {'last': {'up': None, 'down': None, 'state': None},
                                   'current': {'up': None, 'down': None, 'state': None}}}

        try:
            #### DATA PREPARATION ####
            if 'close_time' not in data:
                #data['close_time'] = []
                close_times = []

                interval = data['open_time'][1] - data['open_time'][0]

                for x in range(0, len(data['open_time'])):
                    #data['close_time'].append(data['open_time'][x] + interval)
                    close_times.append(data['open_time'][x] + interval)

                data['close_time'] = np.array(close_times, dtype='f8')

            # Check to see if arrays need to be reversed (timestamp[0] should be most recent)
            if data['close_time'][0] < data['close_time'][-1]:
                logger.debug('Reversing data arrays for Aroon calculation.')

                array_data_categories = ['high', 'low', 'close_time']

                for category in array_data_categories:
                    data[category] = data[category][::-1]

            input_array_high = data['high']
            input_array_low = data['low']
            input_array_close_time = data['close_time']

            input_array_high_length = len(input_array_high)
            logger.debug('input_array_high_length: ' + str(input_array_high_length))

            input_array_low_length = len(input_array_low)
            logger.debug('input_array_low_length: ' + str(input_array_low_length))

            input_array_close_time_length = len(input_array_close_time)
            logger.debug('input_array_close_time_length: ' + str(input_array_close_time_length))

            if input_array_high_length != input_array_low_length:
                logger.error('Input data sets must have the same length.')

                arron_values['Error'] = True

            elif input_array_high_length < (length + 2):
                # ERROR (Not enough data)
                logger.error('Not enough data periods for Aroon calculation.')

                logger.error('Required: ' + str(int(length + 2)) + ' / ' +
                             'Given: ' + str(input_array_high_length))

                aroon_values['Error'] = True

            elif input_array_high_length > (length + 2):
                trim_length = int(input_array_high_length - (length + 2))
                logger.debug('trim_length: ' + str(trim_length))

                input_data_high = input_array_high[:(input_array_high_length - trim_length)]
                logger.debug('len(input_data_high): ' + str(len(input_data_high)))

                input_data_low = input_array_low[:(input_array_low_length - trim_length)]
                logger.debug('len(input_data_low): ' + str(len(input_data_low)))

                input_data_close_time = input_array_close_time[:(input_array_close_time_length - trim_length)]
                logger.debug('len(input_data_close_time): ' + str(len(input_data_close_time)))

            else:
                input_data_high = input_array_high
                input_data_low = input_array_low
                input_data_close_time = input_array_close_time

            if aroon_values['Error'] == True:
                logger.error('Error occurred while prepping Aroon data.')

            else:
                modified_data = {}

                modified_data['high'] = input_data_high
                modified_data['low'] = input_data_low
                modified_data['close_time'] = input_data_close_time

                #### AROON CALCULATION ####
                input_data = {'last': {'high': modified_data['high'][1:],
                                       'low': modified_data['low'][1:],
                                       'close_time': modified_data['close_time'][1:]},
                              'current': {'high': modified_data['high'][:-1],
                                          'low': modified_data['low'][:-1],
                                          'close_time': modified_data['close_time'][:-1]}}

                for timepoint in input_data:
                    high = np.amax(input_data[timepoint]['high'])
                    logger.debug('high: ' + str(high))

                    np_high_pos, = np.where(input_data[timepoint]['high'] == high)
                    if len(np_high_pos) > 1:
                        high_pos = int(np.amax(np_high_pos))
                    else:
                        high_pos = int(np_high_pos)
                    logger.debug('high_pos: ' + str(high_pos))

                    low = np.amin(input_data[timepoint]['low'])
                    logger.debug('low: ' + str(low))

                    np_low_pos, = np.where(input_data[timepoint]['low'] == low)
                    if len(np_low_pos) > 1:
                        low_pos = int(np.amin(np_low_pos))
                    else:
                        low_pos = int(np_low_pos)
                    logger.debug('low_pos: ' + str(low_pos))

                    #periods_since_max = high_pos
                    periods_since_max = length - high_pos
                    logger.debug('periods_since_max: ' + str(periods_since_max))
                    #periods_since_min = low_pos
                    periods_since_min = length - low_pos
                    logger.debug('periods_since_min: ' + str(periods_since_min))

                    #aroon_up = round((((length - periods_since_max) / length) * 100), 2)
                    aroon_up = round(((periods_since_max / length) * 100), 2)
                    logger.debug('aroon_up: ' + str(aroon_up))
                    #aroon_down = round((((length - periods_since_min) / length) * 100), 2)
                    aroon_down = round(((periods_since_min / length) * 100), 2)
                    logger.debug('aroon_down: ' + str(aroon_down))

                    if aroon_up > aroon_down:
                        aroon_state = 'positive'

                    elif aroon_up == aroon_down:
                        aroon_state = 'even'

                    else:
                        aroon_state = 'negative'

                    aroon_values['result'][timepoint]['up'] = aroon_up
                    aroon_values['result'][timepoint]['down'] = aroon_down
                    aroon_values['result'][timepoint]['state'] = aroon_state

        except Exception as e:
            logger.exception('Exception while calculating Aroon.')
            logger.exception(e)

            aroon_values['Exception'] = True

        finally:
            return aroon_values


    def rsi(self, data, length, price_input='close'):
        rsi_values = {'Exception': False, 'result': {'data': None, 'current': None, 'state': None}}

        try:
            results = RSI(data,
                          timeperiod=period_count,
                          prices=price_input)

            rsi_values['result']['data'] = results#[-1]

            rsi_values['result']['current'] = results[-1]

            if rsi_values['result']['current'] > 50:
                rsi_state = 'positive'

            elif rsi_values['result']['current'] == 50:
                rsi_state = 'even'

            else:
                rsi_state = 'negative'

            rsi_values['result']['state'] = rsi_state

        except Exception as e:
            logger.exception('Exception while calculating RSI.')
            logger.exception(e)

            rsi_values['Exception'] = True

        finally:
            return rsi_values


    def stochasticrsi(self, data, length):
        stochrsi_values = {'Exception': False, 'result': {'current': None}}

        try:
            sliced = data[int(-1 * length):]

            current = sliced[-1]

            low = np.min(sliced)
            high = np.max(sliced)

            stochrsi_values['result']['current'] = (current - low) / (high - low)

        except Exception as e:
            logger.exception('Exception while calculating Stochastic RSI.')
            logger.exception(e)

            stochrsi_values['Exception'] = True

        finally:
            return stochrsi_values


    def ema(self, data, length_short, length_long, price_input='close'):
        ema_values = {'Exception': False,
                      'result': {'short': {'data': None, 'current': None},
                                 'long': {'data': None, 'current': None},
                                 'state': None}}

        try:
            ema_inputs = {'short': length_short, 'long': length_long}

            for ema in ema_inputs:
                length = ema_inputs[ema]

                results = EMA(data,
                              timeperiod=length,
                              prices=price_input)

                ema_values['result'][ema]['data'] = results#[-1]

                ema_values['result'][ema]['current'] = results[-1]

            #if ema_values['result']['short'] > ema_values['result']['long']:
            if ema_values['result']['short']['current'] > ema_values['result']['long']['current']:
                ema_state = 'positive'

            #elif ema_values['result']['short'] == ema_values['result']['long']:
            elif ema_values['result']['short']['current'] == ema_values['result']['long']['current']:
                ema_state = 'even'

            else:
                ema_state = 'negative'

            ema_values['result']['state'] = ema_state

        except Exception as e:
            logger.exception('Exception while calculating EMA.')
            logger.exception(e)

            ema_values['Exception'] = True

        finally:
            return ema_values


    def stochastic(self, data, length=14, smoothk=3, smoothd=3, price_input='close'):
        stoch_values = {'Exception': False, 'result': {'smoothk': {'data': None, 'current': None},
                                                       'smoothd': {'data': None, 'current': None},
                                                       'average': None,
                                                       'state': None}}

        try:
            #length = 14
            #smoothk = 3
            smoothk_matype = 0
            #smoothd = 3
            smoothd_matype = 0

            smoothk, smoothd = STOCH(data, length, smoothk, smoothk_matype, smoothd, smoothd_matype)

            stoch_values['result']['smoothk']['data'] = smoothk
            stoch_values['result']['smoothk']['current'] = smoothk[-1]

            stoch_values['result']['smoothd']['data'] = smoothd
            stoch_values['result']['smoothd']['current'] = smoothd[-1]

            stoch_values['result']['average'] = (smoothk[-1] + smoothd[-1]) / 2

            if stoch_values['result']['smoothk']['current'] > stoch_values['result']['smoothd']['current']:
                stoch_state = 'positive'

            elif stoch_values['result']['smoothk']['current'] == stoch_values['result']['smoothd']['current']:
                stoch_state = 'even'

            else:
                stoch_state = 'negative'

            stoch_values['result']['state'] = stoch_state

        except Exception as e:
            logger.exception('Exception while calculating stochastic.')
            logger.exception(e)

            stoch_values['Exception'] = True

        finally:
            return stoch_values


# ADD NOW
def sma(self, data, length, price_input='close'):
    sma_values = {'Exception': False, 'result': {'data': None, 'current': None, 'state': None}}

    try:
        # uses open prices
        results = SMA(data, timeperiod=length, price='close')

        sma_values['result']['data'] = results

        sma_values['result']['current'] = results[-1]

        if sma_values['result']['current'] > 50:
            sma_state = 'positive'

        elif sma_values['result']['current'] == 50:
            sma_state = 'even'

        else:
            sma_state = 'negative'

        sma_values['result']['state'] = sma_state

    except Exception as e:
        logger.exception('Exception while calculating SMA.')
        logger.exception(e)

    finally:
        return sma_values


def macd(self):
    macd_values = {'Exception': False}

    try:
        macd, macdsignal, macdhist = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    except Exception as e:
        logger.exception('Exception while calculating MACD.')
        logger.exception(e)

        macd_values['Exception'] = True

    finally:
        return macd_values


# ADD LATER
def bollinger_bands(self):
    pass


def fibonacci_levels(self):
    pass


def ichimoku_cloud(self):
    pass


if __name__ == '__main__':
    indicator_calc = IndicatorCalc()

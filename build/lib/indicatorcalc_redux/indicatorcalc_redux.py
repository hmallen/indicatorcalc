import datetime
import logging
import os
from pprint import pprint
import sys

import numpy as np
from talib.abstract import BBANDS, EMA, MACD, RSI, SMA, STOCH

#logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class IndicatorCalc:
    def __init__(self):
        pass


    def aroon(self, data, length):
        aroon_values = {'success': True,
                        'result': {'last': {'up': None, 'down': None, 'state': None},
                                   'current': {'up': None, 'down': None, 'state': None}}}

        data_copy = data.copy()

        try:
            #### DATA PREPARATION ####
            if 'close_time' not in data_copy:
                #data_copy['close_time'] = []
                close_times = []

                interval = data_copy['open_time'][1] - data_copy['open_time'][0]

                for x in range(0, len(data_copy['open_time'])):
                    #data_copy['close_time'].append(data_copy['open_time'][x] + interval)
                    close_times.append(data_copy['open_time'][x] + interval)

                data_copy['close_time'] = np.array(close_times, dtype='f8')

            # Check to see if arrays need to be reversed (timestamp[0] should be most recent)
            if data_copy['close_time'][0] < data_copy['close_time'][-1]:
                logger.debug('Reversing data arrays for Aroon calculation.')

                array_data_categories = ['high', 'low', 'close_time']

                for category in array_data_categories:
                    data_copy[category] = data_copy[category][::-1]

            input_array_high = data_copy['high']
            input_array_low = data_copy['low']
            input_array_close_time = data_copy['close_time']

            input_array_high_length = len(input_array_high)
            logger.debug('input_array_high_length: ' + str(input_array_high_length))

            input_array_low_length = len(input_array_low)
            logger.debug('input_array_low_length: ' + str(input_array_low_length))

            input_array_close_time_length = len(input_array_close_time)
            logger.debug('input_array_close_time_length: ' + str(input_array_close_time_length))

            if input_array_high_length != input_array_low_length:
                logger.error('Input data sets must have the same length.')

                #aroon_values['Error'] = True
                aroon_values['success'] = False

            elif input_array_high_length < (length + 2):
                # ERROR (Not enough data)
                logger.error('Not enough data periods for Aroon calculation.')

                logger.error('Required: ' + str(int(length + 2)) + ' / ' +
                             'Given: ' + str(input_array_high_length))

                #aroon_values['Error'] = True
                aroon_values['success'] = False

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

            #if aroon_values['Error'] == True:
            if aroon_values['success'] == False:
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

            #aroon_values['Exception'] = True
            aroon_values['success'] = False

        finally:
            return aroon_values


    def rsi(self, data, length, price_input='close'):
        rsi_values = {'success': True, 'result': {'data': None, 'current': None, 'state': None}}

        data_copy = data.copy()

        try:
            results = RSI(data_copy, timeperiod=length, prices=price_input)

            rsi_values['result']['data'] = results

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

            rsi_values['success'] = False

        finally:
            return rsi_values


    def stochasticrsi(self, data, length, price_input='close'):
        stochrsi_values = {'success': True, 'result': {'current': None, 'state': None}}

        data_copy = data.copy()

        try:
            #sliced = data_copy[int(-1 * length):]
            sliced = data_copy[price_input][int(-1 * length):]

            current = sliced[-1]

            low = np.min(sliced)
            high = np.max(sliced)

            stochrsi_values['result']['current'] = (current - low) / (high - low)

            if stochrsi_values['result']['current'] > 0.5:
                stochrsi_state = 'positive'

            elif stochrsi_values['result']['current'] == 0.5:
                stochrsi_state = 'even'

            else:
                stochrsi_state = 'negative'

            stochrsi_values['result']['state'] = stochrsi_state

        except Exception as e:
            logger.exception('Exception while calculating Stochastic RSI.')
            logger.exception(e)

            stochrsi_values['success'] = False

        finally:
            return stochrsi_values


    def ema(self, data, length_short, length_long=None, price_input='close'):
        ema_values = {'success': True,
                      'result': {'short': {'data': None, 'current': None},
                                 'long': {'data': None, 'current': None},
                                 'state': None}}

        data_copy = data.copy()

        try:
            ema_inputs = {'short': length_short, 'long': length_long}

            for ema in ema_inputs:
                if ema_inputs[ema] != None:
                    length = ema_inputs[ema]

                    results = EMA(data_copy, timeperiod=length, prices=price_input)

                    ema_values['result'][ema]['data'] = results

                    ema_values['result'][ema]['current'] = results[-1]

            if length_long != None:
                if ema_values['result']['short']['current'] > ema_values['result']['long']['current']:
                    ema_state = 'positive'

                elif ema_values['result']['short']['current'] == ema_values['result']['long']['current']:
                    ema_state = 'even'

                else:
                    ema_state = 'negative'

                ema_values['result']['state'] = ema_state

        except Exception as e:
            logger.exception('Exception while calculating EMA.')
            logger.exception(e)

            ema_values['success'] = False

        finally:
            return ema_values


    def stochastic(self, data, length=14, smoothk=3, smoothd=3, price_input=['high', 'low', 'close']):
        stoch_values = {'success': True, 'result': {'smoothk': {'data': None, 'current': None},
                                                    'smoothd': {'data': None, 'current': None},
                                                    'average': None,
                                                    'state': None}}

        data_copy = data.copy()

        try:
            #length = 14
            #smoothk = 3
            smoothk_matype = 0
            #smoothd = 3
            smoothd_matype = 0

            smoothk, smoothd = STOCH(data_copy, length, smoothk, smoothk_matype, smoothd, smoothd_matype, prices=price_input)

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

            stoch_values['success'] = False

        finally:
            return stoch_values


    def sma(self, data, length, price_input='close'):
        sma_values = {'success': True, 'result': {'data': None, 'current': None}}#, 'state': None}}

        data_copy = data.copy()

        try:
            # uses open prices?
            results = SMA(data_copy, timeperiod=length, price='close')

            sma_values['result']['data'] = results

            sma_values['result']['current'] = results[-1]

            """
            if sma_values['result']['current'] > 50:
                sma_state = 'positive'

            elif sma_values['result']['current'] == 50:
                sma_state = 'even'

            else:
                sma_state = 'negative'

            sma_values['result']['state'] = sma_state
            """

        except Exception as e:
            logger.exception('Exception while calculating SMA.')
            logger.exception(e)

            sma_values['success'] = False

        finally:
            return sma_values


    def macd(self, data, length_fast=12, length_slow=26, length_signal=9, price_input='close'):
        macd_values = {'success': True, 'result': {'macd': {'data': None, 'current': None},
                                                   'signal': {'data': None, 'current': None},
                                                   'histogram': {'data': None, 'current': None}}}

        data_copy = data.copy()

        try:
            macd, signal, histogram = MACD(data_copy, fastperiod=length_fast, slowperiod=length_slow,
                                           signalperiod=length_signal, price=price_input)

            macd_values['result']['macd']['data'] = macd
            macd_values['result']['macd']['current'] = macd[-1]

            macd_values['result']['signal']['data'] = signal
            macd_values['result']['signal']['current'] = signal[-1]

            macd_values['result']['histogram']['data'] = histogram
            macd_values['result']['histogram']['current'] = histogram[-1]

        except Exception as e:
            logger.exception('Exception while calculating MACD.')
            logger.exception(e)

            macd_values['success'] = False

        finally:
            return macd_values


    def volume(self, data, threshold):
        volume_values = {'success': True, 'result': {'volume': None, 'reached': None}}

        data_copy = data.copy()

        try:
            volume_values['result']['volume'] = data_copy['volume'][-1]

            if volume_values['result']['volume'] >= threshold:
                volume_values['result']['reached'] = True

            else:
                volume_values['result']['reached'] = False

        except Exception as e:
            logger.exception('Exception while calculating volume.')
            logger.exception(e)

            volume_values['success'] = False

        finally:
            return volume_values


    def bollinger_bands(self, data, length, nbdevup, nbdevdown=None, price_input='close'):
        bollinger_bands_values = {'success': True, 'result': {'upper': {'data': None, 'current': None},
                                                              'middle': {'data': None, 'current': None},
                                                              'lower': {'data': None, 'current': None}}}

        data_copy = data.copy()

        try:
            if nbdevdown == None:
                nbdevdown = nbdevup

            upper, middle, lower = BBANDS(data_copy, timeperiod=length, nbdevup=nbdevup, nbdevdn=nbdevdown, matype=0, prices=price_input)

            logger.debug('upper[-1]: ' + str(upper[-1]))
            logger.debug('middle[-1]: ' + str(middle[-1]))
            logger.debug('lower[-1]: ' + str(lower[-1]))

            bollinger_bands_values['result']['upper']['data'] = upper
            bollinger_bands_values['result']['upper']['current'] = upper[-1]

            bollinger_bands_values['result']['middle']['data'] = middle
            bollinger_bands_values['result']['middle']['current'] = middle[-1]

            bollinger_bands_values['result']['lower']['data'] = lower
            bollinger_bands_values['result']['lower']['current'] = lower[-1]

        except Exception as e:
            logger.exception('Exception while calculating Bollinger bands.')
            logger.exception(e)

            bollinger_band_values['success'] = False

        finally:
            return bollinger_bands_values


    """
    def fibonacci_levels(self):
        fibonacci_values = {'success': True, 'result': {}}

        try:
            pass

        except Exception as e:
            logger.exception('Exception while calculating Fibonacci levels.')
            logger.exception(e)

            fibonacci_values['success'] = False

        finally:
            return fibonacci_values
    """


    def ichimoku_cloud(self, data, length_tenkan=9, length_kijun=26, length_senkou=52):
        ichimoku_values = {'success': True, 'result': {'tenkan': {'data': None, 'current': None},
                                                       'kijun': {'data': None, 'current': None},
                                                       'senkou_a': {'data': None, 'current': None},
                                                       'senkou_b': {'data': None, 'current':None},
                                                       'chikou': {'data': None, 'current': None}}}

        data_copy = data.copy()

        """
        Tenkan-sen = (9-day high + 9-day low) / 2
        Kijun-sen = (26-day high + 26-day low) / 2
        Senkou Span A = (Tenkan-sen + Kijun-sen) / 2
        Senkou Span B = (52-day high + 52-day low) / 2
        Chikou Span = Close plotted 26-days in the past.
        """

        try:
            # Tenkan-sen
            data_short_low = data_copy['low'][(-1 * length_tenkan):]
            data_short_high = data_copy['high'][(-1 * length_tenkan):]

            data_short_min = np.min(data_short_low)
            data_short_max = np.max(data_short_high)

            tenkan_sen = (data_short_min + data_short_max) / 2
            logger.debug('tenkan_sen: ' + str(tenkan_sen))

            ichimoku_values['result']['tenkan']['current'] = tenkan_sen

            # Kijun-sen
            data_med_low = data_copy['low'][(-1 * length_kijun):]
            data_med_high = data_copy['high'][(-1 * length_kijun):]

            data_med_min = np.min(data_med_low)
            data_med_max = np.max(data_med_high)

            kijun_sen = (data_med_min + data_med_max) / 2
            logger.debug('kijun_sen: ' + str(kijun_sen))

            ichimoku_values['result']['kijun']['current'] = kijun_sen

            # Senkou Span A
            senkou_span_a = (tenkan_sen + kijun_sen) / 2
            logger.debug('senkou_span_a: ' + str(senkou_span_a))

            ichimoku_values['result']['senkou_a']['current'] = senkou_span_a

            # Senkou Span B
            data_long_low = data_copy['low'][(-1 * length_senkou):]
            data_long_high = data_copy['high'][(-1 * length_senkou):]

            data_long_min = np.min(data_long_low)
            data_long_max = np.max(data_long_high)

            senkou_span_b = (data_long_min + data_long_max) / 2
            logger.debug('senkou_span_b: ' + str(senkou_span_b))

            ichimoku_values['result']['senkou_b']['current'] = senkou_span_b

            # Chikou Span
            chikou_span = data_copy['close'][-1]
            logger.debug('chikou_span: ' + str(chikou_span))

            ichimoku_values['result']['chikou']['current'] = chikou_span

        except Exception as e:
            logger.exception('Exception while calculating Ichimoku cloud.')
            logger.exception(e)

            ichimoku_values['success'] = False

        finally:
            return ichimoku_values


if __name__ == '__main__':
    indicator_calc = IndicatorCalc()

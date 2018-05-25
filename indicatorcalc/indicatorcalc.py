import datetime
import logging
import os
from pprint import pprint
import sys

import numpy as np
from talib.abstract import EMA, RSI, STOCH

#logging.basicConfig()
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)


class IndicatorCalc:
    def __init__(self):
        pass


    def calc_aroon(self, data, period_count):
        aroon_values = {'Exception': False, 'Error': False,
                        'result': {'last': {}, 'current': {}}}

        #data_flipped = IndicatorCalc.flip_data(data)

        try:
            #### DATA PREPARATION ####
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

            elif input_array_high_length < (period_count + 2):
                # ERROR (Not enough data)
                logger.error('Not enough data periods for Aroon calculation.')

                logger.error('Required: ' + str(int(period_count + 2)) + ' / ' +
                             'Given: ' + str(input_array_high_length))

                aroon_values['Error'] = True

            elif input_array_high_length > (period_count + 2):
                trim_length = int(input_array_high_length - (period_count + 2))
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
                    periods_since_max = period_count - high_pos
                    logger.debug('periods_since_max: ' + str(periods_since_max))
                    #periods_since_min = low_pos
                    periods_since_min = period_count - low_pos
                    logger.debug('periods_since_min: ' + str(periods_since_min))

                    #aroon_up = round((((period_count - periods_since_max) / period_count) * 100), 2)
                    aroon_up = round(((periods_since_max / period_count) * 100), 2)
                    logger.debug('aroon_up: ' + str(aroon_up))
                    #aroon_down = round((((period_count - periods_since_min) / period_count) * 100), 2)
                    aroon_down = round(((periods_since_min / period_count) * 100), 2)
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


    def calc_rsi(self, data, period_count, price_input='close'):
        rsi_values = {'Exception': False, 'result': {}}

        try:
            results = RSI(data,
                          timeperiod=period_count,
                          prices=price_input)

            rsi_values['result']['rsi'] = results#[-1]

            #if rsi_values['result']['rsi'] > 50:
            if rsi_values['result']['rsi'][-1] > 50:
                rsi_state = 'positive'

            #elif rsi_values['result']['rsi'] == 50:
            elif rsi_values['result']['rsi'][-1] == 50:
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


    def calc_stochrsi(self, data, period_count):
        try:
            sliced = data[int(-1 * period_count):]

            current = sliced[-1]

            low = np.min(sliced)
            high = np.max(sliced)

            result = (current - low) / (high - low)

            return result

        except Exception:
            logger.exception('Exception while calculating Stochastic RSI.')

            raise


    def calc_ema(self, data, period_count_short, period_count_long, price_input='close'):
        ema_values = {'Exception': False, 'result': {}}

        try:
            ema_inputs = {'short': period_count_short, 'long': period_count_long}

            for ema in ema_inputs:
                period_count = ema_inputs[ema]

                results = EMA(data,
                              timeperiod=period_count,
                              prices=price_input)

                ema_values['result'][ema] = results[-1]

            if ema_values['result']['short'] > ema_values['result']['long']:
                ema_state = 'positive'

            elif ema_values['result']['short'] == ema_values['result']['long']:
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


    def calc_stoch(self, data, price_input='close'):
        stoch_values = {'Exception': False, 'result': {}}

        try:
            fastk_period = 14
            slowk_period = 3
            slowk_matype = 0
            slowd_period = 3
            slowd_matype = 0

            slowk, slowd = STOCH(data,
                                 fastk_period, slowk_period, slowk_matype,
                                 slowd_period, slowd_matype)

            stoch_values['result']['slowk'] = slowk[-1]
            stoch_values['result']['slowd'] = slowd[-1]
            stoch_values['result']['average'] = (slowk[-1] + slowd[-1]) / 2

            if stoch_values['result']['slowk'] > stoch_values['result']['slowd']:
                stoch_state = 'positive'

            elif stoch_values['result']['slowk'] == stoch_values['result']['slowd']:
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


if __name__ == '__main__':
    indicator_calc = IndicatorCalc()

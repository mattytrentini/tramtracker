#!/usr/bin/python
# tramtracker
# -*- coding: latin-1 -*-
# ----------------------------------------------------------------------------
# I, Colin Jacobs, <colin@coljac.net>, the author of this file, release it
# to the public domain for use and modification without restriction. Where
# possible, retaining acknowledgement of original authorship is appreciated.
# ----------------------------------------------------------------------------
# ****************************************************************************
# * Software: tramtracker                                                    *
# * Version:  0.1                                                            *
# * Date:     2014-09-26                                                     *
# * Last update: 2014-09-26                                                  *
# *                                                                          *
# * Author:  Colin Jacobs, colin@coljac.net                                  *
# *                                                                          *
# * A wrapper for Yarra Trams' Tram Tracker data, accessed via               *
# * tramtracker.com.                                                         *
# *                                                                          *
# * If you don't live in Melbourne, Australia, this is probably not the      *
# * module you're looking for.                                               *
# *                                                                          *
# * Usage from command line:                                                 *
# *                                                                          *
# *     tramtracker.py  stopID [route]                                       *
# *                                                                          *
# *     $ python tramtracker.py 3110                                         *
# *     Next trams:                                                          *
# *     72: 1 minutes                                                        *
# *      1: 2 minutes                                                        *
# *      ...                                                                 *
# *                                                                          *
# * Usage from python:                                                       *
# *                                                                          *
# *     >>> import tramtracker                                               *
# *     >>> my_tram = 1                                                      *
# *     >>> my_stop = 3110                                                   *
# *     >>> mins_to_wait = tramtracker.get_next_time(my_stop, my_tram)       *
# *     >>> mins_to_wait                                                     *
# *     4.823830298582712                                                    *
# *     >>> tramtracker.get_next_times(my_stop)                              *
# *     {72: 2.564150317509969, 1: 4.964150631427765, ...}                   *
# ****************************************************************************
import json, ure, time

TT_URL = "http://www.tramtracker.com/Controllers/GetNextPredictionsForStop.ashx"

def _call_tt(stop=1421, route=19):
    import urequests
    page = urequests.get(TT_URL +
                    "?stopNo=%s&routeNo=%s&isLowFloor=false" % (stop, route))
    return page.text

def _get_minutes_from_date_string(time_str):
    time_string = ure.match('.*(' + (r'\d' * 13) + ').*', str(time_str)).group(1)
    seconds_until_tram = int(time_string)/1000. - (time.time() + 946684800)
    print(time_str, time_string, seconds_until_tram)
    return (seconds_until_tram/60)

def get_next_time(stop=1421, route=19):
    """
    :param stop: The id of the tram stop. Can be found in the apps or Yarra
     Trams website.
    :param route: The tram route/line number.
    :return: the time, in minutes, until the next tram at the stop.
    """
    raw_result = _call_tt(stop, route)
    json_obj = json.loads(raw_result)
    next_string = json_obj['responseObject'][0]['PredictedArrivalDateTime']
    return _get_minutes_from_date_string(next_string)

def get_next_times(stop):
    """
    :param stop: The id of the tram stop. Can be found in the apps or Yarra
     Trams website.
    :return: A dict, containing the tram ids as keys and the the time,
    in minutes, until the next tram of that route as the values.

    e.g. {'1': '12.3', '8': '2.5'}
    """
    raw_result = _call_tt(stop, 0)
    json_obj = json.loads(raw_result)['responseObject']
    trams = {}
    for resp in json_obj:
        tram = resp['InternalRouteNo']
        time = _get_minutes_from_date_string(resp['PredictedArrivalDateTime'])
        if tram in trams:
            if trams[tram] > time:
                trams[tram] = time
        else:
            trams[tram] = time
    return trams

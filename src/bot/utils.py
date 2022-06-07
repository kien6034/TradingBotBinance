import time

NUM_OF_CANDLES= 60
def get_start_date(interval):
        ts = int(time.time())
        interval_type = interval[-1]
        interval_value = int(interval[0:-1])
       
        if interval_type == "m":
            value_in_sec = 60
        elif interval_type == "h":
            value_in_sec = 60 * 60
        elif interval_type == "d":
            value_in_sec = 60 * 60 * 24
        elif interval_type == "w":
            value_in_sec = 60 * 60 * 24 * 7
        
        t = interval_value * value_in_sec * NUM_OF_CANDLES
        return ts - t
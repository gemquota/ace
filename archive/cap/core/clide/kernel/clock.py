import time

class LogicalClock:
    def __init__(self, start_time=0):
        self.time = start_time

    def tick(self):
        self.time += 1
        return self.time

    def update(self, received_time):
        self.time = max(self.time, received_time) + 1
        return self.time

# Global clock for the local kernel
_clock = LogicalClock()

def get_next_logical_time():
    return _clock.tick()

def update_clock(received_time):
    return _clock.update(received_time)

def get_real_timestamp():
    return int(time.time())

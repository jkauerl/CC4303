class CongestionControl():

    def __init__(self, mss):
        self.mss = mss
        self.current_state = "slow start"
        self.cwnd = mss # esta valor esta en bytes
        self.ssthresh = None
        self.fraction = 0

    def get_cwnd(self):
        """ retorna el valor de cwnd almacenado en la clase
        """
        return self.cwnd
    
    def get_MSS_in_cwnd(self):
        return self.get_cwnd() // self.mss 
        
    def get_ssthresh(self):
        return self.ssthresh
        
    def is_state_slow_start(self):
        if self.current_state == "slow start":
            return True
        else:
            return False
        
    def is_state_congestion_avoidance(self):
        if self.current_state == "congestion avoidance":
            return True
        else:
            return False
        
    def event_ack_received(self):

        if self.is_state_slow_start():
            self.cwnd += self.mss
            if self.ssthresh != None:
                if self.cwnd >= self.ssthresh:
                    self.current_state = "congestion avoidance"
                    self.ssthresh = self.get_cwnd() / 2
        
        elif self.is_state_congestion_avoidance():
            self.cwnd += 1 // self.get_MSS_in_cwnd() * self.mss
            self.fraction = 1 / self.get_MSS_in_cwnd() * self.mss - 1 // self.get_MSS_in_cwnd() * self.mss
            if (self.fraction // 1).is_integer():
                self.cwnd += self.fraction
                
    def event_timeout(self):

        if self.is_state_slow_start():
            self.ssthresh = self.get_cwnd() / 2
            self.cwnd = self.mss
        elif self.is_state_congestion_avoidance():
            self.current_state = "slow start"
            self.cwnd = self.mss 
            self.ssthresh += (self.get_cwnd() // 2) * self.get_MSS_in_cwnd()

    
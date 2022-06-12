class OrderController:
    def __init__(self) -> None:
        """
            - Status == 0: Not in any order, status == 1: Buying, status == 2: Selling 
        """
        self.status = 0 # not makking any order 

    
    def buy_status(self):
        if self.status == 0:
            self.status == 1 

        
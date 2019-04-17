

class Player:

    def __init__(self, buy_in, name):
        '''
        PARAMETERS:
            buy_in: integer

        RETURN: None
        '''
        self.chips = buy_in
        self.name = name
        self.cards = []

import sys
import json
from time import sleep
import numpy as np
from ColorPrint import COLORS, DARKGRAY, RESET
from misc import deck, value, handTypeLong, resizeWindow, absOpen
from player import Player


class Game:

    def __init__(self, n_players=2, buy_in=100, big_blind=2, player_names=None, hv=None):
        '''
        PARAMETERS:
            n_players: integer

        RETURN: None
        '''
        np.random.seed(123)

        try:
            with open('history.txt', 'r') as f:
                self.text_commands = [line.split()[-1] for line in f.read().splitlines() if 'call' in line]
        except FileNotFoundError:
            pass

        print('Game loading...', end='\r')

        if hv is None:
            with absOpen('hv.json', 'r') as f: self.__hv = json.load(f)
        print(' ' * 80, end='\r')

        self.__bb = big_blind
        self.__n_players = n_players
        self.__n_game = 0
        self.__players = []

        if player_names is None:
            player_names = ['{}Player {}{}'.format(COLORS[i], i, RESET) for i in range(n_players)]

        if isinstance(buy_in, int):
            for i in range(n_players):
                self.__players.append(Player(buy_in, player_names[i]))
        elif isinstance(buy_in, list):
            for i in range(n_players):
                self.__players.append(Player(buy_in[i], player_names[i]))
        else:
            raise TypeError('buy-in can only be (list of) integers')

        self.__newGame()

    def __newGame(self):
        '''
        PARAMETERS: None

        RETURN: None
        '''
        self.__deck = deck
        self.__pot = 0
        self.__players = [p for p in self.__players if p.chips]

        self.__n_players = len(self.__players)
        self.__bets = [0] * self.__n_players
        self.__folds = [p.chips == 0 for p in self.__players]
        for p in self.__players: p.cards = []

        # pre-flop
        cards = self.__draw(self.__n_players * 2)
        for i in range(self.__n_players):
            self.__players[i].cards += cards[i::self.__n_players]
        print('Pre-flop:')
        print('\n'.join('[{}] '.format(self.__players[i].name) +
              ' '.join(self.__players[i].cards) for i in range(self.__n_players)))
        self.__newRound(blind=True)

        # flop
        cards = self.__draw(3)
        for i in range(self.__n_players):
            self.__players[i].cards += cards
        print('Flop:', ' '.join(cards))
        self.__newRound()

        # turn
        cards = self.__draw(1)
        for i in range(self.__n_players):
            self.__players[i].cards += cards
        print('Turn:', cards[0])
        self.__newRound()

        # river
        cards = self.__draw(1)
        for i in range(self.__n_players):
            self.__players[i].cards += cards
        print('River:', cards[0])
        self.__newRound()

        # game over
        self.__finishGame()

    def __finishGame(self):
        print('Results from game {}:'.format(self.__n_game))
        self.__n_game += 1
        if max(len(p.cards) for p in self.__players) > 5:
            hval = [value(p.cards, self.__hv) for p in self.__players]
            nwin = 0
            maxv = 0
            for i, v in enumerate(hval):
                if self.__folds[i]: continue
                if v[0] > maxv:
                    maxv = v[0]
                    nwin = 1
                elif v[0] == maxv:
                    nwin += 1
            for i in range(self.__n_players):
                player = self.__players[i]
                if self.__folds[i]:
                    symbol = ' -'
                elif hval[i][0] == maxv:
                    player.chips += self.__pot // nwin
                    symbol = ' \u2605'
                else:
                    symbol = ''
                print('[{}] Hand: {} ({}). Chips: {}'.format(
                    self.__players[i].name, ' '.join(hval[i][1]), handTypeLong(hval[i][1]),
                    str(player.chips) + symbol
                ))
        else:
            for i in range(self.__n_players):
                player = self.__players[i]
                if not self.__folds[i]: player.chips += self.__pot
                print('[{}] Chips: {}'.format(
                    self.__players[i].name, str(player.chips) + (' -' if self.__folds[i] else ' \u2605')
                ))

        if len([p.chips for p in self.__players if p.chips]) > 1:
            print(DARKGRAY + '#' * 80 + RESET)
            self.__players = np.roll(self.__players, -1).tolist()
            self.__newGame()
        else:
            print(DARKGRAY + '·' * 80 + RESET)
            print('Game over')
            sys.exit()

    def __newRound(self, blind=False):
        '''
        PARAMETERS:
            blind: boolean

        RETURN: None
        '''
        print(DARKGRAY + '·' * 80 + RESET)
        assert not sum(self.__bets), 'bets not initialized.'
        n_round = 0
        all_in = [False] * self.__n_players
        while not (all(all_in) or self.__folds.count(False) == 1):
            for i in range(self.__n_players):
                if self.__folds[i]: continue
                bet = self.__bet(i, n_round, blind)
                self.__bets[i] += bet
                self.__players[i].chips -= bet
            if self.__folds.count(False) == 1:
                print(DARKGRAY + '#' * 80 + RESET)
                self.__pot += sum(self.__bets)
                self.__finishGame()
                return
            n_round += 1
            bets = [b for b, p, f, a in zip(self.__bets, self.__players, self.__folds, all_in)
                    if not (f or not (b or p.chips) or a)]
            all_in = [p.chips == 0 for p in self.__players]  # all-in last round
            if len(set(bets)) < 2: break

        for i in range(self.__n_players):
            self.__pot += self.__bets[i]
            self.__bets[i] = 0
        print(DARKGRAY + '#' * 80 + RESET)

    def __draw(self, n_cards):
        '''
        PARAMETERS:
            stage: sring ('pf', 'f', 't', 'r')

        RETURN: list
        '''
        cards = np.random.choice(self.__deck, n_cards, replace=False).tolist()
        self.__deck = [card for card in self.__deck if card not in cards]
        return cards

    def __input(self, msg):
        '''
        PARAMETERS:
            msg: string

        RETURN: string
        '''
        if hasattr(self, 'text_commands'):
            try:
                command = self.text_commands.pop(0)
                print(msg + command)
                return command
            except IndexError:
                delattr(self, 'text_commands')
        return input(msg)

    def __prompt(self, position, to_call):
        '''
        PARAMETERS:
            position: integer
            to_call: integer

        RETURN: integer
        '''
        chips = self.__players[position].chips
        msg = '[{}] Pot: {}. Chips: {}/{}. Enter: ({} to call): '.format(
                  self.__players[position].name, self.__pot, self.__bets[position], chips,
                  to_call if to_call < chips else 'all-in',
              )
        op_chips = lambda i: self.__players[i].chips * (1 - self.__folds[i]) * (i != position)
        m = max(range(self.__n_players), key=op_chips)
        max_chips = self.__players[m].chips
        chips2ai = self.__bets[m] - self.__bets[position] + max_chips
        while True:
            try:
                bet = int(self.__input(msg))
                if bet == 0:
                    break
                elif chips2ai <= to_call:  # forbid raising
                    if bet < to_call:  # fail to call
                        raise ValueError
                    elif bet == to_call:  # call
                        break
                    else:
                        print('\033[0C\033[1A', end='\r')
                        print(msg + 'no need for raise', end='\r')
                        sleep(.2)
                        print(' ' * 80, end='\r')
                else:  # bet only in [to_call, chips2ai]
                    if bet < to_call:  # fail to call
                        raise ValueError
                    elif to_call <= bet <= chips2ai:  # call or raise
                        break
                    else:
                        print('\033[0C\033[1A', end='\r')
                        print(msg + str(chips2ai), 'to all-in', self.__players[m].name, end='\r')
                        sleep(.2)
                        print(' ' * 80, end='\r')
            except KeyboardInterrupt:
                print('\n' + DARKGRAY + '·' * 80 + RESET)
                print('Good bye')
                sys.exit()
            except ValueError:
                print('\033[0C\033[1A', end='\r')
                print(msg + 'invalid size', end='\r')
                sleep(.2)
                print(' ' * 80, end='\r')
        if bet == 0 and to_call > 0:
            self.__folds[position] = True
        return bet

    def __bet(self, position, n_round, blind):
        '''
        PARAMETERS:
            position: integer (0: sb; 1: bb; etc.)
            n_round: integer
            blind: boolean

        RETURN: integer
        '''
        chips = self.__players[position].chips
        op_chips = [p.chips for i, p in enumerate(self.__players) if
                    (not self.__folds[i]) and (i != position)]
        to_call = max(self.__bets) - self.__bets[position]
        if not chips or not (to_call + sum(op_chips)):
            bet = 0
        elif n_round > 1:  # other rounds
            if to_call > 0:
                bet = self.__prompt(position, to_call)
            else:
                bet = 0
        elif n_round == 1:  # second round
            if (position < 2 and blind) or to_call > 0:
                bet = self.__prompt(position, to_call)
            else:
                bet = 0
        else:  # first round
            if position < 2 and blind:  # sb and bb
                bet = (position + 1) * self.__bb // 2
                if bet >= chips:
                    bet = chips
                print('[{}] Pot: 0. Blind: {}/{}'.format(
                    self.__players[position].name, bet, chips - bet)
                )
            else:  # other players
                bet = self.__prompt(position, to_call)
        return bet


if __name__ == '__main__':
    resizeWindow(80, 60)
    while True:
        try:
            n_players = int(input('Enter number of players: '))
            if not (1 < n_players < 10):
                raise ValueError
            break
        except ValueError:
            print('\033[0C\033[1A', end='\r')
            print('Enter number of players: invalid number', end='\r')
            sleep(.2)
            print(' ' * 80, end='\r')
    resizeWindow(80, 60)
    g = Game(n_players=n_players, buy_in=10)

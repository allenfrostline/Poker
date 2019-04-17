import json
import numpy as np
import PySimpleGUI as sg
from player import Player
from misc import tableFig, drawFigure, deck, value, handTypeLong, absOpen, absPath


class Game:

    def __init__(self, n_players=2, buy_in=100, big_blind=2, hv=None, seed='random'):
        '''
        PARAMETERS:
            n_players: interger (default: 2)
            buy_in: integer (default: 100)
            big_blind: integer (default: 2)
            player_names: list of strings (default: None)
            hv: dictionary (default: None)
            seed: integer (default: 'random')

        RETURN: None
        '''
        if seed != 'random':
            np.random.seed(seed)
        sg.SetOptions(font=('Palatino', 20), border_width=1)
        self.__window = None
        self.__tf = tableFig()

        try:
            with absOpen('history.txt', 'r') as f:
                self.text_commands = [line.split()[-1] for line in f.read().splitlines() if 'call' in line]
        except FileNotFoundError:
            pass

        self.__hv = hv
        self.__big_blind = big_blind
        self.__n_players = n_players
        self.__buy_in = buy_in
        self.__n_game = 1
        self.__players = []
        self.__output = []

        self.__welcome()
        self.__config()
        self.__newGame()

    def __welcome(self):
        # welcome page
        window_title = 'Texas Hold \'em'

        layout = [
            [sg.Text(window_title, justification='center', font=('Palatino', 50), size=(19, 1))],
            [sg.Image(absPath('resources/cover.png'), pad=((70, 0), (0, 10)))],
            [sg.Frame(
                layout=[[sg.Button('Start', bind_return_key=True, size=(15, 1)),
                         sg.Button('Help', size=(15, 1)),
                         sg.Button('Quit', size=(15, 1))]],
                title='',
                border_width=0
            )]
        ]

        window = sg.Window(window_title, icon=absPath('resources/poker.icns'), size=(564, 270), layout=layout, disable_close=True).Finalize()
        self.__current_location = window.CurrentLocation()
        self.__current_size = window.Size

        window.Disable()
        if self.__hv is None:
            with absOpen('hv.json', 'r') as f: self.__hv = json.load(f)
        window.Enable()

        while True:
            event, values = window.Read()
            if event == 'Start':
                self.__current_location = window.CurrentLocation()
                self.__current_size = window.Size
                window.Close()
                break
            elif event == 'Help':
                sg.Window('Help', keep_on_top=True, location=self.__current_location, icon=absPath('resources/poker.icns'), layout=[
                    [sg.Text('All rights reserved Allen Wang @ 2019')],
                    [sg.CButton('OK', size=(35, 1))]
                ]).Read()
            elif event == 'Quit':
                self.__current_location = window.CurrentLocation()
                self.__current_size = window.Size
                window.Close()
                quit()

    def __config(self):
        # config page
        window_title = 'Game Config'

        # initial values
        n_players = self.__n_players
        buy_in = self.__buy_in

        layout = lambda n_players: [
            [sg.Frame(
                layout=[
                    [sg.Text('Game Config', font=('Palatino', 50), justification='center', size=(19, 1))],
                    [sg.Text('Number of player:', size=(16, 1)),
                     sg.Spin(list(range(2, 10)), initial_value=n_players, size=(3, 20), change_submits=True),
                     sg.Text('Buy-in:', size=(17, 1), justification='right'),
                     sg.InputText(str(buy_in), size=(5, 20))]],
                title='',
                border_width=0
            )],
            [sg.Frame(
                layout=[[sg.Text('Name of player {}:'.format(i + 1), size=(16, 1)),
                         sg.InputText('Player {}'.format(i + 1), size=(30, 20))] for i in range(n_players)],
                title='',
                border_width=0
            )],
            [sg.Frame(
                layout=[[sg.Button('Submit', bind_return_key=True, size=(15, 1)),
                         sg.Button('Reset', size=(15, 1)),
                         sg.Button('Quit', size=(15, 1))]],
                title='',
                border_width=0
            )],
        ]

        window = sg.Window(window_title, icon=absPath('resources/poker.icns'), size=(564, 270 + 40 * (n_players - 2)), disable_close=True,
                           location=self.__current_location, layout=layout(n_players)).Finalize()
        while True:
            try:
                event, values = window.Read()
                new_n_players = int(values[0])
                if not (1 < new_n_players < 10):
                    raise ValueError
                if new_n_players != n_players:
                    n_players = new_n_players
                    self.__current_location = window.CurrentLocation()
                    window.Close()
                    window = sg.Window(window_title, icon=absPath('resources/poker.icns'), size=(564, 270 + 40 * (n_players - 2)), disable_close=True,
                                       location=self.__current_location, layout=layout(n_players)).Finalize()
                if event == 'Submit':
                    buy_in = int(values[1])
                    assert len(values) == 2 + n_players
                    player_names = values[-n_players:]
                    assert n_players == len(player_names)
                    self.__current_location = window.CurrentLocation()
                    window.Close()
                    break
                elif event == 'Reset':
                    n_players = self.__n_players
                    self.__current_location = window.CurrentLocation()
                    window.Close()
                    window = sg.Window(window_title, icon=absPath('resources/poker.icns'), size=(564, 270 + 40 * (n_players - 2)), disable_close=True,
                                       location=self.__current_location, layout=layout(n_players)).Finalize()
                elif event == 'Quit':
                    quit()
            except ValueError:
                sg.Window('Error', icon=absPath('resources/poker.icns'), keep_on_top=True, layout=[
                    [sg.Text('Invalid value entry')],
                    [sg.CButton('OK', size=(20, 1))]
                ]).Read()
                self.__current_location = window.CurrentLocation()
                window.Close()
                window = sg.Window(window_title, icon=absPath('resources/poker.icns'), size=(564, 270 + 40 * (n_players - 2)), disable_close=True,
                                   location=self.__current_location, layout=layout(n_players)).Finalize()
            except AssertionError:
                pass
            except TypeError:
                quit()

        self.__n_players = n_players
        self.__buy_in = buy_in
        self.__players = [Player(buy_in, name) for name in player_names]

    def __draw(self, n_cards):
        cards = np.random.choice(self.__deck, n_cards, replace=False).tolist()
        self.__deck = [card for card in self.__deck if card not in cards]
        return cards

    def __newGame(self):
        # start game
        self.__deck = deck
        self.__pot = 0
        self.__players = [p for p in self.__players if p.chips]
        self.__n_players = len(self.__players)
        self.__bets = [0] * self.__n_players
        self.__folds = [p.chips == 0 for p in self.__players]
        self.__community_cards = []
        for p in self.__players: p.cards = []

        # preflop
        cards = self.__draw(self.__n_players * 2)
        for i in range(self.__n_players):
            self.__players[i].cards += cards[i::self.__n_players]
        self.__newRound(blind=True)

        # flop
        cards = self.__draw(3)
        for i in range(self.__n_players):
            self.__players[i].cards += cards
        self.__community_cards += cards
        self.__newRound()

        # turn
        cards = self.__draw(1)
        for i in range(self.__n_players):
            self.__players[i].cards += cards
        self.__community_cards += cards
        self.__newRound()

        # river
        cards = self.__draw(1)
        for i in range(self.__n_players):
            self.__players[i].cards += cards
        self.__community_cards += cards
        self.__newRound()

        # game over
        self.__finishGame()

    def __finishGame(self):
        msg = []
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
                msg.append('[{}] Hand: {} ({}). Chips: {}'.format(
                               self.__players[i].name, ' '.join(hval[i][1]), handTypeLong(hval[i][1]),
                               str(player.chips) + symbol
                           ))
        else:
            for i in range(self.__n_players):
                player = self.__players[i]
                if not self.__folds[i]: player.chips += self.__pot
                msg.append('[{}] Chips: {}'.format(
                                self.__players[i].name, str(player.chips) +
                                (' -' if self.__folds[i] else ' \u2605')
                            ))

        window_title = 'Game {}'.format(self.__n_game)
        self.__window.TKroot.title('Texas Hold \'em - ' + window_title)
        self.__window.FindElement('_TT_').Update(window_title)
        mask = []
        mask = [-1 if self.__folds[i] else 1 for i in range(self.__n_players)]
        fig = self.__tf.plot(self.__players, community_cards=self.__community_cards, mask=mask)
        _ = drawFigure(self.__window.FindElement('_CANVAS_').TKCanvas, fig)
        self.__current_location = self.__window.CurrentLocation()
        self.__current_size = self.__window.Size

        self.__print('Results of game {}:'.format(self.__n_game))
        for m in msg: self.__print(m)

        result_size = (600, 55 + 25 * self.__n_players)
        result_location = [
            c + s // 2 - s_ // 2 for c, s, s_ in
            zip(self.__current_location, self.__current_size, result_size)
        ]

        sg.Window('Results',
            keep_on_top=True, icon=absPath('resources/poker.icns'), disable_close=True,
            size=result_size, location=result_location,
            layout=[
                [sg.Text('\n'.join(msg))],
                [sg.CButton('OK', size=(60, 1), bind_return_key=True)]]
        ).Read()

        if len([p.chips for p in self.__players if p.chips]) > 1:
            self.__n_game += 1
            self.__players = np.roll(self.__players, -1).tolist()
            self.__tf.sb = (self.__tf.sb + 1) % self.__n_players
            self.__newGame()
        else:  # game over for good
            quit()

    def __newRound(self, blind=False):
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

    def __prompt(self, position, to_call):
        msg = 'Bet/Raise ({} to call):'.format(to_call)
        chips = self.__players[position].chips
        op_chips = lambda i: self.__players[i].chips * (1 - self.__folds[i]) * (i != position)
        m = max(range(self.__n_players), key=op_chips)
        max_chips = self.__players[m].chips
        chips2ai = self.__bets[m] - self.__bets[position] + max_chips
        bet = None
        layout = lambda dt: [
            [sg.Text(dt)]
            [sg.Slider((to_call + 1, min(chips2ai, chips)), orientation='h', relief='flat',
                        border_width=0, background_color='#fff', size=(50, 15))],
            [sg.CButton('Ok', size=(50, 1))]
        ] if dt else [
            [sg.Slider((to_call + 1, min(chips2ai, chips)), orientation='h', relief='flat',
                        border_width=0, background_color='#fff', size=(50, 15))],
            [sg.CButton('Ok', size=(50, 1))]
        ]
        dt = ''
        while True:
            try:
                window = sg.Window(title=msg, icon=absPath('resources/poker.icns'), keep_on_top=True, size=(500, 100),
                                   disable_close=True, layout=layout(dt))
                _, values = window.Read()
                bet = values[0]
                bet = int(bet)
                if bet > chips:
                    raise ValueError
                if chips2ai <= to_call:  # forbid raising
                    if bet < to_call:  # fail to call
                        raise ValueError
                    elif bet == to_call:  # call
                        break
                    else:
                        dt = 'No need to raise'
                else:  # bet only in [to_call, chips2ai]
                    if bet < to_call:  # fail to call
                        raise ValueError
                    elif to_call <= bet <= chips2ai:  # call or raise
                        break
                    else:
                        sg.PopupOK('Error!!!!!')
                        quit()
            except ValueError:
                dt = 'You can\'t bet "{}"'.format(bet)
            except TypeError:
                pass
        if bet == 0 and to_call > 0:
            self.__folds[position] = True

        return bet

    # def __print(self, msg):
    #     self.__output.append(msg)
    #     self.__output = self.__output[-5:]
    #     self.__window.FindElement('_OUTPUT_').Update(value='\n'.join(self.__output))

    def __print(self, msg):
        print(msg)

    def __bet(self, position, n_round, blind):
        chips = self.__players[position].chips
        op_chips = [p.chips for i, p in enumerate(self.__players) if
                    (not self.__folds[i]) and (i != position)]
        to_call = max(self.__bets) - self.__bets[position]
        msg = ''

        new_size = (1150, 840)
        self.__current_location = [
            c + s // 2 - s_ // 2 for c, s, s_ in
            zip(self.__current_location, self.__current_size, new_size)
        ]
        window_title = 'Game {}'.format(self.__n_game)
        if not self.__window:
            mask = []
            for i in range(self.__n_players):
                if i == position:
                    m = 1
                elif self.__folds[i]:
                    m = -1
                else:
                    m = 0
                mask.append(m)
            fig = self.__tf.plot(self.__players, community_cards=self.__community_cards, mask=mask)
            figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
            layout = [
                [sg.Text(window_title, justification='center', font=('Palatino', 50), key='_TT_', size=(50, 1))],
                [sg.Canvas(size=(figure_w, figure_h), key='_CANVAS_')],
                # [sg.Text('', background_color='#fff', key='_OUTPUT_', size=(1150, 5))],
                [sg.Output(background_color='#fff', key='_OUTPUT_', size=(1150, 5))],
                [sg.Frame(
                    layout=[
                        [sg.Button('Check', key='_CC_', bind_return_key=True, pad=((230, 10), 20), size=(15, 1)),
                         sg.Button('Bet', key='_BR_', pad=((0, 10), 20), size=(15, 1)),
                         sg.Button('Fold', key='_FOLD_', pad=((0, 10), 20), size=(15, 1)),
                         sg.Button('Quit', pad=((0, 10), 20), size=(15, 1))]],
                    title='',
                    border_width=0,
                )]
            ]
            self.__window = sg.Window(window_title, icon=absPath('resources/poker.icns'), size=new_size, disable_close=True,
                                      location=self.__current_location, layout=layout).Finalize()
        else:
            if to_call > 0:
                cc_text = 'Call'
                br_text = 'Raise'
            else:
                cc_text = 'Check'
                br_text = 'Bet'
            self.__window.TKroot.title('Texas Hold \'em - ' + window_title)
            self.__window.FindElement('_TT_').Update(window_title)
            self.__window.FindElement('_CC_').Update(disabled=False, text=cc_text)
            self.__window.FindElement('_BR_').Update(disabled=False, text=br_text)
            self.__window.FindElement('_FOLD_').Update(disabled=False)
            mask = []
            for i in range(self.__n_players):
                if i == position:
                    m = 1
                elif self.__folds[i]:
                    m = -1
                else:
                    m = 0
                mask.append(m)
            fig = self.__tf.plot(self.__players, community_cards=self.__community_cards, mask=mask)

        window = self.__window
        self.__current_location = window.CurrentLocation()
        self.__current_size = window.Size

        _ = drawFigure(window.FindElement('_CANVAS_').TKCanvas, fig)
        window.Element('_OUTPUT_')._TKOut.output.bind('<Key>', lambda e: 'break')

        if not chips or not (to_call + sum(op_chips)):
            bet = 0
        elif n_round > 1:  # other rounds
            if to_call > 0:

                if to_call >= chips:
                    window.FindElement('_BR_').Update(disabled=True)
                event, values = window.Read()
                if event == '_CC_':
                    bet = min(to_call, chips)
                elif event == '_BR_':
                    bet = self.__prompt(position, to_call)
                elif event == '_FOLD_':
                    self.__folds[position] = True
                    bet = 0
                else:  # quit
                    quit()
            else:
                bet = 0
        elif n_round == 1:  # second round
            if (position < 2 and blind) or to_call > 0:
                if to_call >= chips:
                    window.FindElement('_BR_').Update(disabled=True)
                if to_call == 0:
                    window.FindElement('_FOLD_').Update(disabled=True)
                event, values = window.Read()
                if event == '_CC_':
                    bet = min(to_call, chips)
                elif event == '_BR_':
                    bet = self.__prompt(position, to_call)
                elif event == '_FOLD_':
                    self.__folds[position] = True
                    bet = 0
                else:  # quit
                    quit()
            else:
                bet = 0
        else:  # first round
            if position < 2 and blind:  # sb and bb
                bet = (position + 1) * self.__big_blind // 2
                if bet >= chips:
                    bet = chips
                msg = '[{}] Pot: 0. Chips: {}. Blind: {}'.format(
                    self.__players[position].name, chips, bet
                )
            else:  # other players
                if to_call >= chips:
                    window.FindElement('_BR_').Update(disabled=True)
                if to_call == 0:
                    window.FindElement('_FOLD_').Update(disabled=True)
                event, values = window.Read()
                if event == '_CC_':
                    bet = min(to_call, chips)
                elif event == '_BR_':
                    bet = self.__prompt(position, to_call)
                elif event == '_FOLD_':
                    self.__folds[position] = True
                    bet = 0
                else:  # quit
                    quit()

        if not msg:
            msg = '[{}] Pot: {}. Chips: {}. '.format(self.__players[position].name, self.__pot, chips)
            if bet == chips:
                msg += 'All-in: {}'.format(chips)
            elif bet == to_call == 0:
                msg += 'Checked'
            elif bet == to_call > 0:
                msg += 'Called: {}'.format(to_call)
            elif bet == 0 and to_call > 0:
                msg += 'Folded'
            else:
                msg += 'Bet {}'.format(bet)

        self.__print(msg)

        return bet

if __name__ == '__main__':
    g = Game(n_players=9, buy_in=10, seed='random')

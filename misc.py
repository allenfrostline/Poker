import os
import sys
import numpy as np
from copy import copy
from collections import Counter
from itertools import combinations
import matplotlib
import warnings
warnings.filterwarnings('ignore')
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import matplotlib.backends.tkagg as tkagg
import tkinter as Tk
from PIL import Image
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'serif'
plt.rcParams['figure.dpi'] = 135


ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
suits = ['s', 'h', 'c', 'd']
rank_value = {r: i + 2 for i, r in enumerate(ranks)}
suit_value = {s: i for i, s in enumerate(suits)}
deck = [r + s for r in ranks for s in suits]

pf_compact = [
    'AA ', 'KK ', 'QQ ', 'AKs', 'JJ ', 'AQs', 'KQs', 'AJs', 'KJs', 'TT ', 'AKo', 'ATs', 'QJs',
    'KTs', 'QTs', 'JTs', '99 ', 'AQo', 'A9s', 'KQo', '88 ', 'K9s', 'T9s', 'A8s', 'Q9s', 'J9s',
    'AJo', 'A5s', '77 ', 'A7s', 'KJo', 'A4s', 'A3s', 'A6s', 'QJo', '66 ', 'K8s', 'T8s', 'A2s',
    '98s', 'J8s', 'ATo', 'Q8s', 'K7s', 'KTo', '55 ', 'JTo', '87s', 'QTo', '44 ', '22 ', '33 ',
    'K6s', '97s', 'K5s', '76s', 'T7s', 'K4s', 'K2s', 'K3s', 'Q7s', '86s', '65s', 'J7s', '54s',
    'Q6s', '75s', '96s', 'Q5s', '64s', 'Q4s', 'Q3s', 'T9o', 'T6s', 'Q2s', 'A9o', '53s', '85s',
    'J6s', 'J9o', 'K9o', 'J5s', 'Q9o', '43s', '74s', 'J4s', 'J3s', '95s', 'J2s', '63s', 'A8o',
    '52s', 'T5s', '84s', 'T4s', 'T3s', '42s', 'T2s', '98o', 'T8o', 'A5o', 'A7o', '73s', 'A4o',
    '32s', '94s', '93s', 'J8o', 'A3o', '62s', '92s', 'K8o', 'A6o', '87o', 'Q8o', '83s', 'A2o',
    '82s', '97o', '72s', '76o', 'K7o', '65o', 'T7o', 'K6o', '86o', '54o', 'K5o', 'J7o', '75o',
    'Q7o', 'K4o', 'K3o', '96o', 'K2o', '64o', 'Q6o', '53o', '85o', 'T6o', 'Q5o', '43o', 'Q4o',
    'Q3o', '74o', 'Q2o', 'J6o', '63o', 'J5o', '95o', '52o', 'J4o', 'J3o', '42o', 'J2o', '84o',
    'T5o', 'T4o', '32o', 'T3o', '73o', 'T2o', '62o', '94o', '93o', '92o', '83o', '82o', '72o'
]

suit_combinations = list(combinations(suits, 2))
pf_full = []
for hand in pf_compact:
    if hand[2] == 's':
        pf_full += [(hand[0] + s, hand[1] + s) for s in suits]
    elif hand[2] == 'o':
        pf_full += [(hand[0] + sc[0], hand[1] + sc[1]) for sc in suit_combinations]
        pf_full += [(hand[0] + sc[1], hand[1] + sc[0]) for sc in suit_combinations]
    else:
        pf_full += [(hand[0] + sc[0], hand[1] + sc[1]) for sc in suit_combinations]

hand_count = {
    # here royal flush does not count separately
    # s: straight; f: flush; h: full house;
    # 1,2,3,4: duplicates; 22: two pairs
    'sf': 40,        # 4 * 10
    '4': 624,        # 13 * 12 * 4
    'h': 3744,       # 13 * C(4,3) * 12 * C(4,2)
    'f': 5108,       # C(4,1) * C(13,5) - 40
    's': 10200,      # 10 * 4^5 - 40
    '3': 54912,      # 13 * C(4,3) * C(12,2) * 4^2
    '22': 123552,    # C(13,2) * C(4,2) * 11 * 4
    '2': 1098240,    # 13 * C(4,2) * C(12,3) * 4^2
    '1': 1302540,    # (C(13,5) - 10) * (4^5 - 4)
}

straight_ranks = [
    [14, 5, 4, 3, 2],
    [6, 5, 4, 3, 2],
    [7, 6, 5, 4, 3],
    [8, 7, 6, 5, 4],
    [9, 8, 7, 6, 5],
    [10, 9, 8, 7, 6],
    [11, 10, 9, 8, 7],
    [12, 11, 10, 9, 8],
    [13, 12, 11, 10, 9],
    [14, 13, 12, 11, 10],
]


def ranks(hand):
    '''
    PARAMETERS:
        hand: list of 5 strings e.g. ['As', 'Ac', '2c', '3d', 'Th']

    RETURN: list of integers (sorted)
    '''
    return sorted([rank_value[c[0]] for c in hand], reverse=True)


def suits(hand):
    '''
    PARAMETERS:
        hand: list of 5 strings e.g. ['As', 'Ac', '2c', '3d', 'Th']

    RETURN: list of strings (sorted)
    '''
    return sorted([c[1] for c in hand])


def handType(hand):
    '''
    PARAMETERS:
        hand: list of 5 strings e.g. ['As', 'Ac', '2c', '3d', 'Th']

    RETURN: string
    '''
    rks = ranks(hand)
    sts = suits(hand)
    type_4 = type_h = type_f = type_s = type_3 = type_22 = type_2 = False
    counter_values = list(Counter(rks).values())
    count = {n: (n in counter_values) for n in [2, 3, 4]}

    type_4 = count[4]
    type_h = count[3] and count[2]
    type_f = (len(list(set(sts))) == 1)
    type_s = (rks in straight_ranks)
    type_3 = count[3] and not count[2]
    type_22 = (counter_values.count(2) == 2)
    type_2 = count[2] and not count[3]

    if type_f and type_s: return 'sf'
    elif type_4: return '4'
    elif type_h: return 'h'
    elif type_f: return 'f'
    elif type_s: return 's'
    elif type_3: return '3'
    elif type_22: return '22'
    elif type_2: return '2'
    else: return '1'


def handTypeLong(hand):
    '''
    PARAMETERS:
        hand: list of 5 strings e.g. ['As', 'Ac', '2c', '3d', 'Th']

    RETURN: string
    '''
    ht = handType(hand)
    if ht == 'sf':
        return 'straight flush'
    elif ht == '4':
        return 'four of a kind'
    elif ht == 'h':
        return 'full house'
    elif ht == 's':
        return 'straight'
    elif ht == '3':
        return 'three of a kind'
    elif ht == '22':
        return 'two pairs'
    elif ht == '2':
        return 'one pair'
    else:
        return 'high card'


def handValue(hand):
    '''
    PARAMETERS:
        hand: list of 5 strings e.g. ['As', 'Ac', '2c', '3d', 'Th']

    RETURN: float
    '''
    hand_type = handType(hand)
    rks = [r / 1.5 for r in ranks(hand)]  # normalize ranks to (0, 10)
    counter = Counter(rks)
    rank_of_count = {n: sorted(list(set([r for r in counter if counter[r] == n])),
                     reverse=True) for n in [1, 2, 3, 4]}
    if hand_type == 'sf':
        top = rks[1] if ranks(hand) == [14, 5, 4, 3, 2] else rks[0]
        return top * 1 + 9e5
    elif hand_type == '4':
        return rank_of_count[4][0] * 10 + rank_of_count[1][0] * 1 + 8e5
    elif hand_type == 'h':
        return rank_of_count[3][0] * 10 + rank_of_count[2][0] * 1 + 7e5
    elif hand_type == 'f':
        return sum(rks[i] * 10**(4 - i) for i in range(5)) + 6e5
    elif hand_type == 's':
        top = rks[1] if ranks(hand) == [14, 5, 4, 3, 2] else rks[0]
        return top * 1 + 5e5
    elif hand_type == '3':
        return rank_of_count[3][0] * 1 + rank_of_count[1][0] * 10 + \
               rank_of_count[1][1] * 1 + 4e5
    elif hand_type == '22':
        return rank_of_count[2][0] * 100 + rank_of_count[2][1] * 10 + \
               rank_of_count[1][0] * 1 + 3e5
    elif hand_type == '2':
        return rank_of_count[2][0] * 1000 + rank_of_count[1][2] * 100 + \
               rank_of_count[1][1] * 10 + rank_of_count[1][0] * 1 + 2e5
    else:
        return sum(rks[i] * 10**(4 - i) for i in range(5))


def cardValue(card):
    '''
    PARAMETERS:
        card: string of 2 characters e.g. 'As'

    RETURN: integer
    '''
    return rank_value[card[0]] * 10 + suit_value[card[1]]

def hand2str(hand):
    '''
    PARAMETERS:
        hand: list of 5 strings

    RETURN: string
    '''
    return ''.join(sorted(hand, key=cardValue))

def str2hand(s):
    '''
    PARAMETERS:
        s: 10-char string

    RETURN: list of 5 strings
    '''
    return [s[i:i + 2] for i in range(0, len(s), 2)]

def value(full_hand, hv):
    '''
    PARAMETERS:
        full_hand: list of 7 strings

    RETURN: integer, list of 5 strings
    '''
    possible_hands = [hand2str(hand) for hand in combinations(full_hand, 5)]
    best_hand_str = max(possible_hands, key=hv.get)
    best_hand = str2hand(best_hand_str)
    return hv[best_hand_str], best_hand


def handEval(my_pocket, community, n_players, hv,
             n_tot=1024, ranges=None, verbose=False):
    '''
    PARAMETERS:
        my_pocket: list of 2 strings
        community: list of 3-5 strings
        n_players: integer
        hv: hand_value dictionary
        n_tot: integer
        ranges: list of (n_players - 1) floats (default: None)
        verbose: boolean

    RETURN: (float, float)
    '''
    assert len(set(my_pocket + community)) == len(my_pocket + community) and \
           all(card in deck for card in my_pocket + community), 'invalid cards'
    assert 1 < n_players < 10, 'invalid number'
    n_unshown = 5 - len(community)
    np.random.seed(123)
    if ranges is None: ranges = [1] * (n_players - 1)
    simulation = []
    for j in range(n_tot):
        available = [c for c in deck if (c not in my_pocket + community)]
        sim = np.random.choice(available, n_unshown, replace=False).tolist()
        available = [c for c in available if c not in sim]
        for i in range(n_players - 1):
            pf_range = [pf for k, pf in enumerate(pf_full) if
                        pf[0] in available and pf[1] in available and
                        k < len(pf_full) * ranges[i]]
            idx = np.random.choice(range(len(pf_range)))
            cards = pf_range[idx]
            sim += cards
            available = [c for c in available if c not in cards]
        simulation.append(sim)
        if verbose:
            print('{}/{} ({:.2%})'.format(j + 1, n_tot, (j + 1) / n_tot), end='\r')
    n_win = n_tie = 0
    if not n_tot: n_tot = len(simulation)
    for i, cards in enumerate(simulation):
        cards = list(cards)
        new_community = cards[:n_unshown]
        my_full_hand = my_pocket + community + new_community
        op_full_hands = []
        for j in range(n_players - 1):
            op_pocket = cards[n_unshown + j * 2:n_unshown + j * 2 + 2]
            op_full_hands.append(op_pocket + community + new_community)
        my_value = value(my_full_hand, hv)[0]
        op_values = [value(op_full_hand, hv)[0] for op_full_hand in op_full_hands]
        op_value = max(op_values)
        # print(value(my_full_hand, hv)[1])
        # for op_full_hand in op_full_hands:
        #     print(value(op_full_hand, hv)[1])
        # print()
        n_win += (my_value > op_value)
        n_tie += (my_value == op_value)
    if verbose: print(' ' * 50, end='\r')
    return n_win / n_tot, n_tie / n_tot

def absPath(relative_path):
    '''
    PARAMETERS:
        relative_path: string

    RETURN: string
    '''
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def resizeWindow(ncol, nrow):
    '''
    PARAMETERS:
        ncol: integer
        nrow: integer

    RETURN: None
    '''
    os.system('printf "\\e[8;{};{};t" && clear && printf "\\e[3J"'.format(nrow, ncol))

def overlay(fg, bg, x=0, y=0, angle=0):
    '''
    PARAMETERS:
        fg: pillow image object (default: 0)
        bg: pillow image object (default: 0)
        x: integer (default: 0)
        y: integer
        angle: integer

    RETURN: pillow image object
    '''
    fg = fg.rotate(angle, resample=Image.BICUBIC, expand=True)
    bg.paste(fg, (x, y), fg)
    return bg

def absOpen(name, mode):
    return open(absPath(name), mode=mode, buffering=1)

class tableFig:

    def __init__(self):
        self.sb = 0
        path = 'resources/'
        absOpenImage = lambda fn: Image.open(absOpen(path + fn, 'rb'))
        self.table = absOpenImage('table.png')
        card_back = absOpenImage('card_back.png')
        card_back_fold = absOpenImage('card_back_fold.png')
        card2img = {c: absOpenImage('deck/' + c + '.png') for c in deck}
        card2img['b'] = card_back
        card2img['f'] = card_back_fold
        self.card2img = card2img

    def plot(self, players, mask, community_cards):
        '''
        PARAMETERS:
            players: Player object
            mask: list of integers in [-1, 0, 1]
            community_cards: list of strings (default: [])

        RETURN: matplotlib figure object
        '''
        assert len(players) == len(mask)
        table = copy(self.table)
        # circular shift `sb` steps
        players = np.roll(players, self.sb)
        mask = np.roll(mask, self.sb)

        n_players = len(players)
        player_names = [p.name for p in players]
        pocket_cards = []
        for i in range(n_players):
            if mask[i] == -1:
                pocket = ('f', 'f')
            elif mask[i] == 0:
                pocket = ('b', 'b')
            else:
                pocket = players[i].cards[:2]
            pocket_cards.append(pocket)

        if n_players == 2:
            positions = [0, 4]
        elif n_players == 3:
            positions = [0, 2, 4]
        elif n_players == 4:
            positions = [0, 2, 4, 6]
        elif n_players == 5:
            positions = [0, 2, 4, 6, 8]
        elif n_players == 6:
            positions = [0, 2, 3, 4, 6, 8]
        elif n_players == 7:
            positions = [0, 2, 3, 4, 5, 6, 8]
        elif n_players == 8:
            positions = [0, 2, 3, 4, 5, 6, 7, 8]
        elif n_players == 9:
            positions = [0, 1, 2, 3, 4, 5, 6, 7, 8]

        positions = np.roll(positions, -self.sb)

        if 0 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 615, 35, 170)
            table = overlay(self.card2img[p[1]], table, 590, 30, 160)
        if 1 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 435, 30, 0)
            table = overlay(self.card2img[p[1]], table, 410, 35, 10)
        if 2 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 245, 35, 30)
            table = overlay(self.card2img[p[1]], table, 220, 30, 20)
        if 3 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 70, 30, 50)
            table = overlay(self.card2img[p[1]], table, 60, 35, 40)
        if 4 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 50, 195, 90)
            table = overlay(self.card2img[p[1]], table, 55, 210, 100)
        if 5 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 180, 285, 20)
            table = overlay(self.card2img[p[1]], table, 185, 280, 0)
        if 6 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 375, 270, 20)
            table = overlay(self.card2img[p[1]], table, 360, 280, 10)
        if 7 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 555, 270, 10)
            table = overlay(self.card2img[p[1]], table, 545, 280, 0)
        if 8 in positions:
            p = pocket_cards.pop(0)
            table = overlay(self.card2img[p[0]], table, 660, 185, 90)
            table = overlay(self.card2img[p[1]], table, 660, 165, 80)
        for i, c in enumerate(community_cards):
            table = overlay(self.card2img[c], table, 520 - 70 * i, 170)

        fig = plt.figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 800)
        ax.set_ylim(0, 412)
        ax.axis('off')
        ax.imshow(np.fliplr(table))

        btn = positions[-1] if n_players > 2 else 0
        pos_text = [
            (165, -30), (355, -30), (525, -30),
            (780, 10), (830, 255), (595, 435),
            (405, 435), (220, 435), (-30, 230)
        ]
        pos_btn = [
            (150, 12), (340, 12), (530, 12),
            (748, 25), (785, 225), (580, 398),
            (400, 398), (220, 398), (15, 210)
        ]
        rot = [0, 0, 0, 40, 90, 0, 0, 0, -90]

        for i in range(9):
            if i in positions:
                if i == btn:
                    circle = plt.Circle((pos_btn[i][0], pos_btn[i][1]), 10, color='r')
                    ax.add_patch(circle)
                    ax.text(pos_btn[i][0] + 1, pos_btn[i][1] - 5, 'D', ha='center', color='w')
                ax.text(pos_text[i][0], pos_text[i][1], player_names.pop(0), ha='center', rotation=rot[i])

        return fig


def drawFigure(canvas, figure, loc=(0, 0)):
    '''
    PARAMETERS:
        canvas: tkinter.Canvas object
        figure: matplotlib figure object
        loc: 2-tuple (default: (0, 0))

    RETURN: tkagg image object
    '''
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    photo = Tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)
    canvas.create_image(loc[0] + figure_w / 2, loc[1] + figure_h / 2, image=photo)
    tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    return photo

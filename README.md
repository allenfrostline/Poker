<img src="/resources/icon.png" height=100>

# Poker

This is a simple Texas Hold 'em game running on Mac OS. All scripts are written in pure Python. The main GUI is written using the Python module `PySimpleGUI`, and hand evaluation is done by refering to a hand value table pre-calculated together with Monte Carlo simulation. See [here](https://allenfrostline.com/2019/04/09/texas-holdem-series-4/) for detailed explanation of hand evaluation. Together with the GUI version, I also include here a primitive commmandline version with `ColorPrint` support, which you may download and include from this [repo](https://github.com/allenfrostline/Python-Color-Print). The two versions are supposed to work identicallydd.

### Usage

You don't need any Python or module dependencies installed on your Mac in order to just play the game. The app itself is standalone with everything packed inside it already. There're just two steps:

1. Download the app from [here](https://drive.google.com/file/d/1vpxAMru_WIOT3-9VLIs6PxqR5couAUEj/view?usp=sharing).
2. Double click it.

Or rather, if you'd like to pack it yourself:

<div style="text-align:center"><img src="/resources/screenshot.png" width=80%></img></div>

1. Download this [repo](https://github.com/allenfrostline/Poker).
2. Pack it using `PyInstaller` in `--onefile` mode.
3. Double click the app you just generated.

### To-Do's

There're several things to work on in plan:

- Fix bugs (please, don't again).
- Write up AI agents of different strategies (in progress):
    - Expected hand value optimization (Greedy);
    - Game theory optimal (GTO);
    - Evolutionary algorithm (EA);
    - Deep Q-Learning (DQN).

- Build a server-based version so multiple people can play on different divices.
- Build an Android version (proposed by author of `PySimpleGUI`, [MikeTheWatchGuy](https://github.com/MikeTheWatchGuy)).
- Fix GUI problems:
    - Resolution of image is **extremely** low and it looks ugly on Retina screens.
    - Button styles and other design-related issues.

### Known Bugs

Here are some bugs I'm trying to fix:

- Side pot. It's tricky and I havn't found a way to implement it simple.
- Freeze at start. The app starts and then freezes for a sec. This is because Python is openning the hand value table. Perhaps I should try threading for this particular task (no need for the rest of the game). I'll also try to compress the table in a better way (like functionize it).

### Acknowledgement

I appreciate suggestions and encourage from anyone throughout the development (which may still continue for a long time, considering the considerable time I spent just on writing this primitive game). Special thanks to my friends who ever tried to play the game and found bugs starting from the commmandline version. Also, credit for MikeTheWatchGuy who wrote the `PySimpleGUI` module and helped me fix several bugs. Also, credit to [Freepik](https://www.freepik.com) from [www.flaticon.com](www.flaticon.com), who made this fantastic icon. Finally, I wanna give credit to myself for the nights I stayed up after lectures. There is nothing more fulfilling than realizing an impulse right away.

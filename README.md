<p align="center"><img width="500" height="500" src="https://github.com/nottnottloop/SnakesLaddersAndNukes/blob/main/screenshots/title.png"></p>

# Snakes Ladders And Nukes
A server-client game of Snakes and Ladders with the distinction that there are also nuclear weapons. Pick up the biggest atomic bombs around as you move around the board and constantly nuke your opponents (or usually when they're 6 or less squares away from winning) to achieve victory. 

The game progressively gets more dystopic and scary as more nukes are used, because in nuclear war, there are no winners ヾ(≧▽≦*)o

### Playing the game
1. Run `pip install -r requirements.txt`
1. Copy `serverconfigs/gameconfig.ini` to the root directory
1. Change `host` to the correct IP address
1. Run the client: `python3 -m src.client.client` or `py -m src.client.client` on Windows

You can alternatively use R to roll and N to nuke. You can use Shift+Q to exit a game.

### Hosting the server
If for any ~~god-forsaken~~ reason you want to run the server, run `python3 -m src.server.server` after copying and modifying `serverconfig.ini` in the root directory.

### Credits
The awesome sprites were by yaotu, you can find them [here](https://yaotu.itch.io/snakes-and-ladders-board-game-assets) (thanks!). Comes packed with sound effects and music that is totally original and I made myself yes. (music: Papers Please theme and But Nobody Came from Undertale, sound effects MW2 nuke sounds)

### Game history
This was my first ever 'real' python project. It was originally coded in about a week or so in March 2021. The original code can be found in the `legacy` branch. It was incredibly messy with basically no encapsulation of game logic, functions that are over 5 times longer than they need to be, redundant variables, bad variable names, multiple calls to the draw function for good luck, game logic in the draw functions etc. The game would sometimes crash when someone won, and good luck knowing why!

In March 2026 I picked the game back up and rewrote the code entirely to follow something resembling good practices. The client animations were removed (maybe will add them back), but added some new fun features in the lobby.

If you want to enable debug mode in a lobby, click the 'Lobby' text in the top left of the player select screen. Then use arrow keys to move around or press K and L for fun

<img align="right" width="380" height="380" src="https://github.com/nottnottloop/SnakesLaddersAndNukes/blob/main/screenshots/reallyworse.png">

<img align="left" width="380" height="380" src="https://github.com/nottnottloop/SnakesLaddersAndNukes/blob/main/screenshots/slightlyworse.png">

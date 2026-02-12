<p align="center"><img width="500" height="500" src="https://github.com/coding-with-nottnott/SnakesLaddersAndNukes/blob/main/screenshots/title.png"></p>

# Snakes Ladders And Nukes
A server-client game of Snakes and Ladders with the distinction that there are also nuclear weapons. Pick up the biggest atomic bombs around as you move around the board and constantly nuke your opponents (or usually when they're 6 or less squares away from winning) to achieve victory. 

The game progressively gets more dystopic and scary as more nukes are used, because in nuclear war, there are no winners ヾ(≧▽≦*)o

Before playing, copy the `gameconfig.ini` from the `serverconfigs` directory to the root directory, and change the config IP address accordingly (IPV6). 

After that to play run client.py using python3 from command line `python3 client.py` or `py client.py` on Windows

Windows will think client.exe is a trojan, there's not much that can be done because of how 'compiling' python files to exe files works. If you're scared just use the second method with python3, install python from the website and make sure adding python to the PATH variable is checked when you install it. 

If for any god-forsaken reason you want to run the server, just `python3 .\server.py`. Make sure the IP and ports are set correctly in either case (client or server) for what you want to connect to. If you want to run a LAN game set the IP in both serverconfig.ini and gameconfig.ini to your IPv4 address listed in Windows' ipconfig tool from command line.

The awesome sprites were by yaotu, you can find them [here](https://yaotu.itch.io/snakes-and-ladders-board-game-assets) (thanks!). Comes packed with sound effects and music that is totally original and I made myself yes. (music: Papers Please theme and But Nobody Came from Undertale, sound effects MW2 nuke sounds)

<img align="right" width="380" height="380" src="https://github.com/coding-with-nottnott/SnakesLaddersAndNukes/blob/main/screenshots/reallyworse.png">

<img align="left" width="380" height="380" src="https://github.com/coding-with-nottnott/SnakesLaddersAndNukes/blob/main/screenshots/slightlyworse.png">

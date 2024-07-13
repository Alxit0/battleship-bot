# Battlefield Bot

This project contains a fully automatic bot to play the game [Battlefield](http://en.battleship-game.org/). The bot uses a combination of web automation and strategic algorithms to play the game, aiming to maximize the win rate by prioritizing larger ships and using probabilistic calculations for the next move.

## Features

- Automates playing the Battlefield game using a web browser.
- Implements strategies to prioritize finding and destroying larger ships.
- Uses probability maps to determine the best next move.
- Can start and play multiple games automatically.

## Prerequisites

- Python 3.6+
- Firefox WebDriver (GeckoDriver)
- Required Python libraries: `selenium`, `numpy`, `pynput`

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/battlefield-bot.git
    cd battlefield-bot
    ```

2. **Install the required Python libraries:**

    ```bash
    pip install selenium numpy pynput
    ```

3. **Download and set up GeckoDriver:**

    Download the GeckoDriver from the [official site](https://github.com/mozilla/geckodriver/releases) and place it in your desired directory.

4. **Update the `FIREFOX_DRIVER` path:**

    In the `bot.py` file, update the `FIREFOX_DRIVER` variable with the path to your GeckoDriver executable.

    ```python
    FIREFOX_DRIVER = "path/to/your/geckodriver"
    ```

## Usage

### Start a New Game

To start a new game, simply run the `bot.py` script without any arguments:

```bash
python bot.py
```

### Join a Friend's Game

To join a friend's game, provide the match URL as an argument:

```
python bot.py "http://en.battleship-game.org/your-match-url"
```

## How It Works

1. **Initialization**:

    - The bot initializes the Firefox browser with a custom user agent and navigates to the Battlefield game website.

2. **Game Loop**:

    - The bot enters a loop to play multiple games. For each game, it:

    - Randomizes the ship layout.

    - Starts the game.

    - Continuously waits for its turn and makes moves based on the probability map.

    - Ends the game when all ships are destroyed or the opponent's ships are destroyed.

    - Optionally pauses between games if the user requests.

3. **Move Calculation**:

    - The bot calculates the probability of each cell containing a ship based on the current map and active ships.

    - It prioritizes moves that are more likely to hit larger ships.

    - The bot uses a checkerboard pattern to optimize the search for ships.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

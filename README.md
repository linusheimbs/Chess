# Chess

## Table of Contents
- [About the Game](#about-the-game)
- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Future Improvements](#future-improvements)

## About the Game
Everyone knows chess, and this is my attempt at creating an engine for it.

## Features
- Implements the standard chess rules.
- Supports player-vs-player games locally.
- Legal move generation and validation.

## Installation
To play the game, you’ll need to have Python and pygame installed on your system.

1. Clone the repository:
    ```bash
    git clone https://github.com/linusheimbs/Chess.git
    cd Chess
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the game:
    ```bash
    python main.py
    ```

## How to Play
- **Objective**: The goal of the game is to checkmate your opponent’s king.
- **Movement**: Use the mouse to select a piece and move it according to chess rules:
  - Click on a piece to select it.
  - Valid moves will be highlighted (if implemented).
  - Click on a destination square to move the piece.
  - Deselect a piece by right-clicking or selecting another piece.
  
- **Basic Controls**:
  - **Left-click**: Select a piece and move it.
  - **Right-click**: Deselect a piece.
  
- The game follows standard chess rules, including check, checkmate, and castling.

## Future Improvements
Here are some features and improvements planned for future versions:
- Add AI to play against the computer.
- Implement move history and an undo option.
- Enhanced visuals.
- Add audio.
- More sophisticated move validation (e.g., handling stalemates, en passant, etc.).

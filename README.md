# Auto-Reroller

Auto-Reroller is an automated GUI tool built in Python using `tkinter` specifically designed to automate the character creation stat rerolling process for **Baldur's Gate 1 & 2 Enhanced Edition**. While it might work on other games with a similar character creation system, it is tailor-made for BG1 and BG2 EE.

It uses computer vision (OCR via `pytesseract`) to scan the screen for total roll values, stores the best rolls, and it will automatically stop if the max (e.g., 108) is reached.

## Features

- **Automated Rerolling**: Automates the repetitive task of clicking 'Reroll'.
- **Smart Storing**: Uses OCR to detect the current roll value and automatically stores the roll if it beats your current maximum roll.
- **Dynamic Speed Adjustment**: Adjust the reroll delay speed using the UI or on-the-fly with `+` and `-` hotkeys.
- **Debug Mode**: Toggle the "Debug" checkbox to see the OCR capture region and ensure it is positioned correctly.
- **Hotkeys**: Press `x` to stop the rerolling process at any time.

## Prerequisites

- **Tesseract OCR**: You must have Tesseract OCR installed on your Windows system.
  - By default, the script looks for Tesseract at `C:\OCR\Tesseract-OCR`.
  - If installed elsewhere, you will need to update the path in `main.py` (`os.environ["PATH"] += ...`).
- **Python 3.8+**
- **uv**: It is recommended to use `uv` for blazing fast virtual environment management and package installation.

## Installation

1. Clone or download this repository.
2. Create a virtual environment using `uv`:
   ```bash
   uv venv
   ```
3. Activate the virtual environment:
   ```bash
   # On Windows
   .venv\Scripts\activate
   ```
4. Install the required dependencies using `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```bash
   python main.py
   ```
2. **Setup Phase**: Click **Start Setup** and follow the on-screen instructions:
   - Click the **Recall** button in-game.
   - Click the **Store** button in-game.
   - Click the **CENTER** of the total roll number (where the OCR will read the number).
   - Click the **Reroll** button in-game.
3. **Start Rerolling**: Once setup is complete, click **Start Rerolling**.
4. The script will continuously reroll until you press the `x` key or the max roll reaches `108`.

## Adjusting Speed

- While running, you can press `+` to decrease the delay (faster rerolls) or `-` to increase the delay (slower rerolls).

## Dependencies

- `pyautogui`: Used for screen capture and automating mouse clicks.
- `pytesseract`: Used for Optical Character Recognition (OCR) to read the roll values.
- `keyboard`: Used to detect global key presses (e.g., stopping the script, adjusting speed).
- `pynput`: Used for tracking mouse clicks during the setup phase.
- `Pillow`: Used for image manipulation and displaying debug images in the UI.

# Lecture-Scheduler

## Description
This project is a university course scheduler that crawls and reads all available lectures, allowing users to add desired courses to a list. Unlike other services, this program not only includes mandatory courses but also suggests additional courses that would be beneficial to take if the schedule allows.

## System Requirements
- **OS**: Windows
- **Python**: 3.11.4
- **Required Modules**:
  - PyQt5 5.15.9
  - pyqt5-plugins 5.15.9.2.3
  - PyQt5-Qt5 5.15.2
  - PyQt5-sip 12.13.0
  - pyqt5-tools 5.15.9.3.3
  - Install all modules using: `pip install pyqt5`

## Installation
1. Download the project files.
2. Install the required dependencies listed above.

## Usage
### Running the Program
1. Run `main.py`:
    ```sh
    python main.py
    ```
2. If `main.py` fails to run, try executing `main.exe`:
    ```sh
    ./main.exe
    ```
    - Note: [main.exe](http://_vscodecontentref_/1) should be in the same directory as [Data](http://_vscodecontentref_/2), [plugins](http://_vscodecontentref_/3), and `.ui` files.

### Notes
- The program works best on a 1920x1080 resolution.
- The file might not work well if Python is installed in a path containing Korean characters (due to an issue with PyQt).

## Features
- **Mandatory Courses**: Add courses that must be taken.
- **Preferred Courses**: Add courses that are beneficial to take if the schedule allows.
- **Schedule Calculation**: Calculates all possible schedules based on the provided courses.

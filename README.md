# Obstacle Course Level Editor

## Overview
The Obstacle Course Level Editor is a PyQt5-based application that lets you design and edit obstacle courses. It provides an intuitive graphical interface where you can create new courses, add and manage levels, and place gates with specific properties such as position, rotation, type, and difficulty.

## Features
- **Interactive UI:** Drag and drop gates on a grid with real-time updates.
- **Gate Management:** Add, remove, reorder, rotate, change gate type, and adjust gate difficulty.
- **Level Management:** Create new levels, import/export courses as JSON, and delete existing levels.
- **Linked List Structure:** Gates are managed using a custom linked list for efficient ordering.
- **Customizable Display:** Easily adjust grid dimensions and visualize gate connections with dynamic arrows.

## Screenshots / GIFs
<!-- Replace the paths below with your own images or GIFs -->
![Screenshot 1](/screenshot1.png)


## Installation

### Prerequisites
- Python 3.x
- [PyQt5](https://pypi.org/project/PyQt5/)
- [NumPy](https://pypi.org/project/numpy/)

### Steps
1. **Clone the repository:**

    git clone git@github.com:nick1702/ObstacleCourse.git

2. **Change to the Project Directory:**

    ```bash
    cd obstacle-course-level-editor

3. **Install Dependencies:***

    ```bash
    pip install PyQt5 numpy

### Usage

To start the editor, run:

    python obstacle_course_tool.py
    

This will launch the graphical interface where you can create a new course, add levels, and design your obstacle course by placing and editing gates.

## Opening the Doxygen HTML Documentation

After running Doxygen, the HTML documentation is generated in the `html` folder.

1. Navigate to the `html` folder in your project directory.
2. Open the `index.html` file in your preferred web browser (e.g., by double-clicking the file).



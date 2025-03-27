import sys
from PyQt5.QtWidgets import QGraphicsEllipseItem, QFileDialog, QGraphicsPathItem, QGraphicsItemGroup, QAbstractItemView, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QSplitter, QApplication, QMainWindow, QGraphicsLineItem, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QVBoxLayout, QWidget, QGraphicsItem, QGraphicsTextItem, QMenuBar, QAction, QInputDialog
from PyQt5.QtGui import QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QLineF
from gates import Gate, GateLinkedList
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSplitter
import numpy as np
import json
import os


class LevelEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Obstacle Course Level Editor")
        self.setGeometry(100, 100, 1000, 800)
        
        # Initialize course data to store all levels
        self.course_data = {
            "courseName": "My Course",
            "levels": []
        }
        
        # Level title graphics item
        self.level_title = None
        
        self.initUI()

    def initUI(self):
        # Menu bar setup
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        levels_menu = menubar.addMenu("Levels")

        # File menu actions
        new_course_action = QAction("New Course", self)
        new_course_action.triggered.connect(self.new_course)
        file_menu.addAction(new_course_action)

        import_course_action = QAction("Import Course", self)
        import_course_action.triggered.connect(self.import_course)
        file_menu.addAction(import_course_action)

        export_course_action = QAction("Export Course", self)
        export_course_action.triggered.connect(self.export_course)
        file_menu.addAction(export_course_action)


        # Levels menu actions
        self.levels_menu = levels_menu
        new_level_action = QAction("New Level", self)
        new_level_action.triggered.connect(self.new_level)
        self.levels_menu.addAction(new_level_action)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Graphics view and scene for level editing
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.layout.addWidget(self.view)

        # Gate linked list to manage gates
        self.gate_list = GateLinkedList()

        # Variable to keep track of gate count
        self.gate_counter = 0

        # Flag to check if course has been created
        self.course_created = False

        # Selected gate item
        self.selected_gate_item = None

        # Connect mouse click event to add gate or select gate
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

        # Create axis labels for the grid
        self.axis_labels = []

        # Splitter for main view and gate stack
        self.splitter = QSplitter()
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        # Graphics view and scene for level editing (existing code)
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.layout.addWidget(self.view)

        # Gate linked list to manage gates (existing code)
        self.gate_list = GateLinkedList()

        # List Widget to display gates in a stack
        self.gate_stack_list = QListWidget()
        self.gate_stack_list.setDragDropMode(QListWidget.InternalMove)
        self.gate_stack_list.setDefaultDropAction(Qt.MoveAction)

        # Enable single selection for the gate list and connect selection changes
        self.gate_stack_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.gate_stack_list.currentItemChanged.connect(self.on_gate_list_selection_changed)

        # Connect the rowsMoved signal of the list model to handle reordering
        self.gate_stack_list.model().rowsMoved.connect(self.on_gate_stack_changed)

        # Widget for buttons at the bottom of the list column
        self.button_widget = QWidget()
        self.button_layout = QVBoxLayout()  # Main vertical layout for multiple rows of buttons
        self.button_widget.setLayout(self.button_layout)

        # First row of buttons
        self.first_row_layout = QHBoxLayout()

        # Add Delete Level button
        self.delete_level_button = QPushButton("Delete Level")
        self.delete_level_button.clicked.connect(self.delete_current_level)
        self.first_row_layout.addWidget(self.delete_level_button)

        # Add Remove Gate button
        self.remove_gate_button = QPushButton("Remove Gate")
        self.remove_gate_button.clicked.connect(self.remove_selected_gate)
        self.first_row_layout.addWidget(self.remove_gate_button)
       
        #add difficulty button
        self.change_difficulty_button = QPushButton("Change Difficulty")
        self.change_difficulty_button.clicked.connect(self.change_selected_gate_difficulty)
        self.first_row_layout.addWidget(self.change_difficulty_button)

        # Add the first row layout to the main button layout
        self.button_layout.addLayout(self.first_row_layout)

        # Second row of buttons
        self.second_row_layout = QHBoxLayout()


        # Add Rotate Left button
        self.rotate_left_button = QPushButton("Rotate Left")
        self.rotate_left_button.clicked.connect(self.rotate_gate_left)
        self.second_row_layout.addWidget(self.rotate_left_button)

        # Add Rotate Right button
        self.rotate_right_button = QPushButton("Rotate Right")
        self.rotate_right_button.clicked.connect(self.rotate_gate_right)
        self.second_row_layout.addWidget(self.rotate_right_button)

        # Add Change Type button
        self.change_type_button = QPushButton("Change Gate Type")
        self.change_type_button.clicked.connect(self.change_selected_gate_type)
        self.second_row_layout.addWidget(self.change_type_button)
        

        # Add the second row layout to the main button layout
        self.button_layout.addLayout(self.second_row_layout)

        # Adding the main layout and gate stack to the splitter
        self.main_widget.setLayout(self.layout)
        self.splitter.addWidget(self.main_widget)

        # Container for list and buttons
        self.list_widget_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget_container)
        self.list_layout.addWidget(self.gate_stack_list)
        self.list_layout.addWidget(self.button_widget)

        self.splitter.addWidget(self.list_widget_container)


        # Set the initial sizes of the splitter panes
        self.splitter.setSizes([800, 200])  # Graphical interface will take more space compared to the list

        self.setCentralWidget(self.splitter)

        # Initialize UI flags and setup
        self.gate_counter = 0
        self.course_created = False
        self.selected_gate_item = None
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)


    def new_course(self):
        floor_width, ok_width = QInputDialog.getInt(self, "New Course", "Enter the floor width:")
        if not ok_width:
            return
        floor_height, ok_height = QInputDialog.getInt(self, "New Course", "Enter the floor height:")
        if not ok_height:
            return
        
        self.floor_width = floor_width
        self.floor_height = floor_height
        self.course_created = True
        self.scene.clear()  # Clear the scene for new course
        self.draw_grid()
        print(f"Created new course with dimensions: {floor_width} x {floor_height}")
        self.new_level()  # Automatically create the first level
       
    def import_course(self):
        # Prompt the user to select a JSON file to import
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Import Course", "", "JSON Files (*.json);;All Files (*)", options=options)

        if filename:
            try:
                # Load the data from the JSON file
                with open(filename, 'r') as json_file:
                    imported_data = json.load(json_file)

                # Ensure the imported data structure is valid
                if "levels" in imported_data:
                    self.course_data = imported_data
                    print(f"Course imported from {filename}")

                    # Clear current levels from the dropdown menu but keep the "New Level" option
                    actions_to_remove = [action for action in self.levels_menu.actions() if action.text() != "New Level"]
                    for action in actions_to_remove:
                        self.levels_menu.removeAction(action)

                    # Add imported levels to the levels menu
                    for level in self.course_data["levels"]:
                        level_name = level["levelName"]
                        level_action = QAction(level_name, self)
                        level_action.triggered.connect(lambda checked, name=level_name: self.load_level_from_course_data(name))
                        self.levels_menu.addAction(level_action)

                    # If there are levels, load the first one by default
                    if self.course_data["levels"]:
                        self.load_level_from_course_data(self.course_data["levels"][0]["levelName"])
                else:
                    print("Invalid course data: no levels found")

            except Exception as e:
                print(f"Error importing course: {e}")


    def export_course(self):
        # Save the current level before exporting
        if self.course_created and hasattr(self, 'level_name'):
            self.save_current_level_to_course_data()

        # Prompt the user to save the JSON file
        filename, _ = QInputDialog.getText(self, "Export Course", "Enter filename for export:")
        if filename:
            if not filename.endswith(".json"):
                filename += ".json"

            try:
                with open(filename, 'w') as json_file:
                    json.dump(self.course_data, json_file, indent=4)
                print(f"Course exported to {filename}")
            except Exception as e:
                print(f"Error exporting course: {e}")


    def save_current_level_to_course_data(self):
        # Construct the data structure for the current level
        level_data = {
            "levelName": self.level_name,
            "floorWidth": self.floor_width,
            "floorLength": self.floor_height,
            "gates": []
        }

        # Traverse the linked list to gather gate data
        current = self.gate_list.head
        while current:
            gate = current.gate
            gate_data = {
                "gate_id": gate.gate_id,
                "x": gate.x,
                "z": gate.z,
                "rotation": gate.rotation,
                "type": gate.type,
                "difficulty": gate.difficulty
            }

            level_data["gates"].append(gate_data)
            current = current.next

        # Update or add the level data in course_data
        existing_level = next((level for level in self.course_data["levels"] if level["levelName"] == self.level_name), None)
        if existing_level:
            # Update existing level
            self.course_data["levels"] = [level if level["levelName"] != self.level_name else level_data for level in self.course_data["levels"]]
        else:
            # Add new level
            self.course_data["levels"].append(level_data)
           
    def load_level_from_course_data(self, level_name):
        # Save the current level before loading a new one
        if self.course_created and hasattr(self, 'level_name'):
            self.save_current_level_to_course_data()

        # Reset selected gate item to avoid accessing deleted objects
        self.selected_gate_item = None

        # Find the level data by name in course_data
        level_data = next((level for level in self.course_data["levels"] if level["levelName"] == level_name), None)

        if level_data:
            # Load the level data into the scene
            self.floor_width = level_data["floorWidth"]
            self.floor_height = level_data["floorLength"]
            self.level_name = level_data["levelName"]

            # Initialize the linked list with gates
            self.gate_list = GateLinkedList()
            self.gate_counter = len(level_data["gates"])

            # Clear the scene and draw the grid
            self.scene.clear()
            self.draw_grid()

            # Draw each gate on the scene
            for gate_data in level_data["gates"]:
                gate = Gate(
                    gate_id=gate_data["gate_id"],
                    x=gate_data["x"],
                    z=gate_data["z"],
                    rotation=gate_data["rotation"],
                    type=gate_data["type"],
                    difficulty=gate_data["difficulty"]
                )
                self.gate_list.add_gate(gate)

                # Create a graphical representation of the gate
                grid_size = 20
                gate_item = DraggableGateItem(gate, grid_size, self.floor_width, self.floor_height, self)
                gate_item.setRotation(gate.rotation)
                gate_item.set_gate_color(Qt.blue)
                gate_item.setFlag(QGraphicsItem.ItemIsMovable)
                gate_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
                gate_item.setAcceptHoverEvents(True)
                self.scene.addItem(gate_item)

                # Add a label above each gate
                roman = self.difficulty_to_roman(gate.difficulty)
                gate_label = QGraphicsTextItem(f"{gate.gate_id}: {roman}")
                gate_label.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
                gate_label.setParentItem(gate_item)
                gate_label.setPos(0, -20)
                gate_label.setScale(0.7)
                gate_item.label = gate_label

            # Update arrows to reflect the new configuration
            self.update_arrows()

            # Set level title
            self.set_level_title(level_name)

            print(f"Loaded level: {level_name}")

        else:
            print(f"Level {level_name} not found in course data.")



    def draw_grid(self):
        grid_size = 20
        # Draw the grid and axis labels
        for x in range(0, self.floor_width * grid_size, grid_size):
            for y in range(0, self.floor_height * grid_size, grid_size):
                rect = QGraphicsRectItem(x, y, grid_size, grid_size)
                rect.setPen(QPen(Qt.gray))
                self.scene.addItem(rect)

        # Add axis labels
        for i in range(self.floor_width):
            label = QGraphicsTextItem(f"{i}")
            label.setPos(i * grid_size, -20)
            self.scene.addItem(label)
            self.axis_labels.append(label)

        for i in range(self.floor_height):
            label = QGraphicsTextItem(f"{i}")
            label.setPos(-20, i * grid_size)
            self.scene.addItem(label)
            self.axis_labels.append(label)
           
    def update_arrows(self):
        """
        Draws a smooth path between the gates to indicate the order, ensuring the path passes through the entry and exit points of all gates.
        """
        # First, remove all existing arrows
        for arrow in self.gate_list.arrows:
            self.scene.removeItem(arrow)
        self.gate_list.arrows = []

        # Traverse the linked list and create a smooth path between nodes
        current = self.gate_list.head

        if current is None or current.next is None:
            return  # No arrows if there's less than two gates

        # Create a QPainterPath for smooth lines
        path = QPainterPath()

        # Start the path from the first gate's entry point
        first_gate_item = self.find_gate_item(current.gate)
        if first_gate_item:
            start_entry_pos = self.get_gate_entry_exit_point(first_gate_item, entry=True)
            path.moveTo(start_entry_pos)

        # Iterate through the gates and add segments
        while current:
            start_gate_item = self.find_gate_item(current.gate)

            if start_gate_item:
                # Get exit point from the current gate
                start_exit_pos = self.get_gate_entry_exit_point(start_gate_item, entry=False)

                # Add the exit point of the current gate to the path
                path.lineTo(start_exit_pos)

                if current.next:
                    # Get entry point for the next gate
                    end_gate_item = self.find_gate_item(current.next.gate)
                    end_entry_pos = self.get_gate_entry_exit_point(end_gate_item, entry=True)

                    # Draw a smooth curve between the exit point of the current gate and the entry point of the next gate
                    path.lineTo(end_entry_pos)

            current = current.next

        # Draw the final path as a QGraphicsPathItem
        arrow_path_item = QGraphicsPathItem(path)
        arrow_path_item.setPen(QPen(Qt.red, 2))  # Set the color and width of the line

        # Add the arrow path to the scene and to the list of arrows
        self.scene.addItem(arrow_path_item)
        self.gate_list.arrows.append(arrow_path_item)






    def new_level(self):
        # Save the current level before creating a new one
        if self.course_created and hasattr(self, 'level_name'):
            self.save_current_level_to_course_data()

        # Prompt the user for the new level name
        level_name, ok = QInputDialog.getText(self, "New Level", "Enter the level name:")
        if not ok or not level_name:
            return

        # Check if the level name already exists
        if any(level["levelName"] == level_name for level in self.course_data["levels"]):
            QMessageBox.warning(self, "Warning", "A level with this name already exists. Please choose a different name.")
            return

        # Reset selected gate item to avoid accessing deleted objects
        self.selected_gate_item = None

        # Store the new level name
        self.level_name = level_name

        # Add level to the levels menu
        level_action = QAction(level_name, self)
        level_action.triggered.connect(lambda: self.load_level_from_course_data(level_name))
        self.levels_menu.addAction(level_action)

        # Initialize new level data and add it to course data
        self.gate_list = GateLinkedList()
        self.gate_counter = 0
        self.scene.clear()
        self.draw_grid()
        self.course_created = True

        # Add the new level to course_data
        new_level_data = {
            "levelName": level_name,
            "floorWidth": self.floor_width if hasattr(self, 'floor_width') else 20,
            "floorLength": self.floor_height if hasattr(self, 'floor_height') else 20,
            "gates": []
        }
        self.course_data["levels"].append(new_level_data)

        # Set level title
        self.set_level_title(level_name)

        print(f"Created and loaded new level: {level_name}")



    def load_level(self, level_name):
        # Save the current level before loading a new one
        if self.course_created and hasattr(self, 'level_name'):
            self.save_all_levels_to_json()

        # Load the selected level from the JSON file
        self.load_level_from_json(level_name)
        
    def delete_current_level(self):
        if not self.course_created or not hasattr(self, 'level_name'):
            QMessageBox.warning(self, "Warning", "No level is currently loaded to delete.")
            return

        # Show a confirmation dialog
        reply = QMessageBox.question(
            self,
            "Delete Level",
            f"Are you sure you want to delete the level '{self.level_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Remove the level from course data
            self.course_data["levels"] = [level for level in self.course_data["levels"] if level["levelName"] != self.level_name]

            # Remove the level from the dropdown menu
            for action in self.levels_menu.actions():
                if action.text() == self.level_name:
                    self.levels_menu.removeAction(action)
                    break

            # Clear the current scene and reset relevant flags
            self.scene.clear()
            self.course_created = False
            self.selected_gate_item = None
            self.level_title = None

            # Load the first level available, if any
            if self.course_data["levels"]:
                self.load_level_from_course_data(self.course_data["levels"][0]["levelName"])
            else:
                # If no levels are left, clear the UI
                self.level_name = None
                self.draw_grid()  # Draw an empty grid if no levels are left

            print(f"Level '{self.level_name}' deleted.")



    def add_gate(self, x, y):
        grid_size = 20
        grid_x = x // grid_size
        grid_y = y // grid_size
        # Create a new Gate object with default rotation 0, type 0, and difficulty 1
        gate = Gate(self.gate_counter, grid_x, grid_y, 0, 0, difficulty=1)
        self.gate_list.add_gate(gate)
        # Draw the gate on the scene
        gate_item = DraggableGateItem(gate, grid_size, self.floor_width, self.floor_height, self)
        gate_item.set_gate_color(QBrush(Qt.blue))
        gate_item.setFlag(QGraphicsItem.ItemIsMovable)
        gate_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        gate_item.setAcceptHoverEvents(True)
        self.scene.addItem(gate_item)
        # Create a label with the difficulty (Roman numeral)
        roman = self.difficulty_to_roman(gate.difficulty)
        gate_label = QGraphicsTextItem(f"{gate.gate_id}: {roman}")
        gate_label.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        gate_label.setParentItem(gate_item)
        gate_label.setPos(0, -20)
        gate_label.setScale(0.7)
        gate_item.label = gate_label
        self.gate_counter += 1
        # Add gate to the list widget with updated label text
        gate_list_item = QListWidgetItem(f"Gate {gate.gate_id} - x: {gate.x}, z: {gate.z}, rotation: {gate.rotation}, type: {gate.type}, difficulty: {roman}")
        gate_list_item.setData(Qt.UserRole, gate)
        self.gate_stack_list.addItem(gate_list_item)
        self.update_arrows()


      
    def on_gate_stack_changed(self):
        """
        Called when the gate order is changed by dragging in the gate stack.
        This method will update the gate linked list and redraw gates and arrows.
        """
        new_gate_order = []
        for index in range(self.gate_stack_list.count()):
            item = self.gate_stack_list.item(index)
            gate = item.data(Qt.UserRole)  # Get the gate associated with this list item
            # Update gate_id to match the new order
            gate.gate_id = index
            new_gate_order.append(gate)

        # Reset selected gate item to avoid accessing deleted objects
        self.selected_gate_item = None

        # Clear and rebuild the linked list with the new order
        self.gate_list = GateLinkedList()
        for gate in new_gate_order:
            self.gate_list.add_gate(gate)

        # Clear the current graphical scene and redraw everything
        self.scene.clear()

        # Draw the grid again
        self.draw_grid()

        # Redraw all gates in the new order with their respective rotations and labels
        grid_size = 20
        for gate in new_gate_order:
            gate_item = DraggableGateItem(gate, grid_size, self.floor_width, self.floor_height, self)

            # Apply the preserved rotation to the gate item
            gate_item.setRotation(gate.rotation)

            gate_item.set_gate_color(Qt.blue)
            gate_item.setFlag(QGraphicsItem.ItemIsMovable)
            gate_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
            gate_item.setAcceptHoverEvents(True)
            self.scene.addItem(gate_item)

            # Update the label to reflect the new gate ID
            roman = self.difficulty_to_roman(gate.difficulty)
            gate_label = QGraphicsTextItem(f"{gate.gate_id}: {roman}")
            gate_label.setParentItem(gate_item)
            gate_label.setPos(0, -20)  # Position label directly above the gate
            gate_label.setScale(0.7)  # Adjust the scale if needed for better readability
            gate_item.label = gate_label

        # Update arrows to reflect the new order
        self.update_arrows()

        # Update the list items to reflect any potential changes (e.g., gate IDs)
        self.gate_stack_list.clear()

        for gate in new_gate_order:
            gate_list_item = QListWidgetItem(f"Gate {gate.gate_id} - x: {gate.x}, z: {gate.z}, rotation: {gate.rotation}, type: {gate.type}, difficulty: {roman}")
            gate_list_item.setData(Qt.UserRole, gate)  # Store the gate object as user data
            self.gate_stack_list.addItem(gate_list_item)







    def refresh_gate_stack_list(self):
        """
        Refresh the gate stack list widget to update the information (x, z, rotation)
        for each gate in the linked list and ensure gate IDs are consistent.
        """
        self.gate_stack_list.clear()
        current = self.gate_list.head
        index = 0
        while current:
            gate = current.gate
            gate.gate_id = index  # Update gate_id if needed
            roman = self.difficulty_to_roman(gate.difficulty)
            gate_list_item = QListWidgetItem(f"Gate {gate.gate_id} - x: {gate.x}, z: {gate.z}, rotation: {gate.rotation}, type: {gate.type}, difficulty: {roman}")
            gate_list_item.setData(Qt.UserRole, gate)
            self.gate_stack_list.addItem(gate_list_item)
            current = current.next
            index += 1



    def highlight_selected_gate_in_list(self, selected_gate):
        """
        Highlights the gate in the list that matches the selected gate.
        
        Parameters:
            selected_gate (Gate): The gate object that has been selected.
        """
        for index in range(self.gate_stack_list.count()):
            item = self.gate_stack_list.item(index)
            gate = item.data(Qt.UserRole)
            if gate == selected_gate:
                self.gate_stack_list.setCurrentItem(item)
                item.setSelected(True)
            else:
                item.setSelected(False)
                
    def on_gate_list_selection_changed(self, current, previous):
        """
        Called when the user selects a gate in the list widget.
        This method will select the corresponding gate in the graphical view.
        
        Parameters:
            current (QListWidgetItem): The currently selected list item.
            previous (QListWidgetItem): The previously selected list item.
        """
        if previous and self.selected_gate_item:
            # Deselect the previously selected gate, if it exists
            try:
                self.selected_gate_item.set_gate_color(QBrush(Qt.blue))
            except RuntimeError:
                # Ignore if the item has already been deleted
                pass

        if current:
            selected_gate = current.data(Qt.UserRole)  # Get the gate associated with this list item

            # Find the corresponding graphical item for the selected gate
            for item in self.scene.items():
                if isinstance(item, DraggableGateItem) and item.gate == selected_gate:
                    # Select the new gate item
                    self.selected_gate_item = item
                    self.selected_gate_item.set_gate_color(QBrush(Qt.green))  # Highlight selected gate
                    break


    def remove_selected_gate(self):
        """
        Removes the currently selected gate from the scene, list, and linked list.
        """
        if not self.selected_gate_item:
            return  # No gate is selected

        # Remove the selected gate from the linked list
        selected_gate = self.selected_gate_item.gate
        current = self.gate_list.head
        prev = None

        # Find and remove the gate from the linked list
        while current:
            if current.gate == selected_gate:
                if prev:
                    prev.next = current.next
                else:
                    self.gate_list.head = current.next
                self.gate_list.size -= 1
                break
            prev = current
            current = current.next

        # Remove the gate from the graphical scene
        self.scene.removeItem(self.selected_gate_item)
        if hasattr(self.selected_gate_item, 'label'):
            self.scene.removeItem(self.selected_gate_item.label)
        self.selected_gate_item = None

        # Refresh the gate stack list and reassign gate IDs
        self.refresh_gate_stack_list()

        # Update arrows after gate removal
        self.update_arrows()

    def rotate_gate_left(self):
        if self.selected_gate_item:
            self.selected_gate_item.gate.rotation -= 45
            self.selected_gate_item.gate.rotation %= 360
            self.update_gate_rotation(self.selected_gate_item)
            self.refresh_gate_stack_list()
            self.update_arrows()

    def rotate_gate_right(self):
        if self.selected_gate_item:
            self.selected_gate_item.gate.rotation += 45
            self.selected_gate_item.gate.rotation %= 360
            self.update_gate_rotation(self.selected_gate_item)
            self.refresh_gate_stack_list()
            self.update_arrows()
            
    def change_selected_gate_type(self):
        if not self.selected_gate_item:
            return  # No gate is selected

        # Cycle through gate types: 0 (normal), 1 (step on), 2 (step over)
        current_type = self.selected_gate_item.gate.type
        new_type = (current_type + 1) % 3
        self.selected_gate_item.gate.type = new_type

        # Remove the current graphical representation of the gate
        self.scene.removeItem(self.selected_gate_item)

        # Create a new graphical representation for the gate with the updated type
        grid_size = 20
        new_gate_item = DraggableGateItem(self.selected_gate_item.gate, grid_size, self.floor_width, self.floor_height, self)
        new_gate_item.setRotation(self.selected_gate_item.gate.rotation)
        self.scene.addItem(new_gate_item)

        # Re-create the label with gate ID and difficulty in Roman numerals
        roman = self.difficulty_to_roman(new_gate_item.gate.difficulty)
        label_text = f"{new_gate_item.gate.gate_id}: {roman}"
        gate_label = QGraphicsTextItem(label_text)
        gate_label.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)  # Keep label upright
        gate_label.setParentItem(new_gate_item)
        gate_label.setPos(0, -20)  # Position above the gate
        gate_label.setScale(0.7)
        new_gate_item.label = gate_label

        # If the gate was selected, reapply the selected (green) color
        new_gate_item.set_gate_color(QBrush(Qt.green))
        self.selected_gate_item = new_gate_item

        # Refresh the gate stack list to reflect the updated gate type
        self.refresh_gate_stack_list()


    def change_selected_gate_difficulty(self):
        if not self.selected_gate_item:
            return  # No gate is selected
        # Cycle through difficulty levels: 1 -> 2 -> 3 -> 1
        current_diff = self.selected_gate_item.gate.difficulty
        new_diff = (current_diff % 3) + 1
        self.selected_gate_item.gate.difficulty = new_diff
        # Update the gate's label to show the new difficulty
        roman = self.difficulty_to_roman(new_diff)
        new_text = f"{self.selected_gate_item.gate.gate_id}: {roman}"
        self.selected_gate_item.label.setPlainText(new_text)
        # Refresh the gate stack list to update the text there as well
        self.refresh_gate_stack_list()




    def update_gate_rotation(self, gate_item):
        """
        Updates the rotation of a gate in the graphical view.
        
        Parameters:
            gate_item (DraggableGateItem): The gate item to update.
        """
        # Apply rotation transformation to the gate item
        gate_item.setRotation(gate_item.gate.rotation)




    def eventFilter(self, source, event):
        if event.type() == event.MouseButtonPress and source == self.view.viewport() and self.course_created:
            if event.button() == Qt.LeftButton:
                # Get mouse click position and snap to grid
                grid_size = 20
                scene_pos = self.view.mapToScene(event.pos())
                x = int(scene_pos.x() // grid_size) * grid_size
                y = int(scene_pos.y() // grid_size) * grid_size

                # Ensure the click is within grid boundaries and adjust accordingly
                x = max(0, min(x, (self.floor_width - 1) * grid_size))
                y = max(0, min(y, (self.floor_height - 1) * grid_size))

                # Check if a gate was clicked
                item = self.scene.itemAt(scene_pos, self.view.transform())

                # If an existing gate is clicked, select it
                if isinstance(item, DraggableGateItem):
                    if self.selected_gate_item:
                        try:
                            self.selected_gate_item.set_gate_color(Qt.blue)  # Deselect previous gate
                        except RuntimeError:
                            # Item has already been deleted, reset it
                            self.selected_gate_item = None

                    # Select the clicked gate
                    self.selected_gate_item = item
                    self.selected_gate_item.set_gate_color(Qt.green)  # Highlight selected gate

                # If no gate is clicked, check if the spot already has a gate
                else:
                    # Check if there is any gate occupying the current grid position
                    for gate_item in self.scene.items():
                        if isinstance(gate_item, DraggableGateItem):
                            gate_rect = gate_item.sceneBoundingRect()
                            if gate_rect.contains(scene_pos):
                                # If the clicked position already has a gate, do not create a new one
                                return super().eventFilter(source, event)

                    # If no gate occupies the grid spot, add a new gate
                    self.add_gate(x, y)

        return super().eventFilter(source, event)





    
    #helper
    def find_gate_item(self, gate):
        """
        Finds the DraggableGateItem in the scene corresponding to the given gate.
        
        Parameters:
            gate (Gate): The gate object to find.
            
        Returns:
            DraggableGateItem: The corresponding gate item, or None if not found.
        """
        for item in self.scene.items():
            if isinstance(item, DraggableGateItem) and item.gate == gate:
                return item
        return None
    
    def get_gate_entry_exit_point(self, gate_item, entry=True):
        """
        Gets the entry or exit point for a gate, based on its rotation.
        
        Parameters:
            gate_item (DraggableGateItem): The gate item to get the point for.
            entry (bool): Whether to get the entry point (True) or exit point (False).
            
        Returns:
            QPointF: The calculated entry or exit point.
        """
        # Get the center position of the gate
        rect = gate_item.sceneBoundingRect()
        center_x = rect.center().x()
        center_y = rect.center().y()

        # Offset distance for entry and exit points
        offset_distance = gate_item.grid_size / 2

        # Calculate angle in radians for easier trigonometric calculations
        rotation_angle = np.radians(gate_item.gate.rotation)

        if entry:
            # Entry point should be at the bottom of the gate relative to its rotation
            offset_x = center_x - offset_distance * np.sin(rotation_angle)
            offset_y = center_y + offset_distance * np.cos(rotation_angle)
        else:
            # Exit point should be at the top of the gate relative to its rotation
            offset_x = center_x + offset_distance * np.sin(rotation_angle)
            offset_y = center_y - offset_distance * np.cos(rotation_angle)

        return QPointF(offset_x, offset_y)
    
    def save_all_levels_to_json(self):
        # Save all levels to a temporary JSON file
        try:
            # Construct the data structure to save all levels
            all_levels_data = {
                "levels": []
            }

            # Iterate through the levels in the menu and gather the data for each level
            for i in range(len(self.levels_menu.actions())):
                level_action = self.levels_menu.actions()[i]
                level_name = level_action.text()

                # Get the current level's data from memory
                if level_name == self.level_name:
                    level_data = {
                        "levelName": level_name,
                        "floorWidth": self.floor_width,
                        "floorLength": self.floor_height,
                        "gates": []
                    }

                    # Traverse the linked list to gather gate data
                    current = self.gate_list.head
                    while current:
                        gate = current.gate
                        gate_data = {
                            "gate_id": gate.gate_id,
                            "x": gate.x,
                            "z": gate.z,
                            "rotation": gate.rotation,
                            "type": gate.type
                        }
                        level_data["gates"].append(gate_data)
                        current = current.next

                    all_levels_data["levels"].append(level_data)

            # Save to a JSON file
            with open('temporary_levels.json', 'w') as json_file:
                json.dump(all_levels_data, json_file, indent=4)
            print("All levels saved to temporary_levels.json")
        except Exception as e:
            print(f"Error saving levels to JSON: {e}")

            
    def load_level_from_json(self, level_name):
        # Load levels from the JSON file
        if not os.path.exists('temporary_levels.json'):
            print("No levels have been saved yet.")
            return

        try:
            with open('temporary_levels.json', 'r') as json_file:
                data = json.load(json_file)

            # Find the level data by name
            level_data = next((level for level in data["levels"] if level["levelName"] == level_name), None)

            if level_data:
                # Reset selected gate item to avoid accessing deleted objects
                self.selected_gate_item = None

                # Load the level data into the scene
                self.floor_width = level_data["floorWidth"]
                self.floor_height = level_data["floorLength"]
                self.level_name = level_data["levelName"]

                # Initialize the linked list with gates
                self.gate_list = GateLinkedList()
                self.gate_counter = len(level_data["gates"])

                # Clear the scene and draw the grid
                self.scene.clear()
                self.draw_grid()

                # Draw each gate on the scene
                for gate_data in level_data["gates"]:
                    gate = Gate(
                        gate_id=gate_data["gate_id"],
                        x=gate_data["x"],
                        z=gate_data["z"],
                        rotation=gate_data["rotation"],
                        type=gate_data["type"],
                        difficulty=gate_data.get("difficulty", 1)
                    )
                    self.gate_list.add_gate(gate)

                    # Create a graphical representation of the gate
                    grid_size = 20
                    gate_item = DraggableGateItem(gate, grid_size, self.floor_width, self.floor_height, self)
                    gate_item.setRotation(gate.rotation)
                    gate_item.set_gate_color(Qt.blue)
                    gate_item.setFlag(QGraphicsItem.ItemIsMovable)
                    gate_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
                    gate_item.setAcceptHoverEvents(True)
                    self.scene.addItem(gate_item)

                    # Add a label above each gate
                    gate_label = QGraphicsTextItem(f"Gate {gate.gate_id}")
                    gate_label.setParentItem(gate_item)
                    gate_label.setPos(0, -20)
                    gate_label.setScale(0.7)
                    gate_item.label = gate_label

                # Update arrows to reflect the new configuration
                self.update_arrows()

                print(f"Loaded level: {level_name}")

        except Exception as e:
            print(f"Error loading level from JSON: {e}")
            
    def set_level_title(self, level_name):
        # Check if the title exists and remove it from the scene
        if self.level_title is not None:
            try:
                self.scene.removeItem(self.level_title)
            except RuntimeError:
                # If the title has already been deleted, ignore the error
                pass

        # Create a new title with a larger font
        self.level_title = QGraphicsTextItem(level_name)
        font = self.level_title.font()
        font.setPointSize(20)
        font.setBold(True)
        self.level_title.setFont(font)
        self.level_title.setDefaultTextColor(Qt.black)
        self.level_title.setPos(20, -60)  # Adjust position to place it above the grid
        self.scene.addItem(self.level_title)


    def difficulty_to_roman(self, difficulty):
        mapping = {1: "I", 2: "II", 3: "III"}
        return mapping.get(difficulty, "I")





class DraggableGateItem(QGraphicsItemGroup):
    def __init__(self, gate, grid_size, floor_width, floor_height, editor_ref, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store gate properties and reference to main editor
        self.gate = gate
        self.grid_size = grid_size
        self.floor_width = floor_width
        self.floor_height = floor_height
        self.editor_ref = editor_ref

        # Create an invisible background to cover the entire grid square for easier selection
        self.background = QGraphicsRectItem(0, 0, grid_size, grid_size)
        self.background.setBrush(QBrush(Qt.transparent))
        self.background.setPen(QPen(Qt.NoPen))  # No border to avoid visual clutter

        # Draw the gate based on its type
        if gate.type == 0:
            # Default gate (two thick bars)
            bar_width = grid_size * 0.25  # Width of each bar (thick)
            bar_height = grid_size  # Height of each bar (entire grid square height)

            # Create the first bar (left side)
            self.bar1 = QGraphicsRectItem(0, 0, bar_width, bar_height)
            self.bar1.setBrush(QBrush(Qt.blue))

            # Create the second bar (right side)
            self.bar2 = QGraphicsRectItem(grid_size - bar_width, 0, bar_width, bar_height)
            self.bar2.setBrush(QBrush(Qt.blue))

            # Add bars to the item group
            self.addToGroup(self.bar1)
            self.addToGroup(self.bar2)

        elif gate.type == 1:
            # Step-on gate (draw as a filled circle)
            self.circle = QGraphicsEllipseItem(0, 0, grid_size, grid_size)
            self.circle.setBrush(QBrush(Qt.red))
            self.circle.setPen(QPen(Qt.NoPen))
            self.addToGroup(self.circle)

        elif gate.type == 2:
            # Step-over gate (draw as a square shape)
            self.square = QGraphicsRectItem(0, 0, grid_size, grid_size)
            self.square.setBrush(QBrush(Qt.blue))
            self.addToGroup(self.square)
            # self.line1 = QGraphicsLineItem(0, 0, grid_size-grid_size/2, grid_size-grid_size/2)
            # self.line1.setPen(QPen(Qt.green, 4))
            # self.line2 = QGraphicsLineItem(grid_size-grid_size/2, 0, 0, grid_size-grid_size/2)
            # self.line2.setPen(QPen(Qt.green, 4))
            # self.addToGroup(self.line1)
            # self.addToGroup(self.line2)

        # Add the background to the item group (after other elements for easier selection)
        self.addToGroup(self.background)

        # Set the initial position of the entire gate
        self.setPos(gate.x * grid_size, gate.z * grid_size)

        # Set the transformation origin point to the center of the grid square
        self.setTransformOriginPoint(grid_size / 2, grid_size / 2)

        # Allow the gate to be moved and rotated
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Mark the gate as fully initialized
        self.initialized = True

    def set_gate_color(self, color):
        """
        Sets the color of the gate depending on its type.
        
        Parameters:
            color (QColor): The color to set for the gate elements.
        """
        if hasattr(self, 'bar1') and hasattr(self, 'bar2'):
            # If the gate has bars, update their color
            self.bar1.setBrush(QBrush(color))
            self.bar2.setBrush(QBrush(color))
        elif hasattr(self, 'circle'):
            # If the gate is a circle (step-on type), update its color
            self.circle.setBrush(QBrush(color))
        elif hasattr(self, 'square') :
            # If the gate is a cross ("X" shape), update the color of both lines
            self.square.setBrush(QBrush(color))


    def mousePressEvent(self, event):
        """
        Handles mouse press events on the gate item.
        This prevents creating a new gate when clicking on an existing one.
        """
        # Notify the editor that this gate has been selected
        if self.editor_ref.selected_gate_item:
            # Deselect the previously selected gate
            self.editor_ref.selected_gate_item.set_gate_color(Qt.blue)
            
        # Select the current gate
        self.editor_ref.selected_gate_item = self
        self.set_gate_color(Qt.green)  # Highlight the selected gate

        # Call the base class implementation to maintain dragging behavior
        super().mousePressEvent(event)



    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and hasattr(self, 'initialized') and self.initialized:
            new_pos = value  # Get the new proposed position directly as QPointF
            # Snap to grid
            new_x = int(new_pos.x() // self.grid_size) * self.grid_size
            new_y = int(new_pos.y() // self.grid_size) * self.grid_size

            # Ensure the gate stays within the grid boundaries
            new_x = max(0, min(new_x, (self.floor_width - 1) * self.grid_size))
            new_y = max(0, min(new_y, (self.floor_height - 1) * self.grid_size))

            # Update gate's internal coordinates
            self.gate.x = new_x // self.grid_size
            self.gate.z = new_y // self.grid_size
            # print(f"Gate updated to new position: ({self.gate.x}, {self.gate.z})")  # Debugging output

            # Update arrows after gate has been moved
            self.editor_ref.update_arrows()

            # Refresh the gate stack list to reflect the updated coordinates
            self.editor_ref.refresh_gate_stack_list()

            # Keep the corresponding gate highlighted in the list
            self.editor_ref.highlight_selected_gate_in_list(self.gate)

            # Return the adjusted position
            return QPointF(new_x, new_y)

        return super().itemChange(change, value)
    
    




if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = LevelEditor()
    editor.show()
    sys.exit(app.exec_())

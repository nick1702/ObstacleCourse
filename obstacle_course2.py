import tkinter as tk
from tkinter import filedialog
import json

class LevelEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Obstacle Course Level Editor")

        # Menu
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Level", command=self.new_level)
        filemenu.add_command(label="Import", command=self.import_level)
        filemenu.add_command(label="Export", command=self.export_level)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

        # Toolbar
        toolbar = tk.Frame(root, bd=1, relief=tk.RAISED)
        new_level_btn = tk.Button(toolbar, text="New Level", command=self.new_level)
        new_level_btn.pack(side=tk.LEFT, padx=2, pady=2)
        rotate_left_btn = tk.Button(toolbar, text="Rotate Left", command=lambda: self.rotate_gate(-15))
        rotate_left_btn.pack(side=tk.LEFT, padx=2, pady=2)
        rotate_right_btn = tk.Button(toolbar, text="Rotate Right", command=lambda: self.rotate_gate(15))
        rotate_right_btn.pack(side=tk.LEFT, padx=2, pady=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Canvas
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bindings
        self.canvas.bind("<Button-1>", self.on_click)

        # Initial Level Data
        self.level_data = {
            "levelName": "Default Level",
            "floorWidth": 20,
            "floorLength": 20,
            "gates": []
        }

        self.selected_gate = None
        self.gate_items = {}  # Maps gate IDs to canvas items
        self.draw_grid()

    def new_level(self):
        # Create a new level
        self.level_data = {
            "levelName": "New Level",
            "floorWidth": 20,
            "floorLength": 20,
            "gates": []
        }
        self.canvas.delete("all")
        self.draw_grid()

    def import_level(self):
        # Import level from JSON
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                self.level_data = json.load(file)
                self.load_gates()

    def export_level(self):
        # Export level to JSON
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.level_data, file, indent=4)

    def draw_grid(self):
        # Draw grid on the canvas
        self.canvas.delete("grid_line")
        grid_size = 20
        width = int(self.canvas.cget("width"))
        height = int(self.canvas.cget("height"))
        for i in range(0, width, grid_size):
            self.canvas.create_line([(i, 0), (i, height)], tag='grid_line', fill='gray')
        for i in range(0, height, grid_size):
            self.canvas.create_line([(0, i), (width, i)], tag='grid_line', fill='gray')

    def on_click(self, event):
        # Handle click to add/select a gate
        x, y = event.x, event.y
        clicked_item = self.canvas.find_closest(x, y)
        item_tags = self.canvas.gettags(clicked_item)

        if "gate" in item_tags:
            # Select the gate
            self.select_gate(clicked_item)
        else:
            # Add a new gate
            self.add_gate(x, y)

    def add_gate(self, x, y):
        # Snap to grid
        grid_size = 20
        x = (x // grid_size) * grid_size
        y = (y // grid_size) * grid_size

        gate_id = f"Gate_{len(self.level_data['gates']) + 1}"
        gate = {
            "gate_id": gate_id,
            "x": x,
            "y": y,
            "rotation": 0
        }
        self.level_data['gates'].append(gate)
        gate_item = self.canvas.create_rectangle(x - 10, y - 10, x + 10, y + 10, fill="blue", tags=("gate", gate_id))
        gate_label = self.canvas.create_text(x, y - 15, text=gate_id, tags=("gate_label", gate_id))
        self.gate_items[gate_id] = (gate_item, gate_label)
        self.select_gate(gate_item)

    def select_gate(self, gate_item):
        # Select a gate
        self.selected_gate = gate_item
        self.canvas.itemconfig("gate", outline="")  # Deselect all gates
        self.canvas.itemconfig(gate_item, outline="red")

    def rotate_gate(self, angle):
        # Rotate the selected gate by the given angle
        if self.selected_gate:
            gate_tags = self.canvas.gettags(self.selected_gate)
            gate_id = gate_tags[1]
            for gate in self.level_data['gates']:
                if gate['gate_id'] == gate_id:
                    gate['rotation'] = (gate['rotation'] + angle) % 360
                    self.update_gate_label(gate)
                    break

    def update_gate_label(self, gate):
        # Update the label to show the current rotation
        gate_id = gate['gate_id']
        _, gate_label = self.gate_items[gate_id]
        self.canvas.itemconfig(gate_label, text=f"{gate_id} ({gate['rotation']}°)")

    def load_gates(self):
        # Load gates from level data
        self.canvas.delete("gate")
        self.canvas.delete("gate_label")
        self.gate_items.clear()
        for gate in self.level_data['gates']:
            x, y = gate['x'], gate['y']
            gate_id = gate['gate_id']
            gate_item = self.canvas.create_rectangle(x - 10, y - 10, x + 10, y + 10, fill="blue", tags=("gate", gate_id))
            gate_label = self.canvas.create_text(x, y - 15, text=f"{gate_id} ({gate['rotation']}°)", tags=("gate_label", gate_id))
            self.gate_items[gate_id] = (gate_item, gate_label)

if __name__ == "__main__":
    root = tk.Tk()
    app = LevelEditor(root)
    root.mainloop()

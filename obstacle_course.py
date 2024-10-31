import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import random
import math

class LevelEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Level Editor")
        
        # Main UI frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True)
        
        # Canvas for level design (initially hidden)
        self.canvas = tk.Canvas(main_frame, bg='lightgrey')
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.grid_remove()
        
        # Storage for gates, level info, and levels
        self.gates = []
        self.level_info = None  # No level initially loaded or created
        self.levels = {}  # Stores levels by name
        self.current_level_name = None
        self.grid_size = 20  # Initialize grid size
        
        # Bindings for drag and drop
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Menu setup
        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Import Level", command=self.import_level)
        file_menu.add_command(label="Export Level", command=self.export_level)
        file_menu.add_command(label="Clear All Gates", command=self.clear_gates)
        menu_bar.add_cascade(label="File", menu=file_menu)

        level_menu = tk.Menu(menu_bar, tearoff=0)
        self.level_menu = level_menu  # Store reference for updating
        menu_bar.add_cascade(label="Levels", menu=level_menu)
        root.config(menu=menu_bar)

        # UI Elements for creating new levels and gate management
        toolbar_frame = tk.Frame(main_frame, width=100)
        toolbar_frame.grid(row=0, column=1, sticky="ns")
        
        self.new_level_button = tk.Button(toolbar_frame, text="New Level", command=self.new_level)
        self.new_level_button.pack(pady=5)
        
        self.edit_floor_button = tk.Button(toolbar_frame, text="Edit Level Dimensions", command=self.edit_level_dimensions)
        self.edit_floor_button.pack(pady=5)
        self.edit_floor_button.config(state=tk.DISABLED)
        
        self.remove_gate_button = tk.Button(toolbar_frame, text="Remove Gate", command=self.remove_gate)
        self.remove_gate_button.pack(pady=5)
        self.remove_gate_button.config(state=tk.DISABLED)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        self.selected_gate = None
        self.rotation_handle = None
        self.is_rotating = False

    def draw_grid(self):
        if not self.level_info:
            return
        self.canvas.delete("grid_line")
        for i in range(0, self.level_info['floorWidth'] * self.grid_size, self.grid_size):
            self.canvas.create_line([(i, 0), (i, self.level_info['floorLength'] * self.grid_size)], tag="grid_line", fill="gray")
        for i in range(0, self.level_info['floorLength'] * self.grid_size, self.grid_size):
            self.canvas.create_line([(0, i), (self.level_info['floorWidth'] * self.grid_size, i)], tag="grid_line", fill="gray")

        # Resize the canvas based on the level dimensions
        self.canvas.config(width=self.level_info['floorWidth'] * self.grid_size, height=self.level_info['floorLength'] * self.grid_size)
        self.canvas.grid()  # Make sure the canvas is visible

    def on_click(self, event):
        if not self.level_info:
            return
        # Deselect any previously selected gate
        if self.selected_gate:
            self.draw_gate(self.selected_gate, highlight=False)
            self.clear_rotation_handle()
        self.selected_gate = None
        self.remove_gate_button.config(state=tk.DISABLED)

        # Check if we clicked on an existing gate
        for gate in self.gates:
            if self.canvas.find_withtag(gate['tag']) and self.canvas.find_withtag(gate['tag'])[0] == self.canvas.find_closest(event.x, event.y)[0]:
                # If selected, highlight gate
                self.selected_gate = gate
                self.draw_gate(gate, highlight=True)
                self.create_rotation_handle(gate)
                self.remove_gate_button.config(state=tk.NORMAL)
                return
        
        # Create new gate if clicked on empty space
        if not self.is_rotating:
            self.add_gate(event.x, event.y)
            self.clear_rotation_handle()

    def on_drag(self, event):
        if not self.level_info or not self.selected_gate:
            return

        if self.is_rotating:
            # Calculate rotation angle
            gate = self.selected_gate
            gate_center = (gate['x'], gate['y'])
            angle = math.degrees(math.atan2(event.y - gate_center[1], event.x - gate_center[0]))
            gate['rotation'] = angle
            self.draw_gate(gate, highlight=True)
            self.update_gate_info_label(gate)
        else:
            # Update gate position with snapping to grid
            self.selected_gate['x'] = round(event.x / self.grid_size) * self.grid_size
            self.selected_gate['y'] = round(event.y / self.grid_size) * self.grid_size
            # Redraw the gate
            self.draw_gate(self.selected_gate, highlight=True)
            self.update_gate_info_label(self.selected_gate)

    def on_release(self, event):
        self.is_rotating = False

    def create_rotation_handle(self, gate):
        self.clear_rotation_handle()
        handle_size = 10
        handle_x = gate['x'] + 30
        handle_y = gate['y']
        self.rotation_handle = self.canvas.create_oval(handle_x - handle_size, handle_y - handle_size,
                                                       handle_x + handle_size, handle_y + handle_size,
                                                       fill='green', tags="rotation_handle")
        self.canvas.tag_bind(self.rotation_handle, "<Button-1>", self.start_rotation)
        self.canvas.tag_bind(self.rotation_handle, "<B1-Motion>", self.on_rotate_drag)

    def start_rotation(self, event):
        self.is_rotating = True

    def on_rotate_drag(self, event):
        if not self.selected_gate:
            return
        # Update the rotation based on dragging the handle
        gate = self.selected_gate
        gate_center = (gate['x'], gate['y'])
        angle = math.degrees(math.atan2(event.y - gate_center[1], event.x - gate_center[0]))
        gate['rotation'] = angle
        self.draw_gate(gate, highlight=True)

    def clear_rotation_handle(self):
        if self.rotation_handle:
            self.canvas.delete(self.rotation_handle)
            self.rotation_handle = None

    def draw_gate(self, gate, highlight=False):
        # Clear the old gate drawing
        self.canvas.delete(gate['tag'])
        # Draw the gate as a rectangle with a line representing the rotation
        size = 20
        x, y = gate['x'], gate['y']
        angle_rad = math.radians(gate['rotation'])
        end_x = x + size * math.cos(angle_rad)
        end_y = y + size * math.sin(angle_rad)
        color = 'blue' if not highlight else 'green'
        self.canvas.create_rectangle(x - size, y - size, x + size, y + size, fill=color, tags=gate['tag'])
        self.canvas.create_line(x, y, end_x, end_y, fill='red', tags=gate['tag'])
        # Add the gate value as a label
        self.canvas.create_text(x, y - size - 10, text=f"{gate['value']} (x: {x:.1f}, y: {y:.1f}, rot: {gate['rotation']:.1f})", tags=gate['tag'])

    def add_gate(self, x, y):
        # Snap position to grid
        x = round(x / self.grid_size) * self.grid_size
        y = round(y / self.grid_size) * self.grid_size
        gate_tag = f"gate_{random.randint(1000, 9999)}"
        gate = {
            'tag': gate_tag,
            'x': x,
            'y': y,
            'rotation': 0,
            'value': f"Gate_{len(self.gates) + 1}"
        }
        self.gates.append(gate)
        self.draw_gate(gate)

    def remove_gate(self):
        if self.selected_gate:
            self.gates.remove(self.selected_gate)
            self.canvas.delete(self.selected_gate['tag'])
            self.clear_rotation_handle()
            self.selected_gate = None
            self.remove_gate_button.config(state=tk.DISABLED)

    def import_level(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.clear_gates()
                self.level_info = {
                    'floorWidth': data.get('floorWidth', 20),
                    'floorLength': data.get('floorLength', 20)
                }
                self.current_level_name = data.get('levelName', 'Unnamed')
                self.levels[self.current_level_name] = data
                self.update_level_menu()
                self.draw_grid()
                for gate_data in data.get('gates', []):
                    gate_tag = f"gate_{random.randint(1000, 9999)}"
                    gate = {
                        'tag': gate_tag,
                        'x': gate_data['x'],
                        'y': gate_data['z'],  # Assuming z is used as y in the 2D editor
                        'rotation': gate_data['rotation'],
                        'value': gate_data.get('value', '1')
                    }
                    self.gates.append(gate)
                    self.draw_gate(gate)
                self.edit_floor_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import level: {e}")

    def export_level(self):
        if not self.level_info:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            level_data = {
                'levelName': self.current_level_name if self.current_level_name else "Unnamed",
                'floorWidth': self.level_info['floorWidth'],
                'floorLength': self.level_info['floorLength'],
                'gates': [
                    {
                        'gate_id': gate['value'],
                        'x': gate['x'],
                        'z': gate['y'],  # Assuming y in the editor is z in the game
                        'rotation': gate['rotation']
                    } for gate in self.gates
                ]
            }
            with open(file_path, 'w') as file:
                json.dump(level_data, file, indent=4)
            messagebox.showinfo("Export Successful", "Level exported successfully!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export level: {e}")

    def clear_gates(self):
        for gate in self.gates:
            self.canvas.delete(gate['tag'])
        self.gates.clear()
        self.clear_rotation_handle()
        self.remove_gate_button.config(state=tk.DISABLED)

    def new_level(self):
        level_name = simpledialog.askstring("Level Name", "Enter the level name:")
        floor_width = simpledialog.askinteger("Floor Width", "Enter floor width:", initialvalue=20)
        floor_length = simpledialog.askinteger("Floor Length", "Enter floor length:", initialvalue=20)
        if level_name and floor_width and floor_length:
            self.clear_gates()
            self.level_info = {'floorWidth': floor_width, 'floorLength': floor_length}
            self.current_level_name = level_name
            self.levels[level_name] = self.level_info
            self.update_level_menu()
            messagebox.showinfo("New Level", f"Created a new level: {level_name}. You can now add gates.")
            self.edit_floor_button.config(state=tk.NORMAL)
            self.draw_grid()

    def edit_level_dimensions(self):
        if not self.level_info:
            return
        floor_width = simpledialog.askinteger("Edit Floor Width", "Enter floor width:", initialvalue=self.level_info['floorWidth'])
        floor_length = simpledialog.askinteger("Edit Floor Length", "Enter floor length:", initialvalue=self.level_info['floorLength'])
        if floor_width is not None and floor_length is not None:
            self.level_info['floorWidth'] = floor_width
            self.level_info['floorLength'] = floor_length
            self.draw_grid()
            messagebox.showinfo("Dimensions Updated", f"Floor dimensions updated to {floor_width}x{floor_length}")

    def update_level_menu(self):
        self.level_menu.delete(0, tk.END)
        for level_name in self.levels.keys():
            self.level_menu.add_command(label=level_name, command=lambda name=level_name: self.load_level(name))

    def load_level(self, level_name):
        if level_name in self.levels:
            self.clear_gates()
            self.level_info = self.levels[level_name]
            self.current_level_name = level_name
            self.draw_grid()
            for gate_data in self.level_info.get('gates', []):
                gate_tag = f"gate_{random.randint(1000, 9999)}"
                gate = {
                    'tag': gate_tag,
                    'x': gate_data['x'],
                    'y': gate_data['z'],  # Assuming z is used as y in the 2D editor
                    'rotation': gate_data['rotation'],
                    'value': gate_data.get('value', '1')
                }
                self.gates.append(gate)
                self.draw_gate(gate)
            self.edit_floor_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = LevelEditor(root)
    root.mainloop()

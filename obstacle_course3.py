import json

class Gate:
    def __init__(self, gate_id, x, z, rotation):
        self.gate_id = gate_id
        self.x = x
        self.z = z
        self.rotation = rotation

    def to_dict(self):
        return {
            "gate_id": self.gate_id,
            "x": self.x,
            "z": self.z,
            "rotation": self.rotation
        }

class LinkedListNode:
    def __init__(self, gate):
        self.gate = gate
        self.next = None

class GateLinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def add_gate(self, gate):
        new_node = LinkedListNode(gate)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def insert_gate(self, index, gate):
        new_node = LinkedListNode(gate)
        if index == 0:
            new_node.next = self.head
            self.head = new_node
        else:
            current = self.head
            for _ in range(index - 1):
                if current.next is None:
                    break
                current = current.next
            new_node.next = current.next
            current.next = new_node
        self.size += 1

    def remove_gate(self, index):
        if index == 0:
            if self.head:
                self.head = self.head.next
        else:
            current = self.head
            for _ in range(index - 1):
                if current.next is None:
                    return
                current = current.next
            if current.next:
                current.next = current.next.next
        self.size -= 1

    def change_gate_order(self, old_index, new_index):
        if old_index == new_index or old_index < 0 or new_index < 0 or old_index >= self.size or new_index >= self.size:
            return

        # Remove the gate from the old position
        current = self.head
        prev = None
        for _ in range(old_index):
            prev = current
            current = current.next

        if prev:
            prev.next = current.next
        else:
            self.head = current.next

        # Insert the gate at the new position
        self.insert_gate(new_index, current.gate)

    def to_list(self):
        gates = []
        current = self.head
        index = 0
        while current:
            gate_dict = current.gate.to_dict()
            if index == 0:
                gate_dict["gate_id"] = "start"
            elif index == self.size - 1:
                gate_dict["gate_id"] = "end"
            else:
                gate_dict["gate_id"] = str(index)
            gates.append(gate_dict)
            current = current.next
            index += 1
        return gates

def get_level_info():
    level_name = input("Enter the level name: ")
    floor_width = int(input("Enter the floor width: "))
    floor_length = int(input("Enter the floor length: "))
    return {
        "levelName": level_name,
        "floorWidth": floor_width,
        "floorLength": floor_length,
        "gates": []
    }

def get_gate_info(gate_index):
    x = int(input(f"Enter x coordinate for gate '{gate_index}': "))
    z = int(input(f"Enter z coordinate for gate '{gate_index}': "))
    rotation = float(input(f"Enter rotation for gate '{gate_index}' (in degrees): "))
    return Gate(gate_index, x, z, rotation)

def main():
    level = get_level_info()
    total_gates = int(input("Enter the total number of gates (excluding start and end): "))
    gates_list = GateLinkedList()

    # Add gates including start and end
    gates_list.add_gate(get_gate_info(0))  # Start gate
    for i in range(1, total_gates + 1):
        gates_list.add_gate(get_gate_info(i))
    gates_list.add_gate(get_gate_info(total_gates + 1))  # End gate

    while True:
        change_order = input("Do you want to change the order of any gates? (yes/no): ").strip().lower()
        if change_order == 'yes':
            old_index = int(input("Enter the current index of the gate to move: "))
            new_index = int(input("Enter the new index for the gate: "))
            gates_list.change_gate_order(old_index, new_index)
        elif change_order == 'no':
            break
        else:
            print("Please enter 'yes' or 'no'.")

    level['gates'] = gates_list.to_list()
    
    file_name = input("Enter the filename to save the level (e.g., level1.json): ")
    with open(file_name, 'w') as json_file:
        json.dump(level, json_file, indent=4)
    print(f"Level saved to {file_name}")

if __name__ == "__main__":
    main()

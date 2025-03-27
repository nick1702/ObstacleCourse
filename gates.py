class Gate:
    def __init__(self, gate_id, x, z, rotation, type, difficulty=1):
        """
        Initializes a new gate object.
       
        Parameters:
            gate_id (int): The identifier for the gate.
            x (int): The x-coordinate of the gate.
            z (int): The z-coordinate of the gate.
            rotation (float): The rotation of the gate in degrees.
            type (int): 0 = normal gate, 1 = step on, 2 = step over.
            difficulty (int): The difficulty rating (1, 2, or 3).
        """
        self.gate_id = gate_id
        self.x = x
        self.z = z
        self.rotation = rotation
        self.type = type
        self.difficulty = difficulty

    def to_dict(self):
        """
        Converts the Gate object to a dictionary representation.
        
        Returns:
            dict: A dictionary containing gate properties.
        """
        return {
            "gate_id": self.gate_id,
            "x": self.x,
            "z": self.z,
            "rotation": self.rotation,
            "type": self.type,
            "difficulty": self.difficulty
        }


class LinkedListNode:
    def __init__(self, gate):
        """
        Initializes a node for use in a linked list.
        
        Parameters:
            gate (Gate): The gate object that this node will hold.
        """
        self.gate = gate
        self.next = None

class GateLinkedList:
    from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtGui import QPen

class GateLinkedList:
    def __init__(self):
        """
        Initializes an empty linked list to hold gate nodes.
        """
        self.head = None
        self.size = 0
        self.arrows = []  # Store QGraphicsLineItem objects for arrows

    def add_gate(self, gate):
        """
        Adds a gate to the end of the linked list.
        
        Parameters:
            gate (Gate): The gate to add.
        """
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
        """
        Inserts a gate at the specified index in the linked list.
        
        Parameters:
            index (int): The position at which to insert the gate.
            gate (Gate): The gate to insert.
        """
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
        """
        Removes a gate from the linked list at the specified index.
        
        Parameters:
            index (int): The index of the gate to remove.
        """
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
        """
        Changes the order of a gate by moving it from old_index to new_index.
        
        Parameters:
            old_index (int): The current index of the gate.
            new_index (int): The new index to move the gate to.
        """
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
        """
        Converts the linked list of gates to a list of dictionaries.
        
        Returns:
            list: A list of dictionaries representing each gate in the linked list.
        """
        gates = []
        current = self.head
        index = 0
        while current:
            gate_dict = current.gate.to_dict()
            gate_dict["gate_id"] = index  # Use numeric gate IDs; "start" and "end" will be added when saving
            gates.append(gate_dict)
            current = current.next
            index += 1
        return gates

    def print_linked_list(self):
        """
        Prints the linked list for debugging purposes.
        
        Returns:
            str: A string representation of the linked list.
        """
        current = self.head
        gates_info = []
        while current:
            gates_info.append(f"Gate {current.gate.gate_id} - x: {current.gate.x}, z: {current.gate.z}, rotation: {current.gate.rotation}")
            current = current.next
        return " -> ".join(gates_info)

import unittest
from gates import Gate, GateLinkedList

class TestGate(unittest.TestCase):
    def test_gate_initialization(self):
        gate = Gate(1, 100, 200, 45.0, 0, difficulty=2)
        self.assertEqual(gate.gate_id, 1)
        self.assertEqual(gate.x, 100)
        self.assertEqual(gate.z, 200)
        self.assertEqual(gate.rotation, 45.0)
        self.assertEqual(gate.type, 0)
        self.assertEqual(gate.difficulty, 2)

    def test_gate_to_dict(self):
        gate = Gate(2, 150, 250, 90.0, 1, difficulty=3)
        gate_dict = gate.to_dict()
        expected_dict = {
            "gate_id": 2,
            "x": 150,
            "z": 250,
            "rotation": 90.0,
            "type": 1,
            "difficulty": 3
        }
        self.assertEqual(gate_dict, expected_dict)

class TestGateLinkedList(unittest.TestCase):
    def setUp(self):
        self.gate_list = GateLinkedList()

    def test_add_gate(self):
        gate = Gate(1, 100, 200, 45.0, 0)
        self.gate_list.add_gate(gate)
        self.assertEqual(self.gate_list.size, 1)
        self.assertEqual(self.gate_list.head.gate, gate)

    def test_insert_gate(self):
        gate1 = Gate(1, 100, 200, 45.0, 0)
        gate2 = Gate(2, 150, 250, 90.0, 1)
        self.gate_list.add_gate(gate1)
        self.gate_list.insert_gate(0, gate2)
        self.assertEqual(self.gate_list.size, 2)
        self.assertEqual(self.gate_list.head.gate, gate2)
        self.assertEqual(self.gate_list.head.next.gate, gate1)

    def test_remove_gate(self):
        gate1 = Gate(1, 100, 200, 45.0, 0)
        gate2 = Gate(2, 150, 250, 90.0, 1)
        self.gate_list.add_gate(gate1)
        self.gate_list.add_gate(gate2)
        self.gate_list.remove_gate(0)
        self.assertEqual(self.gate_list.size, 1)
        self.assertEqual(self.gate_list.head.gate, gate2)

    def test_change_gate_order(self):
        gate1 = Gate(1, 100, 200, 45.0, 0)
        gate2 = Gate(2, 150, 250, 90.0, 1)
        gate3 = Gate(3, 200, 300, 135.0, 2)
        self.gate_list.add_gate(gate1)
        self.gate_list.add_gate(gate2)
        self.gate_list.add_gate(gate3)
        self.gate_list.change_gate_order(2, 0)
        self.assertEqual(self.gate_list.head.gate, gate3)
        self.assertEqual(self.gate_list.head.next.gate, gate1)
        self.assertEqual(self.gate_list.head.next.next.gate, gate2)

    def test_to_list(self):
        gate1 = Gate(1, 100, 200, 45.0, 0)
        gate2 = Gate(2, 150, 250, 90.0, 1)
        self.gate_list.add_gate(gate1)
        self.gate_list.add_gate(gate2)
        gate_list_dict = self.gate_list.to_list()
        expected_list = [
            {"gate_id": 0, "x": 100, "z": 200, "rotation": 45.0, "type": 0, "difficulty": 1},
            {"gate_id": 1, "x": 150, "z": 250, "rotation": 90.0, "type": 1, "difficulty": 1}
        ]
        self.assertEqual(gate_list_dict, expected_list)

if __name__ == "__main__":
    unittest.main()

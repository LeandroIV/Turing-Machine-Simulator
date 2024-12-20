import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class TuringMachine:
    def __init__(self, states, input_symbols, transitions, initial_state, accept_state, reject_state):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.current_state = initial_state
        self.tape = []
        self.head_position = 0
        self.accept_state = accept_state
        self.reject_state = reject_state

    def reset(self, input_string):
        self.tape = list(input_string)
        self.head_position = 0
        self.current_state = self.states[0]  # Start from the initial state

    def step(self):
        if self.head_position < 0 or self.head_position >= len(self.tape):
            return False  # Out of bounds

        current_symbol = self.tape[self.head_position]
        if (self.current_state, current_symbol) not in self.transitions:
            return False  # No transition defined

        new_state, new_symbol, direction = self.transitions[(self.current_state, current_symbol)]
        self.tape[self.head_position] = new_symbol
        self.current_state = new_state

        if direction == 'R':
            self.head_position += 1
        elif direction == 'L':
            self.head_position -= 1

        return True

    def is_accepting(self):
        return self.current_state == self.accept_state

    def is_rejecting(self):
        return self.current_state == self.reject_state


class TuringMachineSimulator:
    def __init__(self, master):
        self.master = master
        master.title("Turing Machine Simulator")
        master.geometry("900x650")
        master.configure(bg="#f0f0f0")

        # Initialize Turing Machine
        self.tm = None
        self.simulation_active = False

        # GUI Layout
        style = ttk.Style()
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        style.configure("TEntry", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10), padding=5)

        # Left Frame for Inputs
        left_frame = ttk.Frame(master)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(left_frame, text="States (comma-separated):").pack(pady=5)
        self.states_entry = ttk.Entry(left_frame, width=50)
        self.states_entry.pack(pady=5)

        ttk.Label(left_frame, text="Input Symbols (comma-separated):").pack(pady=5)
        self.input_symbols_entry = ttk.Entry(left_frame, width=50)
        self.input_symbols_entry.pack(pady=5)

        ttk.Label(left_frame, text="Initial State:").pack(pady=5)
        self.initial_state_entry = ttk.Entry(left_frame, width=50)
        self.initial_state_entry.pack(pady=5)

        ttk.Label(left_frame, text="Accept State:").pack(pady=5)
        self.accept_state_entry = ttk.Entry(left_frame, width=50)
        self.accept_state_entry.pack(pady=5)

        ttk.Label(left_frame, text="Reject State:").pack(pady=5)
        self.reject_state_entry = ttk.Entry(left_frame, width=50)
        self.reject_state_entry.pack(pady=5)

        ttk.Label(left_frame, text="Transitions (format: current_state,input_symbol,new_state,new_symbol,direction;"
                                   "\n separate by new lines): e.g. q0,a,q1,b,R").pack(pady=5)

        self.transitions_text = tk.Text(left_frame, height=10, width=50, font=("Helvetica", 10))
        self.transitions_text.pack(pady=5)

        ttk.Label(left_frame, text="Input String:").pack(pady=5)
        self.input_string_entry = ttk.Entry(left_frame, width=50)
        self.input_string_entry.pack(pady=5)

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=5)

        self.simulate_button = ttk.Button(button_frame, text="Start Simulation", command=self.start_simulation)
        self.simulate_button.pack(side=tk.LEFT, padx=5)

        self.step_button = ttk.Button(button_frame, text="Step", command=self.step_simulation, state=tk.DISABLED)
        self.step_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_simulation, state=tk.DISABLED)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.visualize_button = ttk.Button(button_frame, text="Visualize", command=self.visualize_tm)
        self.visualize_button.pack(side=tk.LEFT, padx=5)

        # Right Frame for Output
        right_frame = ttk.Frame(master)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Output:").pack(pady=5)
        self.output_text = tk.Text(right_frame, height=30, width=50, font=("Helvetica", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def parse_tm_description(self):
        # Parse states
        states = self.states_entry.get().split(',')
        if not states:
            raise ValueError("States cannot be empty")

        # Parse input symbols
        input_symbols = self.input_symbols_entry.get().split(',')
        if not input_symbols:
            raise ValueError("Input symbols cannot be empty")

        # Parse transitions
        transitions = {}
        transition_lines = self.transitions_text.get("1.0", tk.END).strip().split('\n')
        for line in transition_lines:
            parts = line.split(',')
            if len(parts) != 5:
                raise ValueError(f"Invalid transition format: {line}")
            current_state, input_symbol, new_state, new_symbol, direction = parts
            transitions[(current_state, input_symbol)] = (new_state, new_symbol, direction)

        # Parse initial, accept, and reject states
        initial_state = self.initial_state_entry.get()
        accept_state = self.accept_state_entry.get()
        reject_state = self.reject_state_entry.get()

        if not initial_state or not accept_state or not reject_state:
            raise ValueError("Initial, accept, and reject states must be specified")

        return states, input_symbols, transitions, initial_state, accept_state, reject_state

    def start_simulation(self):
        self.output_text.delete(1.0, tk.END)

        try:
            states, input_symbols, transitions, initial_state, accept_state, reject_state = self.parse_tm_description()
            input_string = self.input_string_entry.get()

            self.tm = TuringMachine(states, input_symbols, transitions, initial_state, accept_state, reject_state)
            self.tm.reset(input_string)

            self.simulation_active = True
            self.step_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.simulate_button.config(state=tk.DISABLED)

            self.output_text.insert(tk.END, "Simulation started. Press 'Step' to proceed.\n")
            self.output_text.insert(tk.END, f"Initial State: {self.tm.current_state}, Tape: {''.join(self.tm.tape)}, Head: {self.tm.head_position}\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def step_simulation(self):
        if not self.simulation_active or self.tm is None:
            return

        # Insert current simulation status into the output text widget
        self.output_text.insert(tk.END,
                                f"State: {self.tm.current_state}, Tape: {''.join(self.tm.tape)}, Head: {self.tm.head_position}\n")

        # Automatically scroll to the bottom of the text widget
        self.output_text.see(tk.END)  # Ensure the view is updated to the last inserted line

        # Check if the Turing Machine reaches accept or reject states
        if self.tm.is_accepting():
            self.output_text.insert(tk.END, "Accepted\n")
            self.simulation_active = False
            self.step_button.config(state=tk.DISABLED)
        elif self.tm.is_rejecting() or not self.tm.step():
            self.output_text.insert(tk.END, "Rejected\n")
            self.simulation_active = False
            self.step_button.config(state=tk.DISABLED)

        # Auto-scroll again to ensure the rejection/acceptance message is visible
        self.output_text.see(tk.END)

    def reset_simulation(self):
        self.simulation_active = False
        self.tm = None
        self.step_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.simulate_button.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Simulation reset. Enter new input or description to start again.\n")

    def visualize_tm(self):
        try:
            _, _, transitions, _, _, _ = self.parse_tm_description()

            graph = nx.MultiDiGraph()  # Use MultiDiGraph to support multiple edges

            # Group transitions by source and destination states
            edge_labels = {}
            for (current_state, input_symbol), (new_state, new_symbol, direction) in transitions.items():
                # Create a multi-edge
                graph.add_edge(current_state, new_state)

                # Accumulate labels for this edge
                if (current_state, new_state) not in edge_labels:
                    edge_labels[(current_state, new_state)] = []

                # Add the transition details to the labels
                label = f"{input_symbol}/{new_symbol},{direction}"
                edge_labels[(current_state, new_state)].append(label)

            def show_visualization():
                visualization_window = Toplevel(self.master)
                visualization_window.title("Turing Machine Visualization")

                plt.figure(figsize=(10, 8))
                pos = nx.spring_layout(graph, k=0.9)  # Increased spacing

                # Draw nodes
                nx.draw_networkx_nodes(graph, pos, node_size=3000, node_color='lightblue')
                nx.draw_networkx_labels(graph, pos, font_size=10, font_weight='bold')

                # Draw edges with proper arrows for all types of edges
                for (src, dest) in graph.edges():
                    if src == dest:
                        # Self-loop with arrow
                        nx.draw_networkx_edges(graph, pos,
                                               edgelist=[(src, dest)],
                                               connectionstyle='arc3,rad=0.5',  # More pronounced loop
                                               arrows=True,
                                               arrowsize=20)
                    else:
                        # Regular edges with multiple possible routes
                        nx.draw_networkx_edges(graph, pos,
                                               edgelist=[(src, dest)],
                                               connectionstyle='arc3,rad=0.1',
                                               # Slight curve to distinguish multiple edges
                                               arrows=True,
                                               arrowsize=70)

                # Custom edge label placement
                for (src, dest), labels in edge_labels.items():
                    # Stack multiple labels vertically
                    label_text = '\n'.join(labels)

                    # Handle self-loops differently
                    if src == dest:
                        # Position label above the node
                        node_pos = pos[src]
                        plt.text(node_pos[0], node_pos[1] + 0.2, label_text,
                                 fontsize=8,
                                 bbox=dict(facecolor='white', edgecolor='lightgray', alpha=0.7),
                                 horizontalalignment='center', verticalalignment='bottom')
                    else:
                        # For regular edges, use midpoint
                        x = (pos[src][0] + pos[dest][0]) / 2
                        y = (pos[src][1] + pos[dest][1]) / 2
                        plt.text(x, y, label_text, fontsize=8,
                                 bbox=dict(facecolor='white', edgecolor='lightgray', alpha=0.7),
                                 horizontalalignment='center', verticalalignment='center')

                plt.title("Turing Machine Visualization")
                plt.axis('off')  # Hide axis

                canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_window)
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                canvas.draw()

            show_visualization()

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = TuringMachineSimulator(root)
    root.mainloop()

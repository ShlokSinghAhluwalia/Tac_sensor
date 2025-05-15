# PyQt5 version of the original tactile GUI
import sys
import numpy as np
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QLabel, QGridLayout, QScrollArea
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import threading

# Serial config
PORT = "/dev/cu.usbserial-0001"
BAUD_RATE = 115200
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

ROWS = 16
COLS = 4
sensor_data = np.zeros((ROWS, COLS))
selected_row = [0]  # Mutable container for callback

class TactileGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tactile Sensor Dashboard")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Plot section
        self.canvas = FigureCanvas(Figure(figsize=(8, 6)))
        main_layout.addWidget(self.canvas, stretch=4)

        self.ax_heatmap = self.canvas.figure.add_subplot(211)
        self.ax_plot = self.canvas.figure.add_subplot(212)

        self.heatmap = self.ax_heatmap.imshow(sensor_data, cmap='plasma', vmin=0, vmax=30000, aspect='auto')
        self.canvas.figure.colorbar(self.heatmap, ax=self.ax_heatmap)
        self.ax_heatmap.set_title("Tactile Sensor Heatmap")
        self.ax_heatmap.set_xlabel("Columns")
        self.ax_heatmap.set_ylabel("Rows")

        self.text_vals = [[self.ax_heatmap.text(j, i, '', ha='center', va='center', fontsize=6, color='white')
                           for j in range(COLS)] for i in range(ROWS)]

        self.line_plot, = self.ax_plot.plot(np.arange(COLS), sensor_data[selected_row[0]], marker='o', color='orange')
        self.ax_plot.set_ylim(0, 30000)
        self.ax_plot.set_title(f"Live Data - Row 0")
        self.ax_plot.set_xlabel("Columns")
        self.ax_plot.set_ylabel("Sensor Value")
        self.ax_plot.grid(True)

        # Row selection section
        side_panel = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)

        for i in range(ROWS):
            btn = QPushButton(f"Row {i}")
            btn.clicked.connect(lambda _, x=i: self.select_row(x))
            scroll_layout.addWidget(btn, i // 2, i % 2)

        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        side_panel.addWidget(scroll_area)
        main_layout.addLayout(side_panel, stretch=1)

        # Start update loop
        self.update_timer()

    def select_row(self, row):
        selected_row[0] = row
        self.ax_plot.set_title(f"Live Data - Row {row}")

    def update_timer(self):
        self.update_data()
        self.canvas.draw()
        threading.Timer(0.1, self.update_timer).start()

    def update_data(self):
        global sensor_data
        row_count = 0
        while row_count < ROWS:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith("Row"):
                    parts = line.split(":")
                    if len(parts) == 2:
                        row_index = int(parts[0].split()[1])
                        values = list(map(int, parts[1].strip().split()))
                        if len(values) == COLS:
                            sensor_data[row_index] = values
                            row_count += 1
            except Exception as e:
                print(f"Error: {e}")
                continue

        self.heatmap.set_data(sensor_data)
        for i in range(ROWS):
            for j in range(COLS):
                self.text_vals[i][j].set_text(str(sensor_data[i, j]))

        current_row = selected_row[0]
        self.line_plot.set_ydata(sensor_data[current_row])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TactileGUI()
    window.show()
    sys.exit(app.exec_())

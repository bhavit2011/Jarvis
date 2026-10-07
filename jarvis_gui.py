import sys
import time
from collections import deque
from datetime import datetime

import cv2
import psutil

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QImage
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)


# ============================================================
# COLORS
# ============================================================

BG = "#031018"
PANEL = "#071D27"
PANEL_2 = "#0B2632"
CYAN = "#19D8F7"
CYAN_LIGHT = "#72F1FF"
GREEN = "#40F0A8"
ORANGE = "#FF9E32"
RED = "#FF5365"
TEXT = "#E9FBFF"
MUTED = "#6E9BA8"
GRID = "#113844"


# ============================================================
# MINI GRAPH
# ============================================================

class MiniGraph(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.values = deque(
            [0.0] * 50,
            maxlen=50
        )

        self.setMinimumHeight(70)

    def add_value(self, value):
        self.values.append(float(value))
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(
            self.rect(),
            QColor("#05171F")
        )

        w = self.width()
        h = self.height()

        # Grid
        pen = QPen(QColor(GRID), 1)
        painter.setPen(pen)

        for i in range(1, 5):
            y = int(h * i / 5)
            painter.drawLine(0, y, w, y)

        for i in range(1, 7):
            x = int(w * i / 7)
            painter.drawLine(x, 0, x, h)

        if len(self.values) < 2:
            return

        maximum = max(max(self.values), 1)

        points = []

        for i, value in enumerate(self.values):

            x = i * w / (len(self.values) - 1)

            y = h - (
                (value / maximum) * (h - 10)
            ) - 5

            points.append(
                (x, y)
            )

        painter.setPen(
            QPen(
                QColor(CYAN),
                2
            )
        )

        for i in range(1, len(points)):

            x1, y1 = points[i - 1]
            x2, y2 = points[i]

            painter.drawLine(
                int(x1),
                int(y1),
                int(x2),
                int(y2)
            )


# ============================================================
# RING
# ============================================================

class UsageRing(QWidget):

    def __init__(
        self,
        title,
        color=CYAN,
        parent=None
    ):
        super().__init__(parent)

        self.title = title
        self.color = color
        self.value = 0

        self.setMinimumSize(150, 150)

    def set_value(self, value):

        self.value = max(
            0,
            min(100, int(value))
        )

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        size = min(
            self.width(),
            self.height()
        )

        cx = self.width() / 2
        cy = self.height() / 2

        radius = size * 0.37

        # Background ring
        painter.setPen(
            QPen(
                QColor("#153F4C"),
                10
            )
        )

        painter.drawEllipse(
            QRectF(
                cx - radius,
                cy - radius,
                radius * 2,
                radius * 2
            )
        )

        # Active ring
        painter.setPen(
            QPen(
                QColor(self.color),
                10
            )
        )

        painter.drawArc(
            QRectF(
                cx - radius,
                cy - radius,
                radius * 2,
                radius * 2
            ),
            90 * 16,
            -int(
                self.value * 3.6
            ) * 16
        )

        # Inner circle
        inner = radius * 0.68

        painter.setPen(Qt.NoPen)
        painter.setBrush(
            QBrush(
                QColor("#09242F")
            )
        )

        painter.drawEllipse(
            QRectF(
                cx - inner,
                cy - inner,
                inner * 2,
                inner * 2
            )
        )

        # Title
        painter.setPen(
            QColor(TEXT)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                9
            )
        )

        painter.drawText(
            QRectF(
                cx - 65,
                cy - 35,
                130,
                25
            ),
            Qt.AlignCenter,
            self.title
        )

        # Number
        painter.setPen(
            QColor(self.color)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                25,
                QFont.Bold
            )
        )

        painter.drawText(
            QRectF(
                cx - 65,
                cy - 2,
                130,
                42
            ),
            Qt.AlignCenter,
            f"{self.value}%"
        )


# ============================================================
# PANEL
# ============================================================

class Panel(QFrame):

    def __init__(
        self,
        title,
        parent=None
    ):
        super().__init__(parent)

        self.setObjectName(
            "panel"
        )

        self.layout = QVBoxLayout(
            self
        )

        self.layout.setContentsMargins(
            12, 10, 12, 10
        )

        self.layout.setSpacing(7)

        header = QHBoxLayout()

        label = QLabel(
            title.upper()
        )

        label.setObjectName(
            "panelTitle"
        )

        header.addWidget(label)
        header.addStretch()

        close = QLabel("×")
        close.setObjectName(
            "panelClose"
        )

        header.addWidget(close)

        self.layout.addLayout(
            header
        )


# ============================================================
# CAMERA
# ============================================================

class CameraPanel(Panel):

    def __init__(self):
        super().__init__("LIVE CAMERA")

        self.preview = QLabel(
            "CAMERA STARTING..."
        )

        self.preview.setAlignment(
            Qt.AlignCenter
        )

        self.preview.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.preview.setMinimumHeight(220)

        self.preview.setStyleSheet(
            """
            background:#03151D;
            border:1px solid #155465;
            """
        )

        self.status = QLabel(
            "● STARTING"
        )

        self.status.setStyleSheet(
            f"""
            color:{ORANGE};
            font-weight:bold;
            """
        )

        self.layout.addWidget(
            self.preview,
            1
        )

        self.layout.addWidget(
            self.status
        )

        # Windows DirectShow
        self.cap = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )

        # Fallback
        if not self.cap.isOpened():
            self.cap.release()
            self.cap = cv2.VideoCapture(0)

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_camera
        )

        self.timer.start(30)

    def update_camera(self):

        if not self.cap.isOpened():

            self.preview.setText(
                "CAMERA OFFLINE"
            )

            self.status.setText(
                "● CAMERA OFFLINE"
            )

            self.status.setStyleSheet(
                f"""
                color:{RED};
                font-weight:bold;
                """
            )

            return

        ok, frame = self.cap.read()

        if not ok:
            return

        frame = cv2.flip(
            frame,
            1
        )

        h, w = frame.shape[:2]

        # HUD
        cv2.rectangle(
            frame,
            (6, 6),
            (w - 6, h - 6),
            (25, 216, 247),
            2
        )

        cv2.putText(
            frame,
            "JARVIS LIVE",
            (16, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (25, 216, 247),
            2
        )

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        h, w, channels = rgb.shape

        image = QImage(
            rgb.data,
            w,
            h,
            channels * w,
            QImage.Format_RGB888
        ).copy()

        pixmap = image.scaled(
            self.preview.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.preview.setPixmap(
            pixmap
        )

        self.status.setText(
            "● CAMERA ONLINE"
        )

        self.status.setStyleSheet(
            f"""
            color:{GREEN};
            font-weight:bold;
            """
        )

    def close_camera(self):

        if hasattr(self, "timer"):
            self.timer.stop()

        if self.cap:
            self.cap.release()


# ============================================================
# MAIN WINDOW
# ============================================================

class JarvisOS(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "JARVIS OS"
        )

        self.resize(
            1400,
            820
        )

        self.setMinimumSize(
            1180,
            700
        )

        self.last_net = (
            psutil.net_io_counters()
        )

        self.last_net_time = time.time()

        self.build_ui()

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.refresh_system
        )

        self.timer.start(1000)

        self.refresh_system()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        central = QWidget()

        central.setObjectName(
            "root"
        )

        self.setCentralWidget(
            central
        )

        root = QVBoxLayout(
            central
        )

        root.setContentsMargins(
            14, 10, 14, 10
        )

        root.setSpacing(8)

        # ====================================================
        # TOP BAR
        # ====================================================

        top = QHBoxLayout()

        title = QLabel(
            "▣  JARVIS OS"
        )

        title.setObjectName(
            "appTitle"
        )

        top.addWidget(
            title
        )

        top.addStretch()

        self.clock = QLabel(
            ""
        )

        self.clock.setObjectName(
            "clock"
        )

        top.addWidget(
            self.clock
        )

        root.addLayout(
            top
        )

        # ====================================================
        # MAIN GRID
        # ====================================================

        grid = QGridLayout()

        grid.setSpacing(
            10
        )

        # ----------------------------------------------------
        # CPU PANEL
        # ----------------------------------------------------

        cpu_panel = Panel(
            "CPU STATUS"
        )

        cpu_top = QHBoxLayout()

        self.cpu_ring = UsageRing(
            "CPU USAGE"
        )

        cpu_top.addWidget(
            self.cpu_ring,
            0
        )

        cores_box = QVBoxLayout()

        self.core_bars = []

        core_count = (
            psutil.cpu_count(
                logical=True
            ) or 1
        )

        for i in range(
            core_count
        ):

            row = QHBoxLayout()

            label = QLabel(
                f"CORE {i + 1}"
            )

            label.setFixedWidth(
                52
            )

            bar = QProgressBar()

            bar.setRange(
                0,
                100
            )

            bar.setTextVisible(
                False
            )

            bar.setFixedHeight(
                9
            )

            row.addWidget(
                label
            )

            row.addWidget(
                bar
            )

            cores_box.addLayout(
                row
            )

            self.core_bars.append(
                bar
            )

        cpu_top.addLayout(
            cores_box,
            1
        )

        cpu_panel.layout.addLayout(
            cpu_top
        )

        self.cpu_graph = MiniGraph()

        cpu_panel.layout.addWidget(
            self.cpu_graph
        )

        grid.addWidget(
            cpu_panel,
            0,
            0,
            2,
            4
        )

        # ----------------------------------------------------
        # JARVIS CORE
        # ----------------------------------------------------

        core_panel = Panel(
            "JARVIS CORE"
        )

        core_panel.layout.addStretch()

        logo = QLabel(
            "JARVIS"
        )

        logo.setAlignment(
            Qt.AlignCenter
        )

        logo.setStyleSheet(
            f"""
            color:{CYAN};
            font-size:40px;
            font-weight:bold;
            letter-spacing:6px;
            """
        )

        core_panel.layout.addWidget(
            logo
        )

        reactor = QLabel(
            "◈"
        )

        reactor.setAlignment(
            Qt.AlignCenter
        )

        reactor.setStyleSheet(
            f"""
            color:{CYAN_LIGHT};
            font-size:72px;
            """
        )

        core_panel.layout.addWidget(
            reactor
        )

        self.jarvis_status = QLabel(
            "● ONLINE"
        )

        self.jarvis_status.setAlignment(
            Qt.AlignCenter
        )

        self.jarvis_status.setStyleSheet(
            f"""
            color:{GREEN};
            font-size:15px;
            font-weight:bold;
            """
        )

        core_panel.layout.addWidget(
            self.jarvis_status
        )

        self.message = QLabel(
            "SYSTEM READY\n"
            "Awaiting command..."
        )

        self.message.setAlignment(
            Qt.AlignCenter
        )

        self.message.setStyleSheet(
            f"""
            color:{MUTED};
            font-size:11px;
            """
        )

        core_panel.layout.addWidget(
            self.message
        )

        core_panel.layout.addStretch()

        grid.addWidget(
            core_panel,
            0,
            4,
            2,
            3
        )

        # ----------------------------------------------------
        # RAM
        # ----------------------------------------------------

        ram_panel = Panel(
            "RAM & MEMORY"
        )

        self.ram_ring = UsageRing(
            "RAM USED",
            ORANGE
        )

        ram_panel.layout.addWidget(
            self.ram_ring,
            1
        )

        self.ram_text = QLabel(
            "0 GB / 0 GB"
        )

        self.ram_text.setAlignment(
            Qt.AlignCenter
        )

        self.ram_text.setStyleSheet(
            f"""
            color:{TEXT};
            font-size:13px;
            """
        )

        ram_panel.layout.addWidget(
            self.ram_text
        )

        grid.addWidget(
            ram_panel,
            0,
            7,
            2,
            2
        )

        # ----------------------------------------------------
        # PROCESS MANAGER
        # ----------------------------------------------------

        process_panel = Panel(
            "PROCESS MANAGER"
        )

        self.process_table = QTableWidget(
            0,
            4
        )

        self.process_table.setHorizontalHeaderLabels(
            [
                "PROCESS",
                "PID",
                "CPU %",
                "RAM %"
            ]
        )

        # Hide row numbers
        self.process_table.verticalHeader().setVisible(
            False
        )

        header = self.process_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        self.process_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        process_panel.layout.addWidget(
            self.process_table
        )

        grid.addWidget(
            process_panel,
            0,
            9,
            4,
            3
        )

        # ----------------------------------------------------
        # NETWORK
        # ----------------------------------------------------

        network_panel = Panel(
            "NETWORK TRAFFIC"
        )

        net_row = QHBoxLayout()

        self.upload_label = QLabel(
            "▲ UP: 0 KB/s"
        )

        self.download_label = QLabel(
            "▼ DOWN: 0 KB/s"
        )

        net_row.addWidget(
            self.upload_label
        )

        net_row.addStretch()

        net_row.addWidget(
            self.download_label
        )

        network_panel.layout.addLayout(
            net_row
        )

        self.network_graph = MiniGraph()

        network_panel.layout.addWidget(
            self.network_graph
        )

        grid.addWidget(
            network_panel,
            2,
            0,
            2,
            4
        )

        # ----------------------------------------------------
        # SYSTEM
        # ----------------------------------------------------

        system_panel = Panel(
            "SYSTEM STATUS"
        )

        self.system_label = QLabel(
            "CPU TEMP: N/A\n"
            "GPU TEMP: N/A\n"
            "BATTERY: N/A"
        )

        self.system_label.setStyleSheet(
            f"""
            color:{TEXT};
            font-size:14px;
            """
        )

        system_panel.layout.addWidget(
            self.system_label
        )

        grid.addWidget(
            system_panel,
            2,
            4,
            2,
            3
        )

        # ----------------------------------------------------
        # STORAGE
        # ----------------------------------------------------

        storage_panel = Panel(
            "STORAGE"
        )

        self.storage_label = QLabel(
            "C: 0% USED"
        )

        storage_panel.layout.addWidget(
            self.storage_label
        )

        self.storage_bar = QProgressBar()

        self.storage_bar.setRange(
            0,
            100
        )

        self.storage_bar.setTextVisible(
            False
        )

        storage_panel.layout.addWidget(
            self.storage_bar
        )

        grid.addWidget(
            storage_panel,
            2,
            7,
            2,
            2
        )

        # ----------------------------------------------------
        # CAMERA
        # ----------------------------------------------------

        self.camera_panel = CameraPanel()

        grid.addWidget(
            self.camera_panel,
            4,
            9,
            3,
            3
        )

        # ----------------------------------------------------
        # SYSTEM INFO
        # ----------------------------------------------------

        info_panel = Panel(
            "SYSTEM INFORMATION"
        )

        info_layout = QGridLayout()

        self.info1 = QLabel()
        self.info2 = QLabel()
        self.info3 = QLabel()
        self.info4 = QLabel()

        for label in [
            self.info1,
            self.info2,
            self.info3,
            self.info4
        ]:

            label.setStyleSheet(
                f"""
                color:{MUTED};
                font-size:12px;
                """
            )

        info_layout.addWidget(
            self.info1,
            0,
            0
        )

        info_layout.addWidget(
            self.info2,
            1,
            0
        )

        info_layout.addWidget(
            self.info3,
            0,
            1
        )

        info_layout.addWidget(
            self.info4,
            1,
            1
        )

        info_panel.layout.addLayout(
            info_layout
        )

        grid.addWidget(
            info_panel,
            4,
            0,
            3,
            9
        )

        # Let columns resize sensibly
        for col in range(12):
            grid.setColumnStretch(
                col,
                1
            )

        # Camera gets more space
        grid.setColumnStretch(
            9,
            2
        )

        root.addLayout(
            grid,
            1
        )

        # ====================================================
        # BOTTOM DOCK
        # ====================================================

        dock = QHBoxLayout()

        for name in [
            "⚙ SETTINGS",
            "▣ FILES",
            "⚒ TOOLS",
            "〉 TERMINAL"
        ]:

            btn = QPushButton(
                name
            )

            btn.setMinimumHeight(
                38
            )

            dock.addWidget(
                btn
            )

        dock.addStretch()

        listen_btn = QPushButton(
            "◉ LISTEN"
        )

        listen_btn.clicked.connect(
            self.listen
        )

        dock.addWidget(
            listen_btn
        )

        sleep_btn = QPushButton(
            "◐ SLEEP"
        )

        sleep_btn.clicked.connect(
            self.sleep
        )

        dock.addWidget(
            sleep_btn
        )

        exit_btn = QPushButton(
            "EXIT"
        )

        exit_btn.clicked.connect(
            self.close
        )

        dock.addWidget(
            exit_btn
        )

        root.addLayout(
            dock
        )

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh_system(self):

        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        self.clock.setText(
            datetime.now().strftime(
                "%H:%M:%S  |  %A %d %b %Y"
            )
        )

        # ----------------------------------------------------
        # CPU
        # ----------------------------------------------------

        cpu = psutil.cpu_percent()

        self.cpu_ring.set_value(
            cpu
        )

        self.cpu_graph.add_value(
            cpu
        )

        cores = psutil.cpu_percent(
            percpu=True
        )

        for i, value in enumerate(
            cores
        ):

            if i < len(
                self.core_bars
            ):

                self.core_bars[i].setValue(
                    int(value)
                )

        # ----------------------------------------------------
        # RAM
        # ----------------------------------------------------

        ram = psutil.virtual_memory()

        self.ram_ring.set_value(
            ram.percent
        )

        used = ram.used / (
            1024 ** 3
        )

        total = ram.total / (
            1024 ** 3
        )

        self.ram_text.setText(
            f"{used:.1f} GB / "
            f"{total:.1f} GB"
        )

        # ----------------------------------------------------
        # STORAGE
        # ----------------------------------------------------

        try:

            disk = psutil.disk_usage(
                "C:\\"
            )

            self.storage_bar.setValue(
                int(disk.percent)
            )

            free = disk.free / (
                1024 ** 3
            )

            self.storage_label.setText(
                f"C: {disk.percent:.0f}% USED  |  "
                f"FREE: {free:.1f} GB"
            )

        except Exception:

            pass

        # ----------------------------------------------------
        # NETWORK
        # ----------------------------------------------------

        now = time.time()

        network = (
            psutil.net_io_counters()
        )

        elapsed = max(
            now -
            self.last_net_time,
            0.001
        )

        upload = (
            network.bytes_sent -
            self.last_net.bytes_sent
        ) / elapsed

        download = (
            network.bytes_recv -
            self.last_net.bytes_recv
        ) / elapsed

        self.last_net = network
        self.last_net_time = now

        upload_kb = upload / 1024
        download_kb = download / 1024

        self.upload_label.setText(
            f"▲ UP: {upload_kb:.1f} KB/s"
        )

        self.download_label.setText(
            f"▼ DOWN: {download_kb:.1f} KB/s"
        )

        self.network_graph.add_value(
            min(
                100,
                (upload_kb +
                 download_kb) / 30
            )
        )

        # ----------------------------------------------------
        # BATTERY
        # ----------------------------------------------------

        battery = (
            psutil.sensors_battery()
        )

        if battery:

            battery_text = (
                f"{battery.percent:.0f}%"
            )

        else:

            battery_text = "N/A"

        self.system_label.setText(
            f"CPU TEMP: N/A\n"
            f"GPU TEMP: N/A\n"
            f"BATTERY: {battery_text}"
        )

        # ----------------------------------------------------
        # PROCESSES
        # ----------------------------------------------------

        self.update_processes()

        # ----------------------------------------------------
        # INFO
        # ----------------------------------------------------

        physical = (
            psutil.cpu_count(
                logical=False
            ) or 0
        )

        logical = (
            psutil.cpu_count(
                logical=True
            ) or 0
        )

        self.info1.setText(
            f"CPU: {physical} physical / {logical} logical"
        )

        self.info2.setText(
            f"RAM: {total:.1f} GB"
        )

        self.info3.setText(
            "JARVIS GUI: ONLINE"
        )

        self.info4.setText(
            "CAMERA: ONLINE"
        )

    # ========================================================
    # PROCESS TABLE
    # ========================================================

    def update_processes(self):

        processes = []

        for proc in psutil.process_iter(
            [
                "name",
                "pid",
                "cpu_percent",
                "memory_percent"
            ]
        ):

            try:

                info = proc.info

                processes.append(
                    (
                        info["name"] or "Unknown",
                        info["pid"],
                        info["cpu_percent"] or 0,
                        info["memory_percent"] or 0
                    )
                )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied
            ):

                continue

        processes.sort(
            key=lambda x: x[2],
            reverse=True
        )

        processes = processes[:25]

        self.process_table.setRowCount(
            len(processes)
        )

        for row, item in enumerate(
            processes
        ):

            name, pid, cpu, ram = item

            data = [
                str(name),
                str(pid),
                f"{cpu:.1f}",
                f"{ram:.1f}"
            ]

            for col, value in enumerate(
                data
            ):

                self.process_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(
                        value
                    )
                )

    # ========================================================
    # BUTTONS
    # ========================================================

    def listen(self):

        self.jarvis_status.setText(
            "● LISTENING"
        )

        self.jarvis_status.setStyleSheet(
            f"""
            color:{CYAN};
            font-size:15px;
            font-weight:bold;
            """
        )

        self.message.setText(
            "Listening for your command..."
        )

    def sleep(self):

        self.jarvis_status.setText(
            "● SLEEPING"
        )

        self.jarvis_status.setStyleSheet(
            f"""
            color:{ORANGE};
            font-size:15px;
            font-weight:bold;
            """
        )

        self.message.setText(
            "Jarvis is sleeping.\n"
            "Say 'Hey Jarvis' to wake."
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def closeEvent(self, event):

        self.camera_panel.close_camera()

        event.accept()


# ============================================================
# STYLE
# ============================================================

STYLE = f"""
QMainWindow {{
    background:{BG};
}}

QWidget#root {{
    background:{BG};
}}

QLabel {{
    color:{TEXT};
    font-family:"Segoe UI";
}}

QLabel#appTitle {{
    color:{CYAN};
    font-size:18px;
    font-weight:bold;
}}

QLabel#clock {{
    color:{MUTED};
    font-size:12px;
}}

QFrame#panel {{
    background:{PANEL};
    border:1px solid #155364;
    border-radius:8px;
}}

QLabel#panelTitle {{
    color:{TEXT};
    font-size:13px;
    font-weight:bold;
}}

QLabel#panelClose {{
    color:{MUTED};
    font-size:17px;
}}

QPushButton {{
    background:{PANEL_2};
    color:{CYAN_LIGHT};
    border:1px solid #1B6172;
    border-radius:6px;
    padding:7px 14px;
    font-weight:bold;
}}

QPushButton:hover {{
    background:#123D4B;
    border:1px solid {CYAN};
}}

QProgressBar {{
    background:#061820;
    border:1px solid #164854;
    border-radius:4px;
}}

QProgressBar::chunk {{
    background:{CYAN};
    border-radius:4px;
}}

QTableWidget {{
    background:#06171F;
    alternate-background-color:#09222C;
    color:{TEXT};
    gridline-color:#123743;
    border:1px solid #164A58;
}}

QHeaderView::section {{
    background:#0D3441;
    color:{CYAN_LIGHT};
    border:none;
    padding:6px;
    font-weight:bold;
}}
"""


# ============================================================
# START
# ============================================================

def main():

    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    app.setStyleSheet(
        STYLE
    )

    window = JarvisOS()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
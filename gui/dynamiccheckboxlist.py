from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QFrame, QGridLayout, QCheckBox


class DynamicCheckBoxList(QFrame):
    selected_changed = pyqtSignal(list)

    def __init__(self, item_list: list[str], parent=None):
        super().__init__(parent)
        self.checkboxes = []

        self.setFrameStyle(QFrame.Panel)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(1)

        if item_list:
            for item in item_list:
                self.add_checkbox(item)
            self.update_columns()

        self.setLayout(self.grid_layout)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.update_columns)

    def add_checkbox(self, text):
        """CAUTION: Checkbox added after init will only show after resizing."""

        checkbox = QCheckBox(text)
        self.checkboxes.append(checkbox)
        checkbox.stateChanged.connect(lambda: self.selected_changed.emit(self.selected_texts()))

    def update_columns(self):
        if not self.checkboxes:
            return
        # Calculate the number of columns based on the available width
        available_width = self.width()
        checkbox_width = max([cb.sizeHint().width() for cb in self.checkboxes])
        num_columns = available_width // checkbox_width

        # Adjust the grid layout to use the correct number of columns
        self.grid_layout.setColumnStretch(num_columns, 1)
        self.grid_layout.setHorizontalSpacing(1)
        self.grid_layout.setVerticalSpacing(1)
        for i, checkbox in enumerate(self.checkboxes):
            self.grid_layout.addWidget(checkbox, i // num_columns, i % num_columns)

        self.setFixedHeight(self.sizeHint().height())

    def resizeEvent(self, event):
        self.timer.start(50)
        if not self.timer.isActive():
            self.timer.stop()
            self.update_columns()

    def selected_texts(self) -> list[str]:
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

from collections.abc import Iterable
from dataclasses import dataclass

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QAbstractItemView, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,\
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget


@dataclass
class TwoListSelectionData:
    """Class contains information about TwoListSelection items."""

    key: str
    text: str
    tooltip: str

    def __init__(self, key, text: str = None, tooltip: str = None):
        self.key = key
        self.text = text or str(key)
        self.tooltip = tooltip or str(key)


class TwoListSelection(QWidget):
    right_count_changed = pyqtSignal(int)
    right_list_changed = pyqtSignal(dict)

    def __init__(
            self,
            left_list: list = None,
            right_key_list: list = None,
            fixed_right_key_list: list = None,
            left_caption: str = "",
            right_caption: str = "",
            font_size=8,
            clone=False,
            allow_sorting=True,
            allow_filtering=False,
            parent=None
    ):
        super().__init__(parent)

        self.__clone = clone

        self.__left_list = left_list
        self.__right_list = right_key_list
        self.__fixed_list = fixed_right_key_list if isinstance(fixed_right_key_list, Iterable) else []

        # Filter options
        self.filter_by_key = True
        self.filter_by_tooltip = True

        # Widgets
        # Left
        self.__left_caption = QLabel(left_caption)
        self.left_list_widget = QListWidget()
        self.left_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.left_list_widget.setSortingEnabled(True)
        # Filter
        self.__filter_widget = QLineEdit()
        self.__filter_widget.setClearButtonEnabled(True)
        self.__filter_widget.textEdited.connect(self.__filter_edited)

        # Right
        self.__right_caption = QLabel(right_caption)
        self.right_list_widget = QListWidget()
        self.right_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.__button_all_to_right = QPushButton(">>")
        self.__button_all_to_right.setToolTip(self.tr("Move all to the right"))
        self.__button_selected_to_right = QPushButton(">")
        self.__button_selected_to_right.setToolTip(self.tr("Move selected to the right"))
        self.__button_selected_to_left = QPushButton("<")
        self.__button_selected_to_left.setToolTip(self.tr("Move selected to the left"))
        self.__button_all_to_left = QPushButton("<<")
        self.__button_all_to_left.setToolTip(self.tr("Move all to the left"))

        self.__button_up = QPushButton(self.tr("Up"))
        self.__button_up.setToolTip(self.tr("Move selection up"))
        self.__button_down = QPushButton(self.tr("Down"))
        self.__button_down.setToolTip(self.tr("Move selection down"))

        # Font size
        font = self.__left_caption.font()
        font.setPointSize(font_size)
        self.__left_caption.setFont(font)
        self.__right_caption.setFont(font)
        self.__button_all_to_right.setFont(font)
        self.__button_selected_to_right.setFont(font)
        self.__button_selected_to_left.setFont(font)
        self.__button_all_to_left.setFont(font)
        self.__button_up.setFont(font)
        self.__button_down.setFont(font)

        # Layouts
        self.__layout = QHBoxLayout(self)

        # Left list
        self.__left_list_layout = QVBoxLayout()
        self.__left_list_layout.addWidget(self.__left_caption)
        if allow_filtering:
            self.__left_list_layout.addWidget(self.__filter_widget)
        self.__left_list_layout.addWidget(self.left_list_widget)

        self.__layout.addLayout(self.__left_list_layout)

        # Middle buttons
        self.__middle_button_layout = QVBoxLayout()
        self.__middle_button_layout.addItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.__middle_button_layout.addWidget(self.__button_all_to_right)
        self.__middle_button_layout.addWidget(self.__button_selected_to_right)
        self.__middle_button_layout.addWidget(self.__button_selected_to_left)
        self.__middle_button_layout.addWidget(self.__button_all_to_left)
        self.__middle_button_layout.addItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.__layout.addLayout(self.__middle_button_layout)

        # Right list
        self.__right_list_layout = QVBoxLayout()
        self.__right_list_layout.addWidget(self.__right_caption)
        self.__right_list_layout.addWidget(self.right_list_widget)

        self.__layout.addLayout(self.__right_list_layout)

        # Right buttons
        if allow_sorting:
            self.__right_button_layout = QVBoxLayout()
            self.__right_button_layout.addItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
            self.__right_button_layout.addWidget(self.__button_up)
            self.__right_button_layout.addWidget(self.__button_down)
            self.__right_button_layout.addItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

            self.__layout.addLayout(self.__right_button_layout)

        self.__populate_list_widgets()
        self.__set_button_status()
        self.__connect()

    def __filter_edited(self, text: str):
        for i in range(0, self.left_list_widget.count()):
            item = self.left_list_widget.item(i)
            if not text:
                item.setHidden(False)
            elif text.casefold() not in item.text().casefold():
                item.setHidden(True)
                if self.filter_by_key and text.casefold() in str(item.data(Qt.UserRole)).casefold() \
                        or self.filter_by_tooltip and text.casefold() in item.toolTip().casefold():
                    item.setHidden(False)
            else:
                item.setHidden(False)

    def get_right_dict(self) -> dict:
        result = {}
        items = [self.right_list_widget.item(i) for i in range(self.right_list_widget.count())]

        for item in items:
            result[item.data(Qt.UserRole)] = item.data(Qt.DisplayRole)

        return result

    def __populate_list_widgets(self):
        for e in self.__left_list:
            if not isinstance(e, TwoListSelectionData):
                element = TwoListSelectionData(e)
            else:
                element = e

            item = QListWidgetItem()
            item.setData(Qt.DisplayRole, element.text)
            item.setData(Qt.ToolTipRole, element.tooltip)
            item.setData(Qt.UserRole, element.key)

            # Format fixed item
            if element.key in self.__fixed_list:
                font = QFont()
                font.setBold(True)
                item.setFont(font)

            self.left_list_widget.addItem(item)

        if self.__right_list or self.__fixed_list:
            self.__clone_to_right(init=True)
            self.right_list_widget.setCurrentRow(-1)

    def __set_button_status(self):
        self.__button_up.setDisabled(
            self.right_list_widget.count() < 1
            or (self.right_list_widget.currentRow() in (-1, 0) and len(self.right_list_widget.selectedItems()) == 1)
            or len(self.right_list_widget.selectedItems()) == 0
        )

        self.__button_down.setDisabled(
            self.right_list_widget.count() < 1
            or (self.right_list_widget.currentRow() in (-1, self.right_list_widget.count() - 1)
                and len(self.right_list_widget.selectedItems()) == 1)
            or len(self.right_list_widget.selectedItems()) == 0
        )

        self.__button_selected_to_right.setDisabled(len(self.left_list_widget.selectedItems()) == 0)
        self.__button_selected_to_left.setDisabled(len(self.right_list_widget.selectedItems()) == 0)

    def __connect(self):
        self.left_list_widget.itemSelectionChanged.connect(self.__set_button_status)
        self.right_list_widget.itemSelectionChanged.connect(self.__set_button_status)

        if self.__clone:
            # Multiple selected items
            self.__button_selected_to_right.clicked.connect(self.__clone_to_right)
            self.__button_selected_to_left.clicked.connect(self.__remove_from_right)

            # Move all items
            self.__button_all_to_right.clicked.connect(lambda: self.__clone_to_right(True))
            self.__button_all_to_left.clicked.connect(lambda: self.__remove_from_right(True))

            # Double click item
            self.left_list_widget.itemDoubleClicked.connect(self.__left_double_clicked)
            self.right_list_widget.itemDoubleClicked.connect(self.__right_double_clicked)
        else:
            # Multiple selected items
            self.__button_selected_to_right.clicked.connect(
                lambda: self.__move_items(self.left_list_widget, self.right_list_widget))
            self.__button_selected_to_left.clicked.connect(
                lambda: self.__move_items(self.right_list_widget, self.left_list_widget))

            # Move all items
            self.__button_all_to_right.clicked.connect(
                lambda: self.__move_all(self.left_list_widget, self.right_list_widget))
            self.__button_all_to_left.clicked.connect(
                lambda: self.__move_all(self.right_list_widget, self.left_list_widget))

        # Move up/down
        self.__button_up.clicked.connect(self.__move_up)
        self.__button_down.clicked.connect(self.__move_down)

    def __move_items(self, source: QListWidget, destination: QListWidget):
        temp_list = []
        rows = sorted([index.row() for index in source.selectedIndexes()], reverse=True)

        for row in rows:
            temp_list.append(source.takeItem(row))

        for item in reversed(temp_list):
            destination.addItem(item)

        self.right_count_changed.emit(self.right_list_widget.count())
        self.right_list_changed.emit(self.get_right_dict())
        self.__set_button_status()

    def __move_all(self, source: QListWidget, destination: QListWidget):
        while source.count() > 0:
            destination.addItem(source.takeItem(0))

        self.right_count_changed.emit(self.right_list_widget.count())
        self.right_list_changed.emit(self.get_right_dict())
        self.__set_button_status()

    def __move_up(self):
        current_row = self.right_list_widget.currentRow()
        rows = sorted([index.row() for index in self.right_list_widget.selectedIndexes() if index.row() != 0])
        self.right_list_widget.item(0).setSelected(False)

        for row in rows:
            current_item = self.right_list_widget.takeItem(row)
            self.right_list_widget.insertItem(row - 1, current_item)

        if current_row != 0 or len(rows) == 0:
            self.right_list_widget.setCurrentRow(current_row - 1)
        else:
            self.right_list_widget.setCurrentRow(rows[0] - 1)

        for row in rows:
            self.right_list_widget.item(row - 1).setSelected(True)

    def __move_down(self):
        current_row = self.right_list_widget.currentRow()
        last_row = self.right_list_widget.count() - 1
        rows = sorted([index.row() for index in self.right_list_widget.selectedIndexes() if index.row() != last_row],
                      reverse=True)
        self.right_list_widget.item(last_row).setSelected(False)

        for row in rows:
            current_item = self.right_list_widget.takeItem(row)
            self.right_list_widget.insertItem(row + 1, current_item)

        if current_row != last_row or len(rows) == 0:
            self.right_list_widget.setCurrentRow(current_row + 1)
        else:
            self.right_list_widget.setCurrentRow(rows[-1] + 1)

        for row in rows:
            self.right_list_widget.item(row + 1).setSelected(True)

    def __clone_to_right(self, all_items=False, init=False):
        source = self.left_list_widget
        destination = self.right_list_widget
        rows = []

        if init:
            left_items = [source.item(i) for i in range(source.count())]
            temp_dict = {}
            keys_to_clone = self.__right_list.copy()

            # Fixed items
            if self.__fixed_list:
                for fixed in self.__fixed_list:
                    if fixed not in keys_to_clone:
                        keys_to_clone.append(fixed)

            for item in left_items:
                item_data = item.data(Qt.UserRole)
                if item_data in keys_to_clone:
                    temp_dict[item_data] = source.row(item)

            for key in keys_to_clone:
                if key in temp_dict.keys():
                    rows.append(temp_dict[key])
        elif all_items:
            rows = range(source.count())
        else:
            rows = sorted([index.row() for index in source.selectedIndexes()])

        for row in rows:
            item: QListWidgetItem = source.item(row)

            if item.flags() & Qt.ItemIsSelectable == Qt.ItemIsSelectable:
                destination.addItem(item.clone())
                item.setForeground(Qt.gray)
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                item.setSelected(False)

        self.right_count_changed.emit(self.right_list_widget.count())
        self.right_list_changed.emit(self.get_right_dict())
        self.__set_button_status()

    def __remove_from_right(self, all_items=False):
        source = self.right_list_widget
        destination = self.left_list_widget

        if all_items:
            rows = range(source.count() - 1, -1, -1)
        else:
            rows = sorted([index.row() for index in source.selectedIndexes()], reverse=True)

        for row in rows:
            if source.item(row).data(Qt.UserRole) in self.__fixed_list:
                continue

            item: QListWidgetItem = source.takeItem(row)
            matching_row = self.__get_first_row_by_user_role_data(destination, item.data(Qt.UserRole))

            if matching_row == -1:
                return

            left_item = self.left_list_widget.item(matching_row)

            if left_item.flags() & Qt.ItemIsSelectable != Qt.ItemIsSelectable:
                left_item.setForeground(Qt.black)
                left_item.setFlags(item.flags() | Qt.ItemIsSelectable)

        self.right_count_changed.emit(self.right_list_widget.count())
        self.right_list_changed.emit(self.get_right_dict())
        self.__set_button_status()

    def __left_double_clicked(self, item: QListWidgetItem):
        if item.flags() & Qt.ItemIsSelectable == Qt.ItemIsSelectable:
            self.right_list_widget.addItem(item.clone())
            item.setForeground(Qt.gray)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            item.setSelected(False)

            self.right_count_changed.emit(self.right_list_widget.count())
            self.right_list_changed.emit(self.get_right_dict())
            self.__set_button_status()

    def __right_double_clicked(self, item: QListWidgetItem):
        if item.data(Qt.UserRole) in self.__fixed_list:
            return

        matching_row = self.__get_first_row_by_user_role_data(self.left_list_widget, item.data(Qt.UserRole))
        self.right_list_widget.takeItem(self.right_list_widget.row(item))

        if matching_row == -1:
            return

        left_item = self.left_list_widget.item(matching_row)

        if left_item.flags() & Qt.ItemIsSelectable != Qt.ItemIsSelectable:
            left_item.setForeground(Qt.black)
            left_item.setFlags(item.flags() | Qt.ItemIsSelectable)

            self.right_count_changed.emit(self.right_list_widget.count())
            self.right_list_changed.emit(self.get_right_dict())
            self.__set_button_status()

    @staticmethod
    def __get_first_row_by_user_role_data(list_widget: QListWidget, data) -> int:
        items = [list_widget.item(i) for i in range(list_widget.count())]

        for item in items:
            item_data = item.data(Qt.UserRole)
            if item_data == data:
                return list_widget.row(item)

        return -1

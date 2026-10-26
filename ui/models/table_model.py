from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class RecordTableModel(QAbstractTableModel):
    """Универсальная модель для списка ORM-объектов."""

    def __init__(self, columns: list[tuple[str, str]], rows: list | None = None):
        super().__init__()
        # columns: список (атрибут, заголовок)
        self.columns = columns
        self.rows: list = rows or []

    def set_rows(self, rows: list):
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            obj = self.rows[index.row()]
            attr = self.columns[index.column()][0]
            value = getattr(obj, attr, "")
            return "" if value is None else str(value)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.columns[section][1]
        return section + 1

    def record_at(self, row: int):
        return self.rows[row]
from PySide6.QtCore import Qt, QSortFilterProxyModel


class SearchProxyModel(QSortFilterProxyModel):
    """Прокси для поиска по нескольким колонкам и корректной сортировки."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._search_columns: list[int] | None = None  # None = искать везде

    def set_search_columns(self, columns: list[int] | None):
        """Ограничить поиск конкретными колонками (индексы)."""
        self._search_columns = columns
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        pattern = self.filterRegularExpression().pattern()
        if not pattern:
            return True

        model = self.sourceModel()
        columns = self._search_columns or range(model.columnCount())

        for col in columns:
            value = model.raw_value(source_row, col)
            if value is None:
                continue
            if pattern.lower() in str(value).lower():
                return True
        return False

    def lessThan(self, left, right):
        model = self.sourceModel()
        left_val = model.raw_value(left.row(), left.column())
        right_val = model.raw_value(right.row(), right.column())

        if left_val is None:
            return False
        if right_val is None:
            return True

        # Пробуем сравнить как числа (для номеров ПЛ)
        try:
            return float(left_val) < float(right_val)
        except (ValueError, TypeError):
            pass

        return str(left_val).lower() < str(right_val).lower()
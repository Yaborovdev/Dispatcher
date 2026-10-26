from datetime import date
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.cell import MergedCell
from openpyxl.utils import get_column_letter

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

MONTHS_RU = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]


def safe_write(ws, cell_address: str, value):
    """
    Безопасно записывает значение в ячейку.
    Если ячейка является частью объединённого диапазона (MergedCell),
    запись перенаправляется в левую верхнюю ячейку этого диапазона.
    """
    cell = ws[cell_address]

    # Проверяем, находится ли ячейка внутри объединенного диапазона
    for merged_range in ws.merged_cells.ranges:
        if cell.coordinate in merged_range:
            anchor = (
                f"{get_column_letter(merged_range.min_col)}"
                f"{merged_range.min_row}"
            )
            ws[anchor] = value
            return

    # Если это MergedCell, но диапазон не найден — пропускаем во избежание ошибки
    if isinstance(cell, MergedCell):
        print(f"ВНИМАНИЕ: {cell_address} - объединенная ячейка, но диапазон не найден. Запись пропущена.")
        return

    # Обычная ячейка
    cell.value = value


def fill_waybill_template(waybill, output_path: str | Path) -> Path:
    """
    Заполняет Excel-шаблон данными путевого листа.
    waybill - объект модели Waybill (со всеми связями driver, vehicle и т.д.)
    """
    template_name = _template_filename(waybill.template_type)
    template_path = TEMPLATES_DIR / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")

    wb = load_workbook(template_path)
    ws = wb["Лист1"]

    # --- Номер и серия ПЛ ---
    safe_write(ws, "BA4", waybill.number)
    safe_write(ws, "AJ4", "")

    # --- Дата выдачи ---
    d = waybill.date_issue
    if d:
        safe_write(ws, "AK5", d.day)
        safe_write(ws, "AM5", MONTHS_RU[d.month])
        safe_write(ws, "AY5", d.year)

    # --- Срок действия ---
    start = waybill.date_start or waybill.date_issue
    end = waybill.date_end
    if start:
        safe_write(ws, "AK6", start.day)
        safe_write(ws, "AM6", MONTHS_RU[start.month])
        safe_write(ws, "AY6", start.year)
    if end:
        safe_write(ws, "BC6", end.day)
        safe_write(ws, "BE6", MONTHS_RU[end.month])
        safe_write(ws, "BK6", end.year)

    # --- Транспорт ---
    v = waybill.vehicle
    if v:
        safe_write(ws, "A12", v.brand_model)
        safe_write(ws, "B13", v.gov_number)

    # --- Водитель ---
    drv = waybill.driver
    if drv:
        safe_write(ws, "B14", drv.full_name)
        safe_write(ws, "B15", drv.driver_license)
        safe_write(ws, "B16", drv.snils)

    # --- Полуприцеп (Прицеп 1) ---
    t = waybill.trailer
    if t:
        safe_write(ws, "I17", t.brand_model)
        safe_write(ws, "S17", t.reg_number)

    # --- Заказчик и маршрут ---
    if waybill.customer:
        safe_write(ws, "A21", waybill.customer.name)
    if waybill.route:
        safe_write(ws, "W21", waybill.route)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


def _template_filename(template_type: str) -> str:
    """Возвращает имя файла шаблона для соответствующего типа ПЛ."""
    mapping = {
        "междугородний": "mezhgorod.xlsx",
        "грузовой": "gruzovoy_4C.xlsx",  # <--- Исправлено под ваш файл
        "спецтехника": "spectehnika.xlsx",
        "автокран": "avtokran.xlsx",
        "легковой": "legkovoy.xlsx",
    }
    # Если тип не найден, по умолчанию берем грузовой
    return mapping.get(template_type, "gruzovoy_4C.xlsx")
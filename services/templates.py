"""Единый реестр типов путевых листов и привязка к Excel-шаблонам.

Тип ПЛ, файл шаблона, имя листа и адреса ячеек описываются в одном месте,
чтобы список в диалоге и логика экспорта не расходились.
"""
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class TemplateSpec:
    file: str                  # имя файла в папке templates/
    sheet: str                 # лист, на который пишем
    cells: Mapping[str, str]   # поле -> адрес ячейки (левая верхняя ячейка объединённого диапазона)


# Поля, которые умеет заполнять excel_service.build_values:
#   number
#   issue_day, issue_month, issue_year, issue_year_short
#   start_day, start_month, start_year
#   end_day, end_month, end_year
#   vehicle_model, vehicle_number
#   driver_name, driver_license, driver_snils
#   trailer_model, trailer_number
#   customer, route

GRUZOVOY_CELLS = {
    "number": "CX3",
    "issue_day": "BG5", "issue_month": "BP5", "issue_year_short": "CQ5",
    "start_day": "BG6", "start_month": "BP6", "start_year": "CM6",
    "end_day": "DF6", "end_month": "DO6", "end_year": "EK6",
    "vehicle_model": "AH14", "vehicle_number": "AH15",
    "driver_name": "I16", "driver_license": "P18", "driver_snils": "P19",
    "trailer_model": "I22", "trailer_number": "AV22",
    "customer": "A40", "route": "AT40",
}

# Типовая межотраслевая форма № 3 (лист «стр1»). Срока действия и прицепа в форме нет.
LEGKOVOY_CELLS = {
    "number": "BX4",
    "issue_day": "AD5", "issue_month": "AI5", "issue_year": "AU5",
    "vehicle_model": "V10", "vehicle_number": "AI11",
    "driver_name": "M12", "driver_license": "S14",
    "customer": "Q20",   # «В распоряжение»
    "route": "R26",      # «Адрес подачи»
}

_GRUZOVOY = TemplateSpec("gruzovoy_4C.xlsx", "Лист1", GRUZOVOY_CELLS)

# Для типов без cells файла шаблона пока нет: чтобы добавить тип, положите файл
# в templates/ и заполните cells (адреса ячеек смотрите в самом шаблоне).
TEMPLATES: dict[str, TemplateSpec] = {
    "Междугородний": TemplateSpec("mezhgorod.xlsx", "Лист1", {}),
    "Грузовой (4С)": _GRUZOVOY,
    "Грузовой (4Р)": _GRUZOVOY,
    "Спецтехника": TemplateSpec("spectehnika.xlsx", "Лист1", {}),
    "Автокран": TemplateSpec("avtokran.xlsx", "Лист1", {}),
    "Легковой": TemplateSpec("legkovoy.xlsx", "стр1", LEGKOVOY_CELLS),
}

TEMPLATE_TYPES: list[str] = list(TEMPLATES)

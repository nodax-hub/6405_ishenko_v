"""
14.09.24

Задание. Вычислить значение функции y в диапазоне x = [от n0, с шагом h, до nk], результаты записать в файл results.
Переменны должны считываться из файла config, формат файла определяется согласно варианту задания.
Для считывания данных из config реализовать парсер файла.
Предусмотреть возможность задание параметров как аргументов запускаемого py файла через консоль.
Считываемые данные из конфиг файла: n0, h, nk, a, b, c. Можете дополнить по своему усмотрению.

Требование к лабораторным работам
• Код должен правильно работать.
• Отсутствует дублирование кода / логики.
• Отсутствует мусор (закомментированных строк, лишних переменных и т.д.).
• Код должен быть читабельным (осмысленное название переменных и функций, прослеживается логика компоновки)
• Соблюдается форматирование кода
• В коде присутствует документация.
• В github репозитории нет лишних файлов / папок.


Варинат 8:

8 y(x)=a (e^(2bx+c)+1)/(e^(2bx+c)-1) yaml

"""
import argparse
import math
from pathlib import Path
from pprint import pprint
from typing import Callable

import numpy as np
import yaml


def calc_tabulate_func(diapason: slice, func: Callable[[float], float], filename: Path = 'results.yaml'):
    pprint(result := {float(x): float(func(x))
                      for x in np.arange(diapason.start, diapason.stop, diapason.step)})

    with open(filename, 'w') as file:
        yaml.safe_dump(result, file)


def task(n0, h, nk, a, b, c):
    calc_tabulate_func(slice(n0, nk, h),
                       lambda x: a * (math.exp(2 * b * x + c) + 1) / (math.exp(2 * b * x + c) - 1))


def parse_arguments():
    """
    Парсинг аргументов командной строки.
    Позволяет переопределить параметры через консоль при запуске скрипта.
    """
    parser = argparse.ArgumentParser(description="Вычисление функции на диапазоне значений.")

    parser.add_argument('--n0', type=float, help="Начальное значение диапазона x.")
    parser.add_argument('--h', type=float, help="Шаг изменения x.")
    parser.add_argument('--nk', type=float, help="Конечное значение диапазона x.")
    parser.add_argument('--a', type=float, help="Параметр a в формуле.")
    parser.add_argument('--b', type=float, help="Параметр b в формуле.")
    parser.add_argument('--c', type=float, help="Параметр c в формуле.")
    parser.add_argument('--config', type=str, default='config.yaml', help="Путь к конфигурационному файлу.")

    return parser.parse_args()


def load_config(config_file: Path):
    with open(Path(config_file), 'r') as file:
        return yaml.safe_load(file)


def main():
    args = parse_arguments()

    # Если параметры заданы в аргументах командной строки, используем их
    if all(map(lambda a: a is not None, args.__dict__.values())):
        del args.config
        task(**args.__dict__)
    else:
        # В противном случае, загружаем параметры из конфиг файла
        task(**load_config(args.config))


if __name__ == '__main__':
    main()

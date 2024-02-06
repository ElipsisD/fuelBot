import locale

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from aiogram.types import InputFile
from pathlib import Path

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

path = Path('users_graphs')


def make_graph_stat(user_id: str, car: str, expenses: tuple) -> InputFile:
    """Создание графика"""

    fig = plt.figure(figsize=(7, 4))
    ax = fig.add_subplot()
    ax.plot(expenses[1], expenses[0], marker='s', markerfacecolor='w')
    ax.grid()
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ['%y',
                         '%b',
                         '%d',
                         '%H:%M',
                         '%H:%M',
                         '%S.%f', ]
    formatter.zero_formats = [''] + formatter.formats[:-1]
    formatter.zero_formats[3] = '%b %d'
    formatter.offset_formats = ['',
                                '%Y',
                                '%B %Y',
                                '%d %B %Y',
                                '%d %B %Y',
                                '%d %B %Y %H:%M', ]
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    plt.ylabel('л / 100 км')
    plt.title(f'Аналитика расхода на {car}')
    graph_path = path.joinpath(f'{user_id}-{car}.png').as_posix()
    fig.savefig(graph_path)
    plt.close(fig)
    return InputFile(graph_path)

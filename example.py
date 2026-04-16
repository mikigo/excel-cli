# -*- coding: utf-8 -*-
# 示例数据文件

data = {
    "headers": ["姓名", "年龄", "城市", "得分"],
    "rows": [
        ["张三", 28, "北京", 85],
        ["李四", 32, "上海", 92],
        ["王五", 25, "广州", 78],
        ["合计", "=SUM(B1:B3)", "", "=SUM(D1:D3)"],
        ["平均", "=AVG(B1:B3)", "", "=AVG(D1:D3)"],
        ["最大", "=MAX(B1:B3)", "", "=MAX(D1:D3)"],
        ["最小", "=MIN(B1:B3)", "", "=MIN(D1:D3)"],
        ["计数", "=COUNT(B1:B3)", "", "=COUNT(D1:D3)"],
    ]
}

formulas = {
    "SUM": lambda cells: sum(cells),
    "AVG": lambda cells: sum(cells) / len(cells) if cells else 0,
    "COUNT": lambda cells: len(cells),
    "MIN": lambda cells: min(cells) if cells else 0,
    "MAX": lambda cells: max(cells) if cells else 0,
}

import datetime
def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d")

custom_functions = {
    "current_time": get_current_time,
}
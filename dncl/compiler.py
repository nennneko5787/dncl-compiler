import re
from typing import Union, Literal

from .calc import calc

# 変数のパターン
stringPattern = re.compile(r"「(.*)」")
stringPattern2 = re.compile(r"\"(.*)\"")
arrayPattern = re.compile(r"(.*)\[(\d+)\]$")
# 命令
printPattern = re.compile(r"(.*)を表示する")
# 式のパターン
assignPattern = re.compile(r"(.*)←(.*)")
addPattern = re.compile(r"(.*)を(.*)増やす")
removePattern = re.compile(r"(.*)を(.*)減らす")
# 論理演算のパターン
andPattern = re.compile(r"(.*)かつ(.*)")
orPattern = re.compile(r"(.*)または(.*)")
notPattern = re.compile(r"(.*)でない")
variables = {}


def compileScript(script: str):
    lines = script.splitlines()
    for line in lines:
        # Print
        if match := printPattern.match(line):
            runPrintCommand(match[1])
        # 代入式
        elif match := assignPattern.match(line):
            assignment(match[1], match[2])
        elif match := addPattern.match(line):
            assignment(match[1], f"{match[1]}＋{match[2]}")
        elif match := removePattern.match(line):
            assignment(match[1], f"{match[1]}－{match[2]}")


def boolToDNCLBool(flag: bool) -> Literal["真", "偽"]:
    return "真" if flag else "偽"


def dnclBoolToBool(flag: Literal["真", "偽"]) -> bool:
    return flag == "真"


def relationalOperation(raw: str) -> Literal["真", "偽"]:
    if len(value := raw.split("＞")) > 1:
        return boolToDNCLBool(underStanding(value[0]) > underStanding(value[1]))
    elif len(value := raw.split("＜")) > 1:
        return boolToDNCLBool(underStanding(value[0]) < underStanding(value[1]))
    elif len(value := raw.split("＝")) > 1:
        return boolToDNCLBool(underStanding(value[0]) == underStanding(value[1]))
    elif len(value := raw.split("≠")) > 1:
        return boolToDNCLBool(underStanding(value[0]) != underStanding(value[1]))
    elif len(value := raw.split("≠")) > 1:
        return boolToDNCLBool(underStanding(value[0]) != underStanding(value[1]))
    elif len(value := raw.split("≧")) > 1:
        return boolToDNCLBool(underStanding(value[0]) >= underStanding(value[1]))
    elif len(value := raw.split("≦")) > 1:
        return boolToDNCLBool(underStanding(value[0]) <= underStanding(value[1]))


def logicOperation(raw: str) -> Literal["真", "偽"]:
    """グルーピングとネストに対応した論理式の評価"""
    raw = raw.strip(" ")

    # グループ化されたカッコを先に評価
    while "（" in raw and "）" in raw:
        raw = evaluateParentheses(raw)

    # NOT
    if raw.endswith("でない"):
        return boolToDNCLBool(not dnclBoolToBool(relationalOperation(raw[:-3])))

    # AND / OR 左から順に（AND優先ならこの順序でOK）
    for op, op_type in [("かつ", "and"), ("または", "or")]:
        level = 0
        split_index = -1
        for i in range(len(raw)):
            if raw[i] == "（":
                level += 1
            elif raw[i] == "）":
                level -= 1
            elif level == 0 and raw[i : i + len(op)] == op:
                split_index = i
                break

        if split_index != -1:
            left = raw[:split_index]
            right = raw[split_index + len(op) :]
            if op_type == "and":
                return boolToDNCLBool(
                    dnclBoolToBool(logicOperation(left))
                    and dnclBoolToBool(logicOperation(right))
                )
            elif op_type == "or":
                return boolToDNCLBool(
                    dnclBoolToBool(logicOperation(left))
                    or dnclBoolToBool(logicOperation(right))
                )

    # 最後に単一の比較式などを処理
    return relationalOperation(raw)


def evaluateParentheses(expr: str) -> str:
    """最も外側の（）を見つけて評価する"""
    stack = []
    for i, char in enumerate(expr):
        if char == "（":
            stack.append(i)
        elif char == "）" and stack:
            start = stack.pop()
            if not stack:  # 一番外側
                inside = expr[start + 1 : i]
                result = logicOperation(inside)
                expr = expr[:start] + result + expr[i + 1 :]
                return expr  # 一回だけ置換、再帰で全体を処理
    return expr


def underStanding(variable: str) -> Union[int, str, float]:
    """変数や文字列などを理解します。

    Args:
        variable (str): 変数または文字列または数値または式。

    Returns:
        Union[int, str, float]: 理解した値。
    """

    answer = 0
    isFirstMatch = True

    for part in variable.split("と"):
        part = part.strip(" ")
        # 論理演算
        if any(op in part for op in ["かつ", "または", "でない"]):
            if isFirstMatch:
                answer = str()
                isFirstMatch = False
            answer += logicOperation(part)
        # 比較演算
        elif any(op in part for op in "＞＜＝≠≠≧≦"):
            if isFirstMatch:
                answer = str()
                isFirstMatch = False
            answer += relationalOperation(part)
        # 文字列
        elif match := stringPattern.match(part):
            if isFirstMatch:
                answer = str()
                isFirstMatch = False
            answer += match[1]
        elif match := stringPattern2.match(part):
            if isFirstMatch:
                answer = str()
                isFirstMatch = False
            answer += match[1]
        # 配列
        elif part.startswith("{") and part.endswith("}"):
            if isFirstMatch:
                answer = list()
                isFirstMatch = False

            makedList = []
            for value in part.strip("{}").split(","):
                makedList.append(underStanding(value))

            answer += makedList
        # 整数
        elif part.isdigit():
            if isFirstMatch:
                answer = int()
                isFirstMatch = False
            answer += int(part)
        # 数値
        elif part.isnumeric():
            if isFirstMatch:
                answer = float()
                isFirstMatch = False
            answer += float(part)
        # 変数
        elif not any(op in part for op in "＋－×/÷％（）"):
            if match := arrayPattern.match(part):
                if isFirstMatch:
                    answer = type(variables[match[1]][int(match[2])])()
                    isFirstMatch = False

                answer += variables[match[1]][int(match[2])]
            else:
                if isFirstMatch:
                    answer = type(variables[part])()
                    isFirstMatch = False

                answer += variables[part]
        # inputs
        elif part == "【外部からの入力】":
            if isFirstMatch:
                answer = str()
                isFirstMatch = False
            answer += input("入力してください: ")
        else:
            val = calc(part)

            if isFirstMatch:
                answer = type(val)()
                isFirstMatch = False
            answer += val

    return answer


def assignment(name: str, raw: str):
    """変数に値を代入します。

    Args:
        name (str): 変数の名前。
        raw (str): 変数に代入する値。
    """

    value = underStanding(raw.strip(" "))
    variables[name.strip(" ")] = value


def runPrintCommand(variable: str):
    """DNCLでの「表示する」構文を実行します。

    Args:
        variable (str): 表示したい変数または文字列または数値。
    """
    value = underStanding(variable)
    print(value)

from typing import Union


def calc(formula: str) -> Union[int, float]:
    """DNCLの計算式で計算します。

    Args:
        formula (str): 計算式。

    Returns:
        Union[int, float]: 計算後の値。
    """

    def tokenize(s: str):
        tokens = []
        number = ""
        i = 0
        while i < len(s):
            char = s[i]
            if char.isdigit() or char == ".":
                number += char
            else:
                if number:
                    tokens.append(number)
                    number = ""
                if char in "＋－×/÷％":
                    tokens.append(char)
                elif char == "（":
                    depth = 1
                    i += 1
                    subexpr = ""
                    while i < len(s):
                        if s[i] == "（":
                            depth += 1
                        elif s[i] == "）":
                            depth -= 1
                            if depth == 0:
                                break
                        subexpr += s[i]
                        i += 1
                    tokens.append(calc(subexpr))
                elif char == " ":
                    pass  # 無視
                else:
                    raise ValueError(f"無効な文字: {char}")
            i += 1
        if number:
            tokens.append(number)
        return tokens

    def applyOperator(op, a, b):
        a = float(a)
        b = float(b)
        if op == "＋":
            return a + b
        elif op == "－":
            return a - b
        elif op == "×":
            return a * b
        elif op == "/":
            return a / b
        elif op == "÷":
            return a // b
        elif op == "％":
            return a % b
        else:
            raise ValueError(f"無効な演算子: {op}")

    def evaluate(tokens):
        # 優先度順：× / ÷ ％ → ＋ －
        # ステップ1：× / ÷ ％を処理
        i = 0
        while i < len(tokens):
            if tokens[i] in ("×", "/", "÷", "％"):
                result = applyOperator(tokens[i], tokens[i - 1], tokens[i + 1])
                tokens[i - 1 : i + 2] = [result]
                i -= 1
            else:
                i += 1

        # ステップ2：＋ －を処理
        i = 0
        while i < len(tokens):
            if tokens[i] in ("＋", "－"):
                result = applyOperator(tokens[i], tokens[i - 1], tokens[i + 1])
                tokens[i - 1 : i + 2] = [result]
                i -= 1
            else:
                i += 1
        return tokens[0]

    tokens = tokenize(formula)
    result = evaluate(tokens)
    return int(result) if float(result).is_integer() else result

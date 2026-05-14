from langchain_core.tools import tool


@tool
def financial_calculator(expression: str) -> str:
    """执行金融计算。支持常见金融指标计算，如PE、PB、ROE等。

    示例：
    - "PE=股价/每股收益, 股价=50, 每股收益=2.5" → 计算PE
    - "ROE=净利润/净资产, 净利润=1000万, 净资产=5000万" → 计算ROE
    """
    try:
        safe_expr = expression.replace("^", "**")
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in safe_expr):
            result = eval(safe_expr)
            return f"计算结果: {result}"
        return "不支持的计算表达式"
    except Exception as e:
        return f"计算错误: {str(e)}"

from langchain_core.tools import tool

@tool
def Calculator(first_num, second_num, evaluator):
    """Performe basic arthematic opration between two numbers"""
    return eval(f"{first_num} {evaluator} {second_num}")
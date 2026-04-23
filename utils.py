import pandas as pd
import ast

def parse_to_df(result):
    try:
        parsed = ast.literal_eval(result)
        if isinstance(parsed, list):
            return pd.DataFrame(parsed)
    except:
        return None
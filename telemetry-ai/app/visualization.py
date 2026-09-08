import pandas as pd
import numpy as np


class VisualizationRouter:

    @staticmethod
    def _convert_types(df: pd.DataFrame):
        df = df.copy()
        if len(df) == 0:
            return df
        for col in df.columns:
            if isinstance(df[col].iloc[0], pd.Timestamp):
                df[col] = df[col].astype(str)
            if isinstance(df[col].iloc[0], np.generic):
                df[col] = df[col].astype(float)
        return df

    @staticmethod
    def _reshape_long_to_wide(df: pd.DataFrame, query_type: str, parameters):
        """telemetry_numeric queries come back in long format: (time, value)
        for a single parameter, or (time, parameter, value) for multiple.
        Normalizes both into wide format (one column per parameter name)
        so the rest of this router works unchanged for every caller."""
        if df.empty or "value" not in df.columns:
            return df

        if "parameter" in df.columns:
            wide = df.pivot_table(index="time", columns="parameter", values="value").reset_index()
            wide.columns.name = None
            return wide

        if "time" in df.columns and parameters:
            return df.rename(columns={"value": parameters[0]})

        return df

    @staticmethod
    def build_response(df: pd.DataFrame, query_type=None, parameters=None):

        df = VisualizationRouter._reshape_long_to_wide(df, query_type, parameters)
        df = VisualizationRouter._convert_types(df)

        param_name = parameters[0] if parameters else None

        if query_type == "timeseries":
            param_cols = [c for c in df.columns if c != "time"]
            return {
                "type": "line",
                "parameter": param_name or (param_cols[0] if param_cols else None),
                "parameters": param_cols,
                "data": df.to_dict(orient="records")
            }

        if query_type == "compare":
            param_cols = [c for c in df.columns if c != "time"]
            return {
                "type": "multi_line",
                "parameters": parameters or param_cols,
                "data": df.to_dict(orient="records")
            }

        if query_type == "metric":
            return {
                "type": "metric",
                "value": float(df.iloc[0, 0]),
                "parameter": param_name
            }

        if df.shape[0] == 1 and df.shape[1] == 1:
            return {
                "type": "metric",
                "value": float(df.iloc[0, 0]),
                "parameter": param_name
            }

        if "time" in df.columns and len(df.columns) == 2:
            param = param_name or [c for c in df.columns if c != "time"][0]
            return {
                "type": "line",
                "parameter": param,
                "data": df.to_dict(orient="records")
            }

        if "time" in df.columns and len(df.columns) > 2:
            parameters_out = parameters or [c for c in df.columns if c != "time"]
            return {
                "type": "multi_line",
                "parameters": parameters_out,
                "data": df.to_dict(orient="records")
            }

        return {
            "type": "table",
            "data": df.to_dict(orient="records")
        }

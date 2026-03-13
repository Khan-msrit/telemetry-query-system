import pandas as pd
import numpy as np


class VisualizationRouter:

    @staticmethod
    def _convert_types(df: pd.DataFrame):
        df = df.copy()

        for col in df.columns:
            if isinstance(df[col].iloc[0], pd.Timestamp):
                df[col] = df[col].astype(str)

            if isinstance(df[col].iloc[0], np.generic):
                df[col] = df[col].astype(float)

        return df

    @staticmethod
    def build_response(df: pd.DataFrame):

        df = VisualizationRouter._convert_types(df)

        # Metric
        if df.shape[0] == 1 and df.shape[1] == 1:
            return {
                "type": "metric",
                "value": float(df.iloc[0, 0])
            }

        # Single timeseries
        if "time" in df.columns and len(df.columns) == 2:
            param = [c for c in df.columns if c != "time"][0]
            return {
                "type": "line",
                "parameter": param,
                "data": df.to_dict(orient="records")
            }

        # Multi timeseries
        if "time" in df.columns and len(df.columns) > 2:
            parameters = [c for c in df.columns if c != "time"]
            return {
                "type": "multi_line",
                "parameters": parameters,
                "data": df.to_dict(orient="records")
            }

        return {
            "type": "table",
            "data": df.to_dict(orient="records")
        }

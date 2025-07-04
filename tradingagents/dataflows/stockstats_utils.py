import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated
import os
from .config import get_config
from .akshare_utils import AKShareUtils


class StockstatsUtils:
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "ticker symbol for the company"],
        indicator: Annotated[
            str, "quantitative indicators based off of the stock data for the company"
        ],
        curr_date: Annotated[
            str, "curr date for retrieving stock price data, YYYY-mm-dd"
        ],
        data_dir: Annotated[
            str,
            "directory where the stock data is stored.",
        ],
        online: Annotated[
            bool,
            "whether to use online tools to fetch data or offline tools. If True, will use online tools.",
        ] = False,
    ):
        df = None
        data = None
        config = get_config()
        market_type = config.get("market_type", "US")

        if not online:
            try:
                data_file_path = os.path.join(
                        data_dir,
                        f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
                )
                data = pd.read_csv(data_file_path)
                df = wrap(data)
            except FileNotFoundError:
                raise Exception("Stockstats fail: Market data not fetched yet!")
            except Exception as e:
                raise Exception(f"Error reading data: {e}")
        else:
            today_date = pd.Timestamp.today()
            curr_date_dt = pd.to_datetime(curr_date)

            end_date = today_date
            start_date = today_date - pd.DateOffset(years=15)
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            cache_dir = config["data_cache_dir"]
            os.makedirs(cache_dir, exist_ok=True)

            data_file = os.path.join(
                cache_dir,
                f"{symbol}-YFin-data-{start_date_str}-{end_date_str}.csv",
            )

            if os.path.exists(data_file):
                try:
                    data = pd.read_csv(data_file)
                    data["Date"] = pd.to_datetime(data["Date"])
                except Exception as e:
                    print(f"Error reading data: {e}")
                    raise Exception(f"Error reading data: {e}")
            else:
                try:
                    if market_type == "CN":
                        data = AKShareUtils.get_stock_data(symbol, start_date_str, end_date_str)
                    else:
                        data = yf.download(
                        symbol,
                            start=start_date_str,
                            end=end_date_str,
                        multi_level_index=False,
                        progress=False,
                        auto_adjust=True,
                    )
                    data = data.reset_index()
                    data.to_csv(data_file)
                except Exception as e:
                    print(f"Error downloading data: {e}")
                    raise Exception(f"Error downloading data: {e}")

            df = wrap(data)
            df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
            curr_date = curr_date_dt.strftime("%Y-%m-%d")

        try:
            df[indicator]  # trigger stockstats to calculate the indicator
        except Exception as e:
            print(f"Error calculating indicator: {e}")
            raise Exception(f"Error calculating indicator: {e}")

        matching_rows = df[df["Date"].str.startswith(curr_date)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            return "N/A: Not a trading day (weekend or holiday)"

import yfinance as yf

from mcp_server.server.schemas.finance_result import FundDetails, FundSource, FundSummary

def get_fund_details(ticker: str) -> FundDetails:
    try:
        info = yf.Ticker(ticker).info
        symbol = info.get("symbol", ticker).upper()
        url = f"https://finance.yahoo.com/quote/{symbol}"

        summary = FundSummary(
            symbol=symbol,
            name=info.get("longName") or info.get("shortName") or "",
            classification=info.get("category") or info.get("fundFamily") or info.get("typeDisp"),
            expense_ratio=float(info.get("annualReportExpenseRatio") or info.get("netExpenseRatio") or 0),
            risk_level=info.get("morningStarRiskRating"),
            url=url,
            total_assets=info.get("totalAssets") or info.get("netAssets"),
            ytd_return=info.get("ytdReturn"),
            morningstar_rating=info.get("morningStarOverallRating"),
            morningstar_risk=info.get("morningStarRiskRating"))

        source = FundSource(
            provider="Yahoo Finance",
            source_url=url
        )

        return FundDetails(summary=summary, source=source)
    except Exception as e:
        raise RuntimeError(f"Error retrieving fund details: {e}")
"""
Sales Ledger Generator Module.

This module contains the core logic for generating realistic yearly sales
ledger entries from a total annual sales value.
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List, Optional

from utils import (
    get_preset_weights,
    normalize_percentages,
    split_amount_into_entries,
)


class SalesLedgerGenerator:
    """
    Generates realistic sales ledger entries for a financial year.

    Attributes:
        annual_sales: Total annual sales amount
        min_daily_sale: Minimum daily sale amount
        max_daily_sale: Maximum daily sale amount
        fy_start_date: Financial year start date
        distribution_mode: Distribution preset name or 'uniform'
        entry_mode: 'daily_summary' or 'multiple_entries'
        weights: Optional custom weights list
    """

    def __init__(
        self,
        annual_sales: float,
        min_daily_sale: float,
        max_daily_sale: float,
        fy_start_date: datetime,
        distribution_preset: str = "Fruit Wholesale",
        entry_mode: str = "daily_summary",
        ledger_name: str = "Cash",
        custom_weights: Optional[List[float]] = None,
        gst_enabled: bool = False,
        gst_rate: float = 0.0,
        gst_ledger_name: str = "GST Payable"
    ):
        """
        Initialize the generator with parameters.

        Args:
            annual_sales: Total annual sales amount
            min_daily_sale: Minimum allowed daily sale
            max_daily_sale: Maximum allowed daily sale
            fy_start_date: Start date of financial year
            distribution_preset: Name of distribution preset
            entry_mode: 'daily_summary' or 'multiple_entries'
            ledger_name: Name of the cash/party ledger account
            custom_weights: Optional list of 12 custom weights
            gst_enabled: Whether GST is applicable
            gst_rate: GST rate percentage (e.g., 18.0)
            gst_ledger_name: Name of GST ledger
        """
        self.annual_sales = round(annual_sales, 2)
        self.min_daily_sale = min_daily_sale
        self.max_daily_sale = max_daily_sale
        self.fy_start_date = fy_start_date
        self.distribution_preset = distribution_preset
        self.entry_mode = entry_mode.lower()
        self.ledger_name = ledger_name
        self.custom_weights = custom_weights
        self.gst_enabled = gst_enabled
        self.gst_rate = gst_rate
        self.gst_ledger_name = gst_ledger_name

        # Validate inputs
        if min_daily_sale > max_daily_sale:
            raise ValueError("Minimum daily sale cannot exceed maximum daily sale")
        if annual_sales <= 0:
            raise ValueError("Annual sales must be positive")

    def _get_month_end_date(self, start_date: datetime, month_offset: int) -> Tuple[datetime, datetime]:
        """
        Get the start and end dates for a specific month offset from FY start.

        Args:
            start_date: Financial year start date
            month_offset: Number of months from start (0-11)

        Returns:
            Tuple of (month_start_date, month_end_date)
        """
        # Calculate the target month
        target_month = start_date.month + month_offset
        target_year = start_date.year
        
        while target_month > 12:
            target_month -= 12
            target_year += 1

        month_start = datetime(target_year, target_month, 1)

        # Calculate end of month
        if target_month == 12:
            month_end = datetime(target_year, 12, 31)
        else:
            month_end = datetime(target_year, target_month + 1, 1) - timedelta(days=1)

        return month_start, month_end

    def generate_monthly_distribution(self) -> pd.DataFrame:
        """
        Generate monthly distribution of annual sales.

        Creates monthly percentages that sum to exactly 100% and calculates
        the amount for each month based on the actual financial year start date.

        Returns:
            DataFrame with columns: Month, Percentage, Amount, Year, MonthNum, StartDate, EndDate
        """
        # Get weights based on preset or custom
        if self.custom_weights is not None:
            weights = self.custom_weights
        elif self.distribution_preset.lower() == "uniform":
            weights = [1.0] * 12
        else:
            weights = get_preset_weights(self.distribution_preset)

        # Normalize to ensure exact 100%
        percentages = normalize_percentages(weights)

        # Calculate amounts using largest remainder method
        amounts = []
        remaining = self.annual_sales

        for i in range(11):  # First 11 months
            amount = round((percentages[i] / 100) * self.annual_sales, 2)
            amounts.append(amount)
            remaining -= amount

        # Last month gets the remainder to ensure exact total
        amounts.append(round(remaining, 2))

        # Generate month names and dates based on exact FY start
        month_names = []
        years = []
        month_nums = []
        start_dates = []
        end_dates = []

        for i in range(12):
            month_start, month_end = self._get_month_end_date(self.fy_start_date, i)
            
            # Get month name
            month_names.append(month_start.strftime("%B"))
            years.append(month_start.year)
            month_nums.append(month_start.month)
            start_dates.append(month_start.strftime("%Y-%m-%d"))
            end_dates.append(month_end.strftime("%Y-%m-%d"))

        # Create DataFrame
        df = pd.DataFrame({
            "Month": month_names,
            "Percentage": percentages,
            "Amount": amounts,
            "Year": years,
            "MonthNum": month_nums,
            "StartDate": start_dates,
            "EndDate": end_dates
        })

        # Verify total
        total = df["Amount"].sum()
        assert abs(total - self.annual_sales) < 0.01, f"Monthly total {total} != annual {self.annual_sales}"

        return df

    def _generate_daily_base_amounts(self, month_target: float, num_days: int) -> List[float]:
        """
        Generate daily amounts that sum to month target.

        Uses a weighted random approach to create natural variation
        while ensuring the total matches exactly.

        Args:
            month_target: Target total for the month
            num_days: Number of days in the month

        Returns:
            List of daily amounts summing to month_target
        """
        # Calculate average daily amount
        avg_daily = month_target / num_days

        # Ensure constraints are satisfiable
        effective_min = max(self.min_daily_sale, 1.0)
        effective_max = self.max_daily_sale

        if effective_min * num_days > month_target:
            effective_min = month_target / num_days * 0.5

        if effective_max * num_days < month_target:
            effective_max = month_target / num_days * 1.5

        # Generate random weights for variation
        weights = [random.uniform(0.7, 1.3) for _ in range(num_days)]
        total_weight = sum(weights)

        # Scale weights to match target
        amounts = []
        remaining = month_target

        for i in range(num_days - 1):
            proportion = weights[i] / total_weight
            amount = month_target * proportion
            amount = max(effective_min, min(effective_max, amount))
            amount = round(amount, 2)
            amounts.append(amount)
            remaining -= amount

        # Last day gets the remainder
        last_amount = round(remaining, 2)
        amounts.append(last_amount)

        # Final adjustment to ensure exact sum
        current_sum = sum(amounts)
        diff = round(month_target - current_sum, 2)
        if abs(diff) > 0.001:
            max_idx = amounts.index(max(amounts))
            amounts[max_idx] = round(amounts[max_idx] + diff, 2)

        return amounts

    def generate_daily_entries_for_month(
        self,
        month_target: float,
        month_start_date: datetime,
        month_end_date: datetime
    ) -> pd.DataFrame:
        """
        Generate daily sales entries for a single month.

        Args:
            month_target: Target total for the month
            month_start_date: Start date of the month period
            month_end_date: End date of the month period

        Returns:
            DataFrame with daily entries
        """
        days_in_month = (month_end_date - month_start_date).days + 1

        # Generate base daily amounts
        daily_amounts = self._generate_daily_base_amounts(month_target, days_in_month)

        entries = []
        for day_idx, amount in enumerate(daily_amounts):
            date = month_start_date + timedelta(days=day_idx)

            if self.entry_mode == "multiple_entries":
                # Split into multiple entries
                splits = split_amount_into_entries(amount, min_entries=2, max_entries=5)
                for split_amount in splits:
                    entries.append({
                        "Date": date.strftime("%Y-%m-%d"),
                        "VoucherType": "Sales",
                        "Ledger": self.ledger_name,
                        "Amount": round(split_amount, 2)
                    })
            else:
                # Single daily summary entry
                entries.append({
                    "Date": date.strftime("%Y-%m-%d"),
                    "VoucherType": "Sales",
                    "Ledger": self.ledger_name,
                    "Amount": round(amount, 2)
                })

        return pd.DataFrame(entries)

    def generate_full_ledger(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate complete sales ledger for the financial year.

        Returns:
            Tuple of (monthly_summary_df, full_ledger_df)
        """
        # Get monthly distribution
        monthly_df = self.generate_monthly_distribution()

        # Generate daily entries for each month using exact date ranges
        all_entries = []

        for month_idx in range(12):
            month_target = monthly_df.loc[month_idx, "Amount"]
            
            # Parse start and end dates from the monthly dataframe
            month_start_str = monthly_df.loc[month_idx, "StartDate"]
            month_end_str = monthly_df.loc[month_idx, "EndDate"]
            month_start_date = datetime.strptime(month_start_str, "%Y-%m-%d")
            month_end_date = datetime.strptime(month_end_str, "%Y-%m-%d")

            daily_df = self.generate_daily_entries_for_month(
                month_target, month_start_date, month_end_date
            )
            all_entries.append(daily_df)

        # Combine all entries
        ledger_df = pd.concat(all_entries, ignore_index=True)

        # Sort by date
        ledger_df = ledger_df.sort_values("Date").reset_index(drop=True)

        # Verify totals
        generated_total = ledger_df["Amount"].sum()

        # Final adjustment if there's a tiny discrepancy
        if abs(generated_total - self.annual_sales) > 0.001:
            diff = round(self.annual_sales - generated_total, 2)
            mid_idx = len(ledger_df) // 2
            ledger_df.loc[mid_idx, "Amount"] = round(
                ledger_df.loc[mid_idx, "Amount"] + diff, 2
            )

        final_total = ledger_df["Amount"].sum()
        assert abs(final_total - self.annual_sales) < 0.01, \
            f"Final total {final_total} != annual {self.annual_sales}"

        return monthly_df, ledger_df

    def export_to_excel(self, ledger_df: pd.DataFrame, output_path: str) -> None:
        """
        Export ledger to Excel file.

        Args:
            ledger_df: DataFrame with ledger entries
            output_path: Path for output Excel file
        """
        columns = ["Date", "VoucherType", "Ledger", "Amount"]
        export_df = ledger_df[columns].copy()
        export_df["Amount"] = export_df["Amount"].astype(float)
        export_df.to_excel(output_path, index=False, engine="openpyxl")

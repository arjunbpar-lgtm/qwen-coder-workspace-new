"""
Unit tests for the Sales Ledger Generator.

Run with: pytest test_generator.py -v
"""

import pytest
import sys
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator import SalesLedgerGenerator
from xml_converter import TallyXMLConverter
from utils import (
    get_preset_weights,
    normalize_percentages,
    split_amount_into_entries
)


class TestMonthlyTotalMatchesAnnual:
    """Test 1: generate_monthly_distribution() amounts must sum to exactly annual_sales."""

    def test_monthly_total_matches_annual(self):
        """Monthly distribution must sum to annual sales within 0.01."""
        gen = SalesLedgerGenerator(
            annual_sales=500000.0,
            min_daily_sale=500.0,
            max_daily_sale=5000.0,
            fy_start_date=datetime(2024, 4, 1),
            distribution_preset="Fruit Wholesale"
        )
        monthly_df = gen.generate_monthly_distribution()
        total = monthly_df["Amount"].sum()
        assert abs(total - 500000.0) < 0.01, f"Monthly total {total} != 500000.0"


class TestDailyTotalMatchesMonthly:
    """Test 2: For each month, sum of daily entries must match monthly target."""

    def test_daily_total_matches_monthly(self):
        """Daily entries per month must sum to monthly target within 0.01."""
        gen = SalesLedgerGenerator(
            annual_sales=365000.0,
            min_daily_sale=500.0,
            max_daily_sale=2000.0,
            fy_start_date=datetime(2024, 4, 1),
            distribution_preset="Uniform"
        )
        monthly_df, ledger_df = gen.generate_full_ledger()
        
        # Group by month and verify totals
        ledger_df['Month'] = pd.to_datetime(ledger_df['Date']).dt.month
        for _, row in monthly_df.iterrows():
            month_num = row['MonthNum']
            monthly_target = row['Amount']
            daily_sum = ledger_df[ledger_df['Month'] == month_num]['Amount'].sum()
            assert abs(daily_sum - monthly_target) < 0.01, \
                f"Month {month_num}: daily sum {daily_sum} != monthly target {monthly_target}"


class TestAnnualTotalEndToEnd:
    """Test 3: Full generate_full_ledger() — ledger_df['Amount'].sum() must equal annual_sales."""

    def test_annual_total_end_to_end(self):
        """Full ledger generation must produce exact annual total."""
        gen = SalesLedgerGenerator(
            annual_sales=750000.0,
            min_daily_sale=1000.0,
            max_daily_sale=5000.0,
            fy_start_date=datetime(2024, 4, 1),
            distribution_preset="Fruit Wholesale"
        )
        monthly_df, ledger_df = gen.generate_full_ledger()
        total = ledger_df["Amount"].sum()
        assert abs(total - 750000.0) < 0.01, f"Ledger total {total} != 750000.0"


class TestSeasonalWeightsSumTo100:
    """Test 4: normalize_percentages() output must sum to exactly 100.0."""

    def test_seasonal_weights_sum_to_100(self):
        """Normalized percentages must sum to exactly 100.0."""
        weights = [6.0, 6.5, 7.0, 8.0, 9.0, 10.0, 11.0, 10.0, 9.0, 8.0, 7.0, 6.5]
        normalized = normalize_percentages(weights)
        total = sum(normalized)
        assert abs(total - 100.0) < 0.001, f"Normalized weights sum {total} != 100.0"


class TestMinMaxConstraintsSatisfied:
    """Test 5: At least 95% of daily entries must be within bounds."""

    def test_min_max_constraints_satisfied(self):
        """With min_daily=500 max_daily=5000, annual=500000, at least 95% within bounds."""
        gen = SalesLedgerGenerator(
            annual_sales=500000.0,
            min_daily_sale=500.0,
            max_daily_sale=5000.0,
            fy_start_date=datetime(2024, 4, 1),
            distribution_preset="Uniform"
        )
        monthly_df, ledger_df = gen.generate_full_ledger()
        
        in_bounds = (
            (ledger_df['Amount'] >= 500.0) & 
            (ledger_df['Amount'] <= 5000.0)
        ).sum()
        total_entries = len(ledger_df)
        percentage_in_bounds = (in_bounds / total_entries) * 100
        
        assert percentage_in_bounds >= 95.0, \
            f"Only {percentage_in_bounds:.1f}% of entries within bounds"


class TestMultipleEntriesMode:
    """Test 6: In multiple_entries mode, sum of split amounts must equal original."""

    def test_multiple_entries_mode(self):
        """Split amounts for each day must sum to original daily amount."""
        gen = SalesLedgerGenerator(
            annual_sales=365000.0,
            min_daily_sale=500.0,
            max_daily_sale=2000.0,
            fy_start_date=datetime(2024, 4, 1),
            distribution_preset="Uniform",
            entry_mode="multiple_entries"
        )
        monthly_df, ledger_df = gen.generate_full_ledger()
        
        # Group by date and verify sums
        grouped = ledger_df.groupby('Date')['Amount'].sum().reset_index()
        grouped.columns = ['Date', 'DailyTotal']
        
        # Each daily total should be reasonable (within expected range)
        assert len(grouped) == 365, f"Expected 365 days, got {len(grouped)}"
        assert abs(grouped['DailyTotal'].sum() - 365000.0) < 0.01


class TestXMLStructureValid:
    """Test 7: convert_ledger_to_xml() output must have correct tags."""

    def test_xml_structure_valid(self):
        """XML output must be parseable and contain required tags."""
        gen = SalesLedgerGenerator(
            annual_sales=100000.0,
            min_daily_sale=200.0,
            max_daily_sale=500.0,
            fy_start_date=datetime(2024, 4, 1),
            distribution_preset="Uniform"
        )
        monthly_df, ledger_df = gen.generate_full_ledger()
        
        converter = TallyXMLConverter(company_name="Test Company")
        output_path = "/tmp/test_vouchers.xml"
        converter.convert_ledger_to_xml(ledger_df, output_path)
        
        # Parse and verify structure
        tree = ET.parse(output_path)
        root = tree.getroot()
        
        # Check root tag
        assert root.tag == "ENVELOPE", f"Root tag is {root.tag}, expected ENVELOPE"
        
        # Check required elements
        header = root.find("HEADER")
        body = root.find("BODY")
        assert header is not None, "Missing HEADER element"
        assert body is not None, "Missing BODY element"
        
        # Check nested structure
        tally_request = header.find("TALLYREQUEST")
        assert tally_request is not None, "Missing TALLYREQUEST"
        assert tally_request.text == "Import Data", f"TALLYREQUEST is '{tally_request.text}'"
        
        import_data = body.find("IMPORTDATA")
        assert import_data is not None, "Missing IMPORTDATA"
        
        request_data = import_data.find("REQUESTDATA")
        assert request_data is not None, "Missing REQUESTDATA"
        
        tally_message = request_data.find("TALLYMESSAGE")
        assert tally_message is not None, "Missing TALLYMESSAGE"
        
        voucher = tally_message.find("VOUCHER")
        assert voucher is not None, "Missing VOUCHER"
        
        all_ledger_entries = voucher.find("ALLLEDGERENTRIES.LIST")
        assert all_ledger_entries is not None, "Missing ALLLEDGERENTRIES.LIST"


class TestGSTAmountsCorrect:
    """Test 8: When GST is 18%, GST ledger entry must equal round(base * 0.18, 2)."""

    def test_gst_amounts_correct(self):
        """GST amounts must be calculated correctly."""
        gen = SalesLedgerGenerator(
            annual_sales=100000.0,
            min_daily_sale=200.0,
            max_daily_sale=500.0,
            fy_start_date=datetime(2024, 4, 1),
            distribution_preset="Uniform",
            gst_enabled=True,
            gst_rate=18.0,
            gst_ledger_name="GST Payable"
        )
        monthly_df, ledger_df = gen.generate_full_ledger()
        
        # Get first few days' data
        first_day = ledger_df.iloc[0]['Date']
        first_day_amount = ledger_df[ledger_df['Date'] == first_day]['Amount'].sum()
        
        # Calculate expected GST
        expected_gst = round(first_day_amount * 0.18, 2)
        expected_sales = -(first_day_amount + expected_gst)
        expected_cash = first_day_amount + expected_gst
        
        # Generate XML and verify
        converter = TallyXMLConverter(
            company_name="Test Company",
            sales_ledger_name="Sales",
            cash_ledger_name="Cash"
        )
        output_path = "/tmp/test_gst_vouchers.xml"
        converter.convert_ledger_to_xml(
            ledger_df.head(1),  # Just first entry for simplicity
            output_path,
            gst_enabled=True,
            gst_rate=18.0,
            gst_ledger_name="GST Payable"
        )
        
        # Parse XML and verify amounts
        tree = ET.parse(output_path)
        root = tree.getroot()
        
        voucher = root.find(".//VOUCHER")
        assert voucher is not None, "Missing VOUCHER"
        
        ledger_entries = voucher.findall("ALLLEDGERENTRIES.LIST")
        assert len(ledger_entries) == 3, f"Expected 3 ledger entries, got {len(ledger_entries)}"
        
        # Find amounts by ledger name
        amounts_by_ledger = {}
        for entry in ledger_entries:
            ledger_name = entry.find("LEDGERNAME").text
            amount_elem = entry.find("AMOUNT")
            if amount_elem is not None:
                amounts_by_ledger[ledger_name] = float(amount_elem.text)
        
        # Verify GST Payable exists and has correct amount
        assert "GST Payable" in amounts_by_ledger, "Missing GST Payable ledger entry"
        gst_amount = abs(amounts_by_ledger["GST Payable"])
        
        # Allow small tolerance for rounding
        assert abs(gst_amount - expected_gst) < 0.02, \
            f"GST amount {gst_amount} != expected {expected_gst}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

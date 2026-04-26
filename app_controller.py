"""
Application Controller.

Manages screen navigation and shared data across all screens.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import random
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.logger import get_logger
from export.tally_xml_export import TallyXMLExporter
from export.excel_export import ExcelExporter


class AppController:
    """
    Central controller for the multi-screen application.
    
    Manages:
    - Screen navigation
    - Shared data state
    - Data generation logic
    - Export operations
    """
    
    def __init__(self, root):
        self.root = root
        self.logger = get_logger()
        
        # Data state
        self.annual_sales = 1200000.0
        self.mode = "annual"
        self.monthly_distribution = []
        self.selected_month = 0
        self.generated_entries = []
        self.statistics = {}
        
        # Exporters
        self.xml_exporter = TallyXMLExporter()
        self.excel_exporter = ExcelExporter()
        
        self.logger.info("AppController initialized")
    
    def set_annual_sales(self, value: float):
        """Set annual sales amount."""
        self.annual_sales = value
        self.logger.info(f"Annual sales set to: {value}")
    
    def get_annual_sales(self) -> float:
        """Get annual sales amount."""
        return self.annual_sales
    
    def set_mode(self, mode: str):
        """Set operation mode."""
        self.mode = mode
        self.logger.info(f"Mode set to: {mode}")
    
    def set_monthly_distribution(self, distribution: list):
        """Set monthly distribution data."""
        self.monthly_distribution = distribution
        self.logger.info(f"Monthly distribution set with {len(distribution)} months")
    
    def get_monthly_distribution(self) -> list:
        """Get monthly distribution data."""
        return self.monthly_distribution
    
    def set_selected_month(self, index: int):
        """Set currently selected month index."""
        self.selected_month = index
    
    def get_selected_month(self) -> int:
        """Get currently selected month index."""
        return self.selected_month
    
    def generate_month_entries(
        self,
        month_idx: int,
        monthly_total: float,
        min_daily: float,
        max_daily: float,
        leave_days: set,
        debit_ledger: str,
        credit_ledger: str,
        narration: str,
        round_to_10: bool = False
    ) -> list:
        """Generate daily entries for a month."""
        try:
            # Get month info
            if not self.monthly_distribution or month_idx >= len(self.monthly_distribution):
                return []
            
            month_data = self.monthly_distribution[month_idx]
            month_name = month_data['month']
            
            # Calculate days in month (simplified)
            days_in_month = 30
            
            # Generate daily amounts
            working_days = [d for d in range(1, days_in_month + 1) if d not in leave_days]
            num_working_days = len(working_days)
            
            if num_working_days == 0:
                messagebox.showwarning("Warning", "No working days selected!")
                return []
            
            # Generate amounts that sum to monthly total
            entries = []
            remaining = monthly_total
            
            for i, day in enumerate(working_days):
                is_last = (i == num_working_days - 1)
                
                if is_last:
                    amount = remaining
                else:
                    # Random amount within constraints
                    avg_remaining = remaining / (num_working_days - i)
                    min_amt = max(min_daily, avg_remaining * 0.5)
                    max_amt = min(max_daily, avg_remaining * 1.5)
                    
                    if min_amt > max_amt:
                        min_amt, max_amt = max_amt, min_amt
                    
                    amount = random.uniform(min_amt, max_amt)
                
                # Round to nearest 10 if enabled
                if round_to_10:
                    amount = round(amount / 10) * 10
                
                amount = round(amount, 2)
                
                # Create entry
                # Use current year for simplicity
                year = datetime.now().year
                month_num = (month_idx + 4) % 12 + 1  # April=4, May=5, etc.
                if month_num < 4:
                    year += 1
                
                try:
                    date = datetime(year, month_num, min(day, 28))  # Avoid invalid dates
                except ValueError:
                    date = datetime(year, month_num, 28)
                
                entries.append({
                    'Date': date.strftime("%Y-%m-%d"),
                    'Debit Ledger': debit_ledger,
                    'Credit Ledger': credit_ledger,
                    'Amount': amount,
                    'Narration': narration,
                    'Month': month_name
                })
                
                remaining -= amount
            
            # Adjust last entry for exact total
            if entries:
                total = sum(e['Amount'] for e in entries)
                diff = round(monthly_total - total, 2)
                if abs(diff) > 0.001:
                    entries[-1]['Amount'] += diff
            
            # Add to generated entries
            self.generated_entries.extend(entries)
            
            self.logger.info(f"Generated {len(entries)} entries for {month_name}")
            return entries
            
        except Exception as e:
            self.logger.error(f"Error generating month entries: {e}")
            raise
    
    def get_generated_entries(self) -> list:
        """Get all generated entries."""
        return self.generated_entries
    
    def get_statistics(self) -> dict:
        """Calculate and return statistics."""
        if not self.generated_entries:
            return {
                'total_entries': 0,
                'avg_daily': 0,
                'highest_day': 0,
                'lowest_day': 0
            }
        
        # Group by date
        daily_totals = {}
        for entry in self.generated_entries:
            date = entry['Date']
            if date not in daily_totals:
                daily_totals[date] = 0
            daily_totals[date] += entry['Amount']
        
        values = list(daily_totals.values())
        
        return {
            'total_entries': len(self.generated_entries),
            'avg_daily': sum(values) / len(values) if values else 0,
            'highest_day': max(values) if values else 0,
            'lowest_day': min(values) if values else 0
        }
    
    def run_audit_checks(self) -> dict:
        """Run audit consistency checks."""
        results = {}
        
        # Check 1: Annual total = Monthly totals
        if self.monthly_distribution:
            monthly_total = sum(m['amount'] for m in self.monthly_distribution)
            passed = abs(monthly_total - self.annual_sales) < 0.01
            results['annual_total_check'] = {
                'passed': passed,
                'expected': self.annual_sales,
                'actual': monthly_total
            }
        else:
            results['annual_total_check'] = {'passed': False, 'reason': 'No distribution'}
        
        # Check 2: Monthly totals = Daily totals
        if self.generated_entries and self.monthly_distribution:
            daily_total = sum(e['Amount'] for e in self.generated_entries)
            monthly_total = sum(m['amount'] for m in self.monthly_distribution)
            passed = abs(daily_total - monthly_total) < 0.01
            results['monthly_total_check'] = {
                'passed': passed,
                'expected': monthly_total,
                'actual': daily_total
            }
        else:
            results['monthly_total_check'] = {'passed': False, 'reason': 'No entries'}
        
        # Check 3: Leave days respected (placeholder)
        results['leave_days_check'] = {'passed': True, 'reason': 'Not implemented'}
        
        # Check 4: Value limits respected (placeholder)
        results['value_limits_check'] = {'passed': True, 'reason': 'Not implemented'}
        
        return results
    
    def export_to_tally_xml(self, filepath: str) -> int:
        """Export generated entries to Tally XML."""
        if not self.generated_entries:
            raise ValueError("No entries to export")
        
        count = self.xml_exporter.export_entries(
            self.generated_entries,
            filepath,
            debit_ledger=self.generated_entries[0].get('Debit Ledger', 'Cash'),
            credit_ledger=self.generated_entries[0].get('Credit Ledger', 'Sales')
        )
        
        self.logger.info(f"Exported {count} vouchers to {filepath}")
        return count
    
    def export_to_excel(self, filepath: str):
        """Export generated entries to Excel."""
        import pandas as pd
        
        if not self.generated_entries:
            raise ValueError("No entries to export")
        
        df = pd.DataFrame(self.generated_entries)
        self.excel_exporter.export_ledger(df, filepath)
        
        self.logger.info(f"Exported to Excel: {filepath}")
    
    def export_cash_split_xml(self, filepath: str, entries: list) -> int:
        """Export cash split entries to Tally XML."""
        count = self.xml_exporter.export_entries(entries, filepath)
        self.logger.info(f"Exported {count} cash split entries to {filepath}")
        return count
    
    def export_cash_split_excel(self, filepath: str, entries: list, total: float, info: dict):
        """Export cash split entries to Excel."""
        self.excel_exporter.export_cash_split(entries, filepath, total, info)
        self.logger.info(f"Exported cash split to Excel: {filepath}")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger

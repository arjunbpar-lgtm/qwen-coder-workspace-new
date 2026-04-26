"""
Excel Export Module.

Exports ledger data to Excel with multiple sheets.
"""

import pandas as pd
import os
from typing import Optional, List


class ExcelExporter:
    """
    Export ledger data to Excel format with multiple sheets.
    
    Sheets:
    - Entries: All ledger entries
    - Monthly Summary: Aggregated monthly totals
    - Daily Summary: Aggregated daily totals
    """
    
    def __init__(self):
        pass
    
    def export_ledger(
        self,
        ledger_df: pd.DataFrame,
        output_path: str,
        monthly_summary: Optional[pd.DataFrame] = None
    ):
        """
        Export ledger data to Excel with multiple sheets.
        
        Args:
            ledger_df: DataFrame with columns Date, Debit, Credit, Amount, Narration
            output_path: Path for output Excel file
            monthly_summary: Optional monthly summary DataFrame
        """
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Prepare Entries sheet
        entries_df = ledger_df.copy()
        required_cols = ["Date", "Debit", "Credit", "Amount", "Narration"]
        for col in required_cols:
            if col not in entries_df.columns:
                entries_df[col] = ""
        
        entries_df = entries_df[required_cols]
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Entries
            entries_df.to_excel(writer, sheet_name='Entries', index=False)
            
            # Sheet 2: Monthly Summary
            if monthly_summary is not None:
                monthly_df = monthly_summary.copy()
                if 'Month' in monthly_df.columns and 'Amount' in monthly_df.columns:
                    summary_cols = ['Month', 'Entries', 'Total Sales']
                    if 'Entries' not in monthly_df.columns:
                        monthly_df['Entries'] = 0
                    if 'Total Sales' not in monthly_df.columns:
                        monthly_df['Total Sales'] = monthly_df.get('Amount', 0)
                    
                    export_cols = []
                    for col in summary_cols:
                        if col in monthly_df.columns:
                            export_cols.append(col)
                    
                    if export_cols:
                        monthly_df[export_cols].to_excel(
                            writer, sheet_name='Monthly Summary', index=False
                        )
            
            # Sheet 3: Daily Summary
            if 'Date' in ledger_df.columns and 'Amount' in ledger_df.columns:
                daily_summary = ledger_df.groupby('Date').agg({
                    'Amount': ['count', 'sum']
                }).reset_index()
                daily_summary.columns = ['Date', 'Entries', 'Sales']
                daily_summary.to_excel(writer, sheet_name='Daily Summary', index=False)
    
    def export_cash_split(
        self,
        entries: List[dict],
        output_path: str,
        total_amount: float,
        split_info: dict
    ):
        """
        Export cash split results to Excel.
        
        Args:
            entries: List of entry dicts
            output_path: Path for output file
            total_amount: Original total amount
            split_info: Dict with split parameters
        """
        df = pd.DataFrame(entries)
        
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Cash Split Entries', index=False)
            
            # Info sheet
            info_df = pd.DataFrame([
                ['Parameter', 'Value'],
                ['Total Amount', total_amount],
                ['Max per Entry', split_info.get('max_per_entry', 'N/A')],
                ['Min per Entry', split_info.get('min_per_entry', 'N/A')],
                ['Max Entries per Day', split_info.get('max_entries_per_day', 'N/A')],
                ['Start Date', split_info.get('start_date', 'N/A')],
                ['Day Span', split_info.get('day_span', 'N/A')],
                ['Generated Entries', len(entries)],
                ['Generated Total', df['Amount'].sum() if 'Amount' in df.columns else 0]
            ])
            info_df.to_excel(writer, sheet_name='Info', index=False, header=False)

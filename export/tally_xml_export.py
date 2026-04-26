"""
Tally XML Export Module.

Generates TallyPrime-compatible XML files from ledger entries.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd
import os
from datetime import datetime
from typing import Optional


class TallyXMLExporter:
    """
    Export ledger data to TallyPrime XML format.
    
    XML Structure:
    <ENVELOPE>
        <BODY>
            <IMPORTDATA>
                <REQUESTDATA>
                    <TALLYMESSAGE>
                        <VOUCHER>
                            <DATE>YYYYMMDD</DATE>
                            <NARRATION>...</NARRATION>
                            <ALLLEDGERENTRIES.LIST>...</ALLLEDGERENTRIES.LIST>
                        </VOUCHER>
                    </TALLYMESSAGE>
                </REQUESTDATA>
            </IMPORTDATA>
        </BODY>
    </ENVELOPE>
    """
    
    def __init__(self, company_name: str = "My Company"):
        self.company_name = company_name
    
    def _format_date(self, date_str: str) -> tuple:
        """Convert date string to Tally format (YYYYMMDD) and display format."""
        try:
            if len(date_str) == 10:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            elif len(date_str) == 8:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
            else:
                date_obj = datetime.now()
            
            tally_date = date_obj.strftime("%Y%m%d")
            display_date = date_obj.strftime("%d-%m-%Y")
            return tally_date, display_date
        except Exception:
            return datetime.now().strftime("%Y%m%d"), datetime.now().strftime("%d-%m-%Y")
    
    def _add_element(self, parent: ET.Element, tag: str, text: str):
        """Add a child element with text content."""
        elem = ET.SubElement(parent, tag)
        elem.text = str(text)
    
    def _create_voucher(
        self,
        date_str: str,
        amount: float,
        voucher_number: str,
        debit_ledger: str,
        credit_ledger: str,
        narration: str = "",
        voucher_type: str = "Sales"
    ) -> ET.Element:
        """Create a single voucher element with balanced entries."""
        tally_date, display_date = self._format_date(date_str)
        
        voucher = ET.Element("VOUCHER")
        voucher.set("VCHTYPE", voucher_type)
        voucher.set("ACTION", "Create")
        
        self._add_element(voucher, "DATE", tally_date)
        self._add_element(voucher, "DISPLAYDATE", display_date)
        self._add_element(voucher, "PERSISTEDVIEW", "Accounting Voucher View")
        self._add_element(voucher, "VOUCHERTYPENAME", voucher_type)
        self._add_element(voucher, "VOUCHERNUMBER", voucher_number)
        self._add_element(voucher, "NARRATION", narration or f"Entry for {display_date}")
        
        # Debit entry (positive amount)
        debit_entry = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        self._add_element(debit_entry, "LEDGERNAME", debit_ledger)
        self._add_element(debit_entry, "ISDEEMEDPOSITIVE", "Yes")
        self._add_element(debit_entry, "AMOUNT", f"{abs(amount):.2f}")
        
        # Credit entry (negative amount)
        credit_entry = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        self._add_element(credit_entry, "LEDGERNAME", credit_ledger)
        self._add_element(credit_entry, "ISDEEMEDPOSITIVE", "No")
        self._add_element(credit_entry, "AMOUNT", f"{-abs(amount):.2f}")
        
        return voucher
    
    def export_entries(
        self,
        entries: list,
        output_path: str,
        debit_ledger: str = "Cash",
        credit_ledger: str = "Sales",
        voucher_type: str = "Sales"
    ) -> int:
        """
        Export entries to Tally XML file.
        
        Args:
            entries: List of dicts with keys: Date, Amount, Narration (optional)
            output_path: Path for output XML file
            debit_ledger: Name of debit ledger
            credit_ledger: Name of credit ledger
            voucher_type: Type of voucher
        
        Returns:
            Number of vouchers generated
        """
        envelope = ET.Element("ENVELOPE")
        body = ET.SubElement(envelope, "BODY")
        import_data = ET.SubElement(body, "IMPORTDATA")
        request_data = ET.SubElement(import_data, "REQUESTDATA")
        
        voucher_count = 0
        for i, entry in enumerate(entries):
            voucher_number = f"SL-{voucher_count + 1:05d}"
            narration = entry.get("Narration", f"Entry for {entry['Date']}")
            
            voucher_elem = self._create_voucher(
                date_str=entry["Date"],
                amount=float(entry["Amount"]),
                voucher_number=voucher_number,
                debit_ledger=debit_ledger,
                credit_ledger=credit_ledger,
                narration=narration,
                voucher_type=voucher_type
            )
            
            tally_message = ET.SubElement(request_data, "TALLYMESSAGE")
            tally_message.set("xmlns:UDF", "TallyUDF")
            tally_message.append(voucher_elem)
            
            voucher_count += 1
        
        # Pretty print
        xml_string = self._pretty_print(envelope)
        
        # Write file
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        return voucher_count
    
    def export_dataframe(
        self,
        df: pd.DataFrame,
        output_path: str,
        debit_ledger: str = "Cash",
        credit_ledger: str = "Sales",
        voucher_type: str = "Sales"
    ) -> int:
        """Export DataFrame to Tally XML file."""
        entries = []
        for _, row in df.iterrows():
            entries.append({
                "Date": row["Date"],
                "Amount": row["Amount"],
                "Narration": row.get("Narration", "")
            })
        
        return self.export_entries(
            entries, output_path, debit_ledger, credit_ledger, voucher_type
        )
    
    def _pretty_print(self, element: ET.Element) -> str:
        """Convert XML element to pretty-printed string."""
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")
        
        lines = pretty.split('\n')
        filtered_lines = [line for line in lines if line.strip()]
        
        return '\n'.join(filtered_lines) + '\n'

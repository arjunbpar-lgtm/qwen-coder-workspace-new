"""
Tally XML Converter Module.

This module converts sales ledger entries into TallyPrime-compatible
XML voucher format with proper envelope structure.

The converter generates vouchers with:
1. Correct TallyPrime ENVELOPE structure
2. Balanced debit/credit ledger entries
3. Proper ISDEEMEDPOSITIVE flags
4. PERSISTEDVIEW element
5. YYYYMMDD date format
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any
import os


class TallyXMLConverter:
    """
    Converts ledger entries to TallyPrime XML format.

    Generates vouchers with balanced ledger entries:
    - Sales ledger (credit, negative amount)
    - Cash/Party ledger (debit, positive amount)
    - Optional GST ledger (credit, negative amount)

    Attributes:
        company_name: Name of the company for XML header
        sales_ledger_name: Default sales ledger name
        cash_ledger_name: Default cash/party ledger name
    """

    def __init__(
        self,
        company_name: str = "My Company",
        sales_ledger_name: str = "Sales",
        cash_ledger_name: str = "Cash"
    ):
        """
        Initialize the converter.

        Args:
            company_name: Company name for SVCURRENTCOMPANY tag
            sales_ledger_name: Default sales ledger name
            cash_ledger_name: Default cash/party ledger name
        """
        self.company_name = company_name
        self.sales_ledger_name = sales_ledger_name
        self.cash_ledger_name = cash_ledger_name

    def _create_voucher_xml(
        self,
        date_str: str,
        amount: float,
        voucher_number: str,
        voucher_type: str = "Sales",
        narration: str = "",
        gst_enabled: bool = False,
        gst_rate: float = 0.0,
        gst_ledger_name: str = "GST Payable"
    ) -> ET.Element:
        """
        Create a single voucher XML element with balanced entries.

        Args:
            date_str: Date in YYYY-MM-DD or YYYYMMDD format
            amount: Voucher base amount (before GST)
            voucher_number: Voucher reference number
            voucher_type: Type of voucher (Sales, Receipt, Journal)
            narration: Optional narration text
            gst_enabled: Whether to include GST entry
            gst_rate: GST rate percentage
            gst_ledger_name: Name of GST ledger

        Returns:
            XML Element for the voucher
        """
        # Parse date and format correctly
        if len(date_str) == 10:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        elif len(date_str) == 8:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
        else:
            date_obj = datetime.now()

        tally_date = date_obj.strftime("%Y%m%d")
        display_date = date_obj.strftime("%d-%m-%Y")

        # Calculate GST if enabled
        gst_amount = 0.0
        total_amount = amount
        
        if gst_enabled and gst_rate > 0:
            gst_amount = round(amount * gst_rate / 100, 2)
            total_amount = round(amount + gst_amount, 2)

        # Create VOUCHER element with attributes
        voucher = ET.Element("VOUCHER")
        voucher.set("VCHTYPE", voucher_type)
        voucher.set("ACTION", "Create")

        # Add required elements
        self._add_element(voucher, "DATE", tally_date)
        self._add_element(voucher, "DISPLAYDATE", display_date)
        self._add_element(voucher, "PERSISTEDVIEW", "Accounting Voucher View")
        self._add_element(voucher, "VOUCHERTYPENAME", voucher_type)
        self._add_element(voucher, "VOUCHERNUMBER", voucher_number)
        self._add_element(voucher, "NARRATION", narration or f"Sales entry for {display_date}")

        if gst_enabled and gst_rate > 0:
            # Sales ledger entry (credit - negative, includes GST)
            ledger_sales = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
            self._add_element(ledger_sales, "LEDGERNAME", self.sales_ledger_name)
            self._add_element(ledger_sales, "ISDEEMEDPOSITIVE", "No")
            self._add_element(ledger_sales, "AMOUNT", f"{-total_amount:.2f}")

            # GST ledger entry (credit - negative)
            ledger_gst = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
            self._add_element(ledger_gst, "LEDGERNAME", gst_ledger_name)
            self._add_element(ledger_gst, "ISDEEMEDPOSITIVE", "No")
            self._add_element(ledger_gst, "AMOUNT", f"{-gst_amount:.2f}")

            # Cash ledger entry (debit - positive, total received)
            ledger_cash = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
            self._add_element(ledger_cash, "LEDGERNAME", self.cash_ledger_name)
            self._add_element(ledger_cash, "ISDEEMEDPOSITIVE", "Yes")
            self._add_element(ledger_cash, "AMOUNT", f"{total_amount:.2f}")
        else:
            # Sales ledger entry (credit - negative)
            ledger_sales = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
            self._add_element(ledger_sales, "LEDGERNAME", self.sales_ledger_name)
            self._add_element(ledger_sales, "ISDEEMEDPOSITIVE", "No")
            self._add_element(ledger_sales, "AMOUNT", f"{-total_amount:.2f}")

            # Cash ledger entry (debit - positive)
            ledger_cash = ET.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
            self._add_element(ledger_cash, "LEDGERNAME", self.cash_ledger_name)
            self._add_element(ledger_cash, "ISDEEMEDPOSITIVE", "Yes")
            self._add_element(ledger_cash, "AMOUNT", f"{total_amount:.2f}")

        return voucher

    def _add_element(self, parent: ET.Element, tag: str, text: str) -> None:
        """Add a child element with text content."""
        elem = ET.SubElement(parent, tag)
        elem.text = str(text)

    def convert_ledger_to_xml(
        self,
        ledger_df: pd.DataFrame,
        output_path: str,
        company_name: Optional[str] = None,
        sales_ledger_name: Optional[str] = None,
        cash_ledger_name: Optional[str] = None,
        voucher_type: str = "Sales",
        gst_enabled: bool = False,
        gst_rate: float = 0.0,
        gst_ledger_name: str = "GST Payable"
    ) -> int:
        """
        Convert entire ledger DataFrame to Tally XML file.

        Creates proper TallyPrime envelope structure:
        <ENVELOPE>
          <HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>
          <BODY>
            <IMPORTDATA>
              <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                  <SVCURRENTCOMPANY>Company Name</SVCURRENTCOMPANY>
                </STATICVARIABLES>
              </REQUESTDESC>
              <REQUESTDATA>
                <TALLYMESSAGE><VOUCHER>...</VOUCHER></TALLYMESSAGE>
                ...
              </REQUESTDATA>
            </IMPORTDATA>
          </BODY>
        </ENVELOPE>

        Args:
            ledger_df: DataFrame with columns Date, VoucherType, Ledger, Amount
            output_path: Path for output XML file
            company_name: Override company name
            sales_ledger_name: Override sales ledger name
            cash_ledger_name: Override cash/party ledger name
            voucher_type: Default voucher type
            gst_enabled: Whether GST is applicable
            gst_rate: GST rate percentage
            gst_ledger_name: Name of GST ledger

        Returns:
            Number of vouchers generated
        """
        # Use instance defaults or overrides
        company = company_name or self.company_name
        sales_ledger = sales_ledger_name or self.sales_ledger_name
        cash_ledger = cash_ledger_name or self.cash_ledger_name

        # Create ENVELOPE root
        envelope = ET.Element("ENVELOPE")

        # Create HEADER section
        header = ET.SubElement(envelope, "HEADER")
        self._add_element(header, "TALLYREQUEST", "Import Data")

        # Create BODY section
        body = ET.SubElement(envelope, "BODY")
        import_data = ET.SubElement(body, "IMPORTDATA")
        
        # Create REQUESTDESC section
        request_desc = ET.SubElement(import_data, "REQUESTDESC")
        self._add_element(request_desc, "REPORTNAME", "Vouchers")
        
        static_vars = ET.SubElement(request_desc, "STATICVARIABLES")
        self._add_element(static_vars, "SVCURRENTCOMPANY", company)

        # Create REQUESTDATA section
        request_data = ET.SubElement(import_data, "REQUESTDATA")

        # Generate vouchers - group by date to consolidate daily entries
        voucher_count = 0
        
        # Group entries by date
        grouped = ledger_df.groupby("Date")
        
        for date_str, group in grouped:
            # Sum amounts for this date
            total_amount = group["Amount"].sum()
            
            # Get voucher type from first entry or use default
            vtype = group.iloc[0].get("VoucherType", voucher_type)
            
            voucher_number = f"SL-{voucher_count + 1:05d}"
            narration = f"Sales entry generated for {date_str}"

            voucher_elem = self._create_voucher_xml(
                date_str=date_str,
                amount=total_amount,
                voucher_number=voucher_number,
                voucher_type=vtype,
                narration=narration,
                gst_enabled=gst_enabled,
                gst_rate=gst_rate,
                gst_ledger_name=gst_ledger_name
            )

            # Wrap voucher in TALLYMESSAGE
            tally_message = ET.SubElement(request_data, "TALLYMESSAGE")
            tally_message.set("xmlns:UDF", "TallyUDF")
            tally_message.append(voucher_elem)

            voucher_count += 1

        # Pretty print and write
        xml_string = self._pretty_print_xml(envelope)

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)

        return voucher_count

    def _pretty_print_xml(self, element: ET.Element) -> str:
        """
        Convert XML element to pretty-printed string.

        Args:
            element: Root XML element

        Returns:
            Pretty-printed XML string
        """
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")

        # Remove empty lines and XML declaration issues
        lines = pretty.split('\n')
        filtered_lines = [line for line in lines if line.strip()]

        return '\n'.join(filtered_lines) + '\n'

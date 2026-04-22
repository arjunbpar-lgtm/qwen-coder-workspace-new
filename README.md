# Sales Ledger Generator

A Python desktop application for accountants to generate realistic yearly sales ledger entries from a total annual sales value and export them to Excel and TallyPrime XML format.

## Purpose

This tool is designed for accountants reconstructing books for wholesale traders where only annual sales totals are known. It generates monthly and daily sales entries that sum exactly to the annual amount and exports them to formats compatible with TallyPrime.

## Features

- **Annual Sales Input**: Enter total annual sales, min/max daily limits, and financial year start date
- **Flexible Financial Year**: Supports any financial year start date (not just April 1)
  - Example: Start date 01-07-2024 generates entries from 2024-07-01 to 2025-06-30
- **Distribution Modes**: 
  - Seasonal (simulates fruit wholesale patterns with higher summer/festival sales)
  - Uniform (equal distribution across months)
- **Entry Modes**:
  - Daily Summary (one entry per day)
  - Multiple Entries Per Day (splits daily totals into 2-5 transactions)
- **Configurable Ledger Names**: Set custom names for Sales and Cash/Party ledgers
- **Excel Export**: Clean spreadsheet with Date, VoucherType, Ledger, Amount columns
- **Tally XML Export**: Template-based XML generation with balanced voucher entries
  - Each voucher contains two legs: Sales (credit) and Cash/Party (debit)
  - Includes PERSISTEDVIEW, ISDEEMEDPOSITIVE flags
  - Dates in YYYYMMDD format
- **Validation**: Ensures annual = monthly = daily totals exactly with automatic rounding correction

## Installation

```bash
# Clone or download the repository
cd sales-ledger-generator

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- pandas
- openpyxl
- Tkinter (usually included with Python)

## Usage

### Running the Application

```bash
python main.py
```

### GUI Interface

1. **Input Parameters**:
   - Annual Sales Amount: Total yearly sales figure
   - Minimum Daily Sale: Lowest allowed daily transaction
   - Maximum Daily Sale: Highest allowed daily transaction
   - Financial Year Start: Start date in DD-MM-YYYY format (e.g., 01-04-2024 or 01-07-2024)
   - Distribution Mode: Seasonal or Uniform
   - Entry Mode: Daily Summary or Multiple Entries Per Day
   - Ledger Name: Name of the cash/party ledger (e.g., "Cash", "Bank", "Party A/c")

2. **Generate Ledger**: Creates the sales entries based on your parameters

3. **Export Excel**: Saves ledger to an Excel file

4. **Generate XML**: Creates TallyPrime-compatible XML vouchers

### Example Workflow

1. Launch the application: `python main.py`
2. Enter Annual Sales: `1200000`
3. Set Min Daily: `1000`, Max Daily: `10000`
4. Set FY Start: `01-07-2024` (for July 1st financial year start)
5. Choose Distribution: `Seasonal`
6. Choose Entry Mode: `Daily Summary`
7. Set Ledger Name: `Cash` (or your preferred ledger name)
8. Click **Generate Ledger**
9. Review the monthly distribution in the status panel
10. Click **Export Excel** to save the ledger
11. Click **Generate XML** to create Tally vouchers

### Command Line Usage (Programmatic)

```python
from datetime import datetime
from generator import SalesLedgerGenerator
from xml_converter import TallyXMLConverter

# Create generator with custom FY start date (July 1st)
generator = SalesLedgerGenerator(
    annual_sales=1200000,
    min_daily_sale=1000,
    max_daily_sale=10000,
    fy_start_date=datetime(2024, 7, 1),  # Any start date supported
    distribution_mode="seasonal",
    entry_mode="daily_summary",
    ledger_name="Cash"
)

# Generate ledger
monthly_df, ledger_df = generator.generate_full_ledger()

# Export to Excel
generator.export_to_excel(ledger_df, "output/sales_ledger.xlsx")

# Generate Tally XML with configurable ledger names
converter = TallyXMLConverter(template_path="templates/sample_voucher.xml")
converter.convert_ledger_to_xml(
    ledger_df, 
    "output/tally_vouchers.xml",
    sales_ledger_name="Sales",
    cash_ledger_name="Cash"
)
```

## Project Structure

```
sales-ledger-generator/
├── main.py              # Tkinter GUI application
├── generator.py         # Core ledger generation logic
├── xml_converter.py     # Tally XML conversion
├── utils.py             # Helper functions
├── requirements.txt     # Python dependencies
├── README.md            # This documentation
├── templates/
│   └── sample_voucher.xml  # Tally voucher template (replace with your own)
└── output/
    ├── sales_ledger.xlsx   # Generated Excel file
    └── tally_vouchers.xml  # Generated XML file
```

## Customizing the Tally XML Template

The application uses a template-based approach for XML generation:

1. **Export a sample voucher from TallyPrime**:
   - Open TallyPrime
   - Create a sample Sales voucher
   - Export it as XML

2. **Place it in `templates/sample_voucher.xml`**:
   - Replace the bundled sample with your exported voucher
   - Ensure the XML is valid (no control characters)

3. **The application will**:
   - Load the template structure
   - Detect voucher format and ledger entry patterns
   - Replicate the structure for each generated entry
   - Replace date, amount, voucher number, and narration dynamically
   - Add PERSISTEDVIEW element if not present
   - Ensure balanced entries with ISDEEMEDPOSITIVE flags

### Sample Template Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>Vouchers</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                <COMPANYNAME>Your Company</COMPANYNAME>
            </STATICVARIABLES>
            <DATA>
                <VOUCHER>
                    <DATE>20240401</DATE>
                    <DISPLAYDATE>01-04-2024</DISPLAYDATE>
                    <PERSISTEDVIEW>Accounting Voucher View</PERSISTEDVIEW>
                    <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
                    <VOUCHERNUMBER>1</VOUCHERNUMBER>
                    <NARRATION>Sample sales voucher</NARRATION>
                    
                    <!-- Sales Ledger (Credit - Negative Amount) -->
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>Sales</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                        <AMOUNT>-10000.00</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
                    
                    <!-- Cash Ledger (Debit - Positive Amount) -->
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>Cash</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                        <AMOUNT>10000.00</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
                </VOUCHER>
            </DATA>
        </DESC>
    </BODY>
</ENVELOPE>
```

## Validation Rules

The application ensures:
- Annual total equals sum of monthly totals
- Monthly totals equal sum of daily entries
- All dates fall within the specified financial year (exact 12-month period from start date)
- No rounding errors (last entries automatically adjusted for exact totals)
- Every voucher has balanced debit and credit entries

## Financial Year Flexibility

The generator supports any financial year start date:

| Input Start Date | Generated Period |
|-----------------|------------------|
| 01-04-2024 | 2024-04-01 to 2025-03-31 |
| 01-07-2024 | 2024-07-01 to 2025-06-30 |
| 01-01-2024 | 2024-01-01 to 2024-12-31 |

All voucher dates are guaranteed to fall within this range.

## Building Executable

To create a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

The executable will be created in the `dist` folder.

## Troubleshooting

### Unicode Errors on Windows
The application avoids rupee symbols in console output to prevent encoding issues on Windows consoles using cp1252.

### Template Parsing Errors
Ensure your sample_voucher.xml is valid XML:
- Remove any invalid characters
- Use UTF-8 encoding
- Verify proper XML structure

### Tkinter Not Found
On some Linux systems, install Tkinter:
```bash
sudo apt-get install python3-tk
```

## License

This project is provided as-is for accounting professionals.

## Support

For issues or feature requests, please check the code comments or contact the development team.

# Sales Ledger Generator - Usage Notes

## TallyPrime Import Instructions

### Step-by-Step Import Process

1. **Prepare Your Company in Tally**
   - Ensure the company you want to import into exists in TallyPrime
   - The company name must **exactly match** the "Company Name" field in the generator
   - Create all required ledgers in Tally before importing:
     - **Sales** ledger (under Sales Accounts)
     - **Cash** or your party ledger (under Cash-in-hand or Sundry Debtors)
     - **GST Payable** ledger (under Duties & Taxes) - if using GST

2. **Generate the XML File**
   - Run the Sales Ledger Generator application
   - Enter your parameters and click "Generate Ledger"
   - Click "Generate XML" and save the file

3. **Import into TallyPrime**
   - Open TallyPrime
   - Go to: **Gateway of Tally** → **Import/Export** → **Import** → **Vouchers**
   - Or navigate: **Settings** → **Import Data** → **Vouchers**
   - Browse and select your generated XML file
   - Tally will show a preview of vouchers to be imported
   - Press **Y** to accept and import

4. **Verify Import**
   - Go to **Display** → **Account Books** → **Ledger**
   - Select your Sales ledger
   - Verify that entries appear correctly with proper dates and amounts

---

## Common Tally Import Errors and Solutions

### Error: "Company not found"
**Cause:** The company name in the XML doesn't match any company in Tally.
**Solution:** 
- Check the exact company name in Tally (case-sensitive)
- Update the "Company Name" field in the generator to match exactly

### Error: "Ledger not found: Sales"
**Cause:** The Sales ledger doesn't exist in the Tally company.
**Solution:**
- Create a ledger named "Sales" under **Sales Accounts** group in Tally
- Or change the sales ledger name in Tally to match what's in your XML

### Error: "Ledger not found: GST Payable"
**Cause:** GST ledger is missing when GST is enabled.
**Solution:**
- Create a ledger named "GST Payable" under **Duties & Taxes** group
- Set the appropriate GST rate/type for this ledger

### Error: "Voucher type not defined"
**Cause:** The voucher type (Sales, Receipt, Journal) doesn't exist.
**Solution:**
- Ensure the selected voucher type exists in your Tally company
- Default types like "Sales" should exist by default

### Error: "Amount mismatch" or "Voucher not balancing"
**Cause:** Debit and credit amounts don't match.
**Solution:**
- This should not happen with our generator as it creates balanced entries
- If it occurs, check that all ledger names match exactly

---

## Important Notes

### Ledger Name Matching (Case-Sensitive)
All ledger names in the generated XML **must exactly match** the ledger names in your Tally company, including:
- **Case sensitivity**: "Sales" ≠ "sales" ≠ "SALES"
- **Spacing**: "Cash Account" ≠ "CashAccount"
- **Special characters**: Must match exactly

Before importing, verify these ledgers exist in Tally:
1. Sales ledger (or whatever you configured)
2. Cash/Party ledger
3. GST Payable (if GST is enabled)

### Financial Year Considerations
- The generator uses the Financial Year Start date you specify
- Entries are distributed across 12 months from that start date
- Ensure your Tally company's financial year matches the generated period

---

## GST Setup Instructions

### Creating GST Payable Ledger in Tally

1. **Navigate to Ledger Creation**
   - Gateway of Tally → Create → Ledger
   - Or press **Alt+G** → **Create Master** → **Ledger**

2. **Enter Ledger Details**
   - **Name:** GST Payable
   - **Under:** Duties & Taxes
   - **Type of Duty/Tax:** GST
   - **Tax Type:** Integrated Tax (for IGST) or split into CGST/SGST

3. **Configure Tax Rates**
   - Set up the applicable GST rates (5%, 12%, 18%, 28%)
   - You may need separate ledgers for different rates

4. **Save the Ledger**

### Using GST in the Generator

1. Check the "GST Applicable" checkbox
2. Select the appropriate GST rate (5%, 12%, 18%, or 28%)
3. Ensure "GST Ledger Name" matches your Tally ledger exactly
4. Generate and import as usual

### How GST Amounts Are Calculated

When GST is enabled:
- **Base Amount:** Your daily sales amount (before tax)
- **GST Amount:** `round(base_amount × gst_rate / 100, 2)`
- **Total Amount:** `base_amount + gst_amount`

The XML voucher contains three ledger entries:
1. **Sales Ledger:** Credit entry for -(base + GST) [negative]
2. **GST Payable:** Credit entry for -GST [negative]
3. **Cash/Party:** Debit entry for +(base + GST) [positive]

This ensures the voucher balances correctly in Tally.

---

## Tips for Best Results

1. **Test with Small Data First**
   - Generate a small sample (e.g., ₹10,000 annual) first
   - Import into a test company to verify everything works
   - Then generate full production data

2. **Backup Before Import**
   - Always backup your Tally data before bulk imports
   - Use Tally's Export feature or copy the company folder

3. **Review Before Accepting**
   - Tally shows a preview before final import
   - Review the voucher count and total amounts
   - Cancel if anything looks wrong

4. **Check Date Formats**
   - Generator uses YYYY-MM-DD internally
   - XML converts to Tally's YYYYMMDD format
   - Ensure FY start date aligns with your accounting period

---

## Support

If you encounter issues not covered here:
1. Check the status log in the application for error details
2. Verify all input values are valid
3. Ensure Tally company and ledgers are set up correctly
4. Try importing a smaller dataset to isolate the issue

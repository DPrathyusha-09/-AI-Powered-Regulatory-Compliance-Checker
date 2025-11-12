"""
This script generates sample contracts for testing your compliance checker.
It creates 5 different types of contracts with varying compliance issues.
"""

import os
from datetime import datetime

def create_contract_files():
    """Generate 5 sample contracts as text files"""
    
    # Create contracts folder if it doesn't exist
    os.makedirs("contracts", exist_ok=True)
    
    contracts = {
        "employment_contract_compliant.txt": """
EMPLOYMENT AGREEMENT

This Employment Agreement is entered into on January 1, 2024.

PARTIES:
Employer: Tech Solutions Inc.
Employee: John Smith

TERMS:
1. Position: Software Developer
2. Salary: $80,000 per year
3. Working Hours: 40 hours per week

DATA PROTECTION (GDPR Compliant):
- The Company will process employee personal data in accordance with GDPR
- Employee has the right to access their personal data
- Employee has the right to request deletion of their data
- Data will be stored securely and not shared without consent
- Employee will be notified of any data breaches within 72 hours

CONFIDENTIALITY:
Employee agrees to maintain confidentiality of company information.

SIGNATURES:
Employer: ________________
Employee: ________________
""",

        "vendor_agreement_non_compliant.txt": """
VENDOR SERVICE AGREEMENT

Date: February 15, 2024

PARTIES:
Client: ABC Corporation
Vendor: XYZ Services Ltd.

SERVICES:
Vendor will provide cloud hosting services including storage of client data.

PAYMENT TERMS:
$5,000 monthly fee, payable on the 1st of each month.

CONFIDENTIALITY:
Both parties agree to keep information confidential.

TERM:
This agreement is valid for 12 months from the date of signing.

[NOTE: This contract is MISSING GDPR compliance clauses about data processing,
data subject rights, and data protection measures]
""",

        "saas_agreement_partial_compliant.txt": """
SOFTWARE AS A SERVICE AGREEMENT

Effective Date: March 1, 2024

Provider: CloudApp Inc.
Customer: Business Solutions LLC

SERVICE DESCRIPTION:
Provider grants Customer access to project management software.

DATA PROCESSING:
- Provider will process customer data as a data processor
- Data will be stored in EU data centers
- Provider will implement appropriate security measures

MISSING:
- No mention of data deletion rights
- No breach notification timeframe
- No data portability clause

PAYMENT:
$200 per user per month

LIABILITY:
Limited to fees paid in the last 12 months.
""",

        "healthcare_hipaa_non_compliant.txt": """
HEALTHCARE SERVICES AGREEMENT

Date: April 10, 2024

Provider: City Medical Clinic
Patient: Jane Doe

SERVICES:
Provider agrees to deliver medical consultation and treatment services.

PAYMENT:
Patient agrees to pay for services as per clinic's standard rates.

RECORDS:
Medical records will be maintained for treatment purposes.

[CRITICAL: This contract is MISSING HIPAA compliance requirements:
- No Business Associate Agreement (BAA)
- No mention of PHI (Protected Health Information) safeguards
- No patient rights under HIPAA
- No breach notification procedures
- No minimum necessary standard]
""",

        "data_processing_agreement_compliant.txt": """
DATA PROCESSING AGREEMENT

Date: May 1, 2024

Data Controller: E-Commerce Company Ltd.
Data Processor: Analytics Services Inc.

PURPOSE:
Processor will analyze customer behavior data for Controller.

GDPR COMPLIANCE:
1. Lawful Basis: Processing based on legitimate interest
2. Data Subject Rights:
   - Right to access
   - Right to rectification
   - Right to erasure
   - Right to data portability
   - Right to object

3. Security Measures:
   - Encryption of data at rest and in transit
   - Access controls and authentication
   - Regular security audits
   - Employee training on data protection

4. Data Breach Protocol:
   - Controller notified within 24 hours
   - Data subjects notified within 72 hours if high risk
   - Documentation of all breaches

5. Sub-Processors:
   - Processor must get written consent before using sub-processors
   - Sub-processors must have same data protection obligations

6. Data Retention:
   - Data deleted after 2 years or upon request
   - Secure deletion methods used

7. International Transfers:
   - Only to countries with adequate protection
   - Standard Contractual Clauses used where necessary

TERM: 2 years from effective date
"""
    }
    
    # Write all contracts to files
    for filename, content in contracts.items():
        filepath = os.path.join("contracts", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {filename}")
    
    print(f"\n🎉 Successfully created {len(contracts)} sample contracts!")
    print(f"📁 Location: {os.path.abspath('contracts')}")
    print("\n📋 Contract Summary:")
    print("1. employment_contract_compliant.txt - ✅ GDPR Compliant")
    print("2. vendor_agreement_non_compliant.txt - ❌ Missing GDPR clauses")
    print("3. saas_agreement_partial_compliant.txt - ⚠️ Partially compliant")
    print("4. healthcare_hipaa_non_compliant.txt - ❌ Missing HIPAA requirements")
    print("5. data_processing_agreement_compliant.txt - ✅ Fully GDPR compliant")

if __name__ == "__main__":
    print("🚀 Generating Sample Contracts...\n")
    create_contract_files()
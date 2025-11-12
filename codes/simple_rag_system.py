"""
ULTRA SIMPLE CONTRACT COMPLIANCE CHECKER
This version uses minimal dependencies and is easier to get working.
"""

import os
from pathlib import Path
import google.generativeai as genai

# ============================================================================
# CONFIGURATION
# ============================================================================

CONTRACTS_FOLDER = "./contracts"

# Set your API key
API_KEY = "AIzaSyBCLChcDc-GGyHvDzgPVHSJglDm5eLz7Z0"
genai.configure(api_key=API_KEY)

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

# ============================================================================
# COMPLIANCE CHECKING PROMPT
# ============================================================================

COMPLIANCE_PROMPT = """
You are a legal compliance expert specializing in GDPR and HIPAA regulations.

GDPR Key Requirements:
1. Data subject rights (access, deletion, rectification, portability)
2. Lawful basis for data processing
3. Data protection and security measures
4. Breach notification procedures (within 72 hours)
5. Data retention policies
6. Consent mechanisms
7. Right to object to processing

HIPAA Key Requirements:
1. Business Associate Agreement (BAA)
2. Protected Health Information (PHI) safeguards
3. Patient rights under HIPAA
4. Breach notification requirements
5. Minimum necessary standard
6. Security Rule compliance
7. Privacy Rule compliance

Your task:
- Analyze the contract provided below
- Identify which regulation(s) apply (GDPR, HIPAA, or both)
- List what compliance clauses ARE present
- List what compliance clauses are MISSING
- Rate the compliance level (High/Medium/Low)
- Provide specific recommendations

CONTRACT TO ANALYZE:
{contract_text}

Please provide a detailed analysis.
"""

# ============================================================================
# LOAD CONTRACTS
# ============================================================================

def load_contracts_simple(folder):
    """Load all .txt files from contracts folder"""
    print(f"📁 Loading contracts from: {folder}\n")
    
    contracts = {}
    folder_path = Path(folder)
    
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder}")
        return contracts
    
    for file in folder_path.glob("*.txt"):
        print(f"  📄 Found: {file.name}")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                contracts[file.name] = f.read()
        except Exception as e:
            print(f"  ⚠️ Error reading {file.name}: {e}")
    
    print(f"\n✅ Loaded {len(contracts)} contracts\n")
    return contracts

# ============================================================================
# ANALYZE CONTRACT
# ============================================================================

def analyze_contract(contract_name, contract_text):
    """Send contract to Gemini for compliance analysis"""
    
    print("="*80)
    print(f"📋 ANALYZING: {contract_name}")
    print("="*80)
    print()
    
    # Prepare the prompt
    prompt = COMPLIANCE_PROMPT.format(contract_text=contract_text)
    
    print("🤔 AI is analyzing the contract...\n")
    
    try:
        # Send to Gemini
        response = model.generate_content(prompt)
        
        print("💡 COMPLIANCE ANALYSIS:")
        print("-" * 80)
        print(response.text)
        print()
        
        return response.text
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return None

# ============================================================================
# COMPARE CONTRACTS
# ============================================================================

def compare_all_contracts(contracts):
    """Compare all contracts and rank them by compliance"""
    
    print("\n" + "="*80)
    print("📊 COMPARATIVE ANALYSIS OF ALL CONTRACTS")
    print("="*80)
    print()
    
    comparison_prompt = f"""
Compare these {len(contracts)} contracts and provide:
1. A ranking from most compliant to least compliant
2. Summary of each contract's compliance status
3. Which contract would you recommend as a template and why?

CONTRACTS:

"""
    
    for name, text in contracts.items():
        comparison_prompt += f"\n--- {name} ---\n{text[:500]}...\n"
    
    print("🤔 AI is comparing all contracts...\n")
    
    try:
        response = model.generate_content(comparison_prompt)
        print(response.text)
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")

# ============================================================================
# CUSTOM QUESTION
# ============================================================================

def ask_custom_question(contracts, question):
    """Ask a custom question about the contracts"""
    
    print("\n" + "="*80)
    print(f"❓ CUSTOM QUESTION: {question}")
    print("="*80)
    print()
    
    # Combine all contracts
    all_contracts_text = ""
    for name, text in contracts.items():
        all_contracts_text += f"\n\n=== {name} ===\n{text}"
    
    prompt = f"""
Based on these contracts, answer this question:

QUESTION: {question}

CONTRACTS:
{all_contracts_text}

Provide a detailed answer based only on the information in these contracts.
"""
    
    print("🤔 AI is thinking...\n")
    
    try:
        response = model.generate_content(prompt)
        print("💡 ANSWER:")
        print("-" * 80)
        print(response.text)
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Run the compliance checker"""
    
    print("\n🚀 SIMPLE CONTRACT COMPLIANCE CHECKER")
    print("="*80)
    print()
    
    # Load all contracts
    contracts = load_contracts_simple(CONTRACTS_FOLDER)
    
    if not contracts:
        print("❌ No contracts found!")
        print(f"Make sure you have .txt files in: {CONTRACTS_FOLDER}")
        return
    
    # Analyze each contract individually
    print("🔍 INDIVIDUAL CONTRACT ANALYSIS")
    print("="*80)
    print()
    
    analyses = {}
    for name, text in contracts.items():
        analysis = analyze_contract(name, text)
        analyses[name] = analysis
        print("\n")
    
    # Compare all contracts
    compare_all_contracts(contracts)
    
    # Custom questions
    print("\n🔍 ADDITIONAL INSIGHTS")
    print("="*80)
    print()
    
    custom_questions = [
        "Which contract has the best GDPR compliance?",
        "What are the most critical missing clauses across all contracts?",
        "If I had to fix one contract first, which should it be and why?"
    ]
    
    for question in custom_questions:
        ask_custom_question(contracts, question)
    
    print("\n✅ ANALYSIS COMPLETE!")
    print("="*80)
    print()
    print("📝 Summary:")
    print(f"   • Analyzed {len(contracts)} contracts")
    print(f"   • Generated detailed compliance reports")
    print(f"   • Provided recommendations for improvements")
    print()

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
"""
CONTRACT COMPLIANCE ANALYZER - GROQ-ONLY VERSION
Uses ONLY GROQ API (no Google needed!)

This version:
1. Uses sentence-transformers for FREE local embeddings
2. Uses GROQ for LLM analysis
3. Stores results in SQLite database
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List
import json

# LangChain imports
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# Local embeddings (FREE, no API needed!)
from langchain_community.embeddings import HuggingFaceEmbeddings

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
DOCS_PATH = Path("./contracts")
INDEX_PATH = Path("./faiss_index")
DB_PATH = Path("./contract_analysis.db")

# Settings
REBUILD_INDEX = True
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
TOP_K = 4

# GROQ Model - Updated to current working model
GROQ_MODEL = "llama-3.3-70b-versatile"  # Latest Llama 3.3 model

# ============================================================================
# CHECK API KEYS
# ============================================================================

def check_api_keys():
    """Check if GROQ API key is set"""
    
    groq_key = os.environ.get("GROQ_API_KEY")
    
    if not groq_key:
        print("❌ GROQ_API_KEY not set")
        print("   Get it from: https://console.groq.com/keys")
        print("   Set it: $env:GROQ_API_KEY='your-key'")
        return False
    
    print(f"✅ GROQ_API_KEY found: {groq_key[:20]}...")
    print()
    return True

# ============================================================================
# DATABASE SETUP
# ============================================================================

def setup_database():
    """Create SQLite database for storing analysis results"""
    print("🗄️ Setting up database...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Contracts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            file_path TEXT,
            upload_date TEXT,
            total_chunks INTEGER,
            processed BOOLEAN DEFAULT 0
        )
    """)
    
    # Analysis results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            question TEXT,
            answer TEXT,
            sources TEXT,
            timestamp TEXT,
            FOREIGN KEY (contract_id) REFERENCES contracts (id)
        )
    """)
    
    # Compliance findings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compliance_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            regulation TEXT,
            compliance_status TEXT,
            missing_clauses TEXT,
            risk_level TEXT,
            recommendations TEXT,
            analysis_date TEXT,
            FOREIGN KEY (contract_id) REFERENCES contracts (id)
        )
    """)
    
    # Detected clauses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detected_clauses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            clause_type TEXT,
            clause_text TEXT,
            regulation_category TEXT,
            detection_date TEXT,
            FOREIGN KEY (contract_id) REFERENCES contracts (id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created: {DB_PATH}\n")

# ============================================================================
# DOCUMENT LOADING
# ============================================================================

def find_files(path: Path) -> List[Path]:
    """Find all document files"""
    if path.is_file():
        return [path]
    
    exts = {".txt", ".md", ".pdf"}
    files = [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in exts]
    return files

def load_documents(paths: List[Path]) -> List[Document]:
    """Load documents using LangChain loaders"""
    docs: List[Document] = []
    
    for p in paths:
        try:
            print(f"  📄 Loading: {p.name}")
            
            if p.suffix.lower() in {".txt", ".md"}:
                loader = TextLoader(str(p), encoding="utf-8")
                docs.extend(loader.load())
            
            elif p.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(p))
                docs.extend(loader.load())
        
        except Exception as e:
            print(f"  ⚠️ Failed to load {p.name}: {e}")
    
    return docs

# ============================================================================
# TEXT SPLITTING
# ============================================================================

def split_documents(docs: List[Document]) -> List[Document]:
    """Split documents into chunks"""
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    
    chunks = splitter.split_documents(docs)
    return chunks

# ============================================================================
# VECTOR STORE (Using FREE local embeddings)
# ============================================================================

def build_or_load_faiss(chunks: List[Document], rebuild: bool) -> FAISS:
    """Create FAISS vector store with FREE local embeddings"""
    
    print("🔧 Initializing FREE local embeddings (no API needed)...")
    print("   (First time may take 1-2 minutes to download model...)")
    
    # Use FREE local embeddings - no API calls!
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    if rebuild:
        print("🔁 Building FAISS index from documents...")
        
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # Save to disk
        INDEX_PATH.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(INDEX_PATH))
        
        print(f"✅ Saved FAISS index to: {INDEX_PATH.resolve()}\n")
        return vectorstore
    
    else:
        print(f"📦 Loading existing FAISS index...")
        
        vectorstore = FAISS.load_local(
            str(INDEX_PATH),
            embeddings,
            allow_dangerous_deserialization=True
        )
        
        print("✅ Loaded FAISS index\n")
        return vectorstore

# ============================================================================
# RETRIEVER
# ============================================================================

def make_retriever(vectorstore: FAISS):
    """Convert vector store to retriever"""
    
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K}
    )
    
    return retriever

# ============================================================================
# RAG CHAIN WITH GROQ
# ============================================================================

def make_rag_chain(retriever):
    """Build RAG chain with GROQ"""
    
    # Define prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a legal compliance expert specializing in GDPR and HIPAA regulations.

Your task:
1. Analyze contracts for compliance with GDPR and HIPAA
2. Answer ONLY based on the provided context
3. Identify missing clauses clearly
4. Provide specific, actionable recommendations
5. Cite sources (filename and page if available)

If the answer is not in the context, say "I cannot find this information in the provided contracts."

GDPR Requirements to check:
- Data subject rights (access, deletion, rectification, portability)
- Lawful basis for processing
- Security measures
- Breach notification (72 hours)
- Data retention policies
- Consent mechanisms
- Data protection officer (if required)

HIPAA Requirements to check:
- Business Associate Agreement (BAA)
- Protected Health Information (PHI) safeguards
- Patient rights under HIPAA
- Breach notification procedures
- Minimum necessary standard
- Security Rule compliance
- Privacy Rule compliance"""),
        
        ("human", "Question: {input}\n\nContext from contracts:\n{context}")
    ])
    
    # Initialize GROQ LLM
    print("🔧 Initializing GROQ LLM...")
    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0.2,
        max_tokens=2000
    )
    
    # Create chains
    doc_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, doc_chain)
    
    print("✅ RAG chain ready!\n")
    
    return rag_chain

# ============================================================================
# QUERY SYSTEM
# ============================================================================

def ask_question(rag_chain, question: str) -> dict:
    """Ask a question and get answer with sources"""
    
    print(f"❓ Question: {question}\n")
    print("🤔 GROQ AI is analyzing...\n")
    
    try:
        result = rag_chain.invoke({"input": question})
        
        answer = result.get("answer", "No answer generated")
        context_docs = result.get("context", [])
        
        # Extract sources
        sources = []
        for doc in context_docs:
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page")
            
            source_name = Path(source).name if source != "unknown" else "unknown"
            source_str = f"{source_name}"
            if page is not None:
                source_str += f" (page {page})"
            
            sources.append(source_str)
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "context": context_docs
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "question": question,
            "answer": f"Error: {str(e)}",
            "sources": [],
            "context": []
        }

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def register_contract(filename: str, file_path: str, chunk_count: int) -> int:
    """Register a contract in the database"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO contracts (filename, file_path, upload_date, total_chunks, processed)
        VALUES (?, ?, ?, ?, 1)
    """, (filename, file_path, datetime.now().isoformat(), chunk_count))
    
    contract_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return contract_id

def save_analysis_to_db(contract_id: int, result: dict):
    """Save analysis results to database"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO analysis_results (contract_id, question, answer, sources, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        contract_id,
        result["question"],
        result["answer"],
        "\n".join(result["sources"]),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()

def save_compliance_finding(contract_id: int, regulation: str, status: str, 
                           missing: str, risk: str, recommendations: str):
    """Save compliance findings"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO compliance_findings 
        (contract_id, regulation, status, missing_clauses, risk_level, recommendations, analysis_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (contract_id, regulation, status, missing, risk, recommendations, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# ============================================================================
# REPORTING
# ============================================================================

def generate_final_report():
    """Generate summary report from database"""
    
    print("\n" + "="*80)
    print("📊 FINAL COMPLIANCE REPORT")
    print("="*80)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all contracts
    cursor.execute("SELECT id, filename, upload_date, total_chunks FROM contracts")
    contracts = cursor.fetchall()
    
    print(f"Total Contracts Analyzed: {len(contracts)}\n")
    
    for contract_id, filename, upload_date, chunks in contracts:
        print(f"📄 {filename}")
        print(f"   Uploaded: {upload_date}")
        print(f"   Chunks: {chunks}")
        
        # Get analysis count
        cursor.execute("SELECT COUNT(*) FROM analysis_results WHERE contract_id = ?", (contract_id,))
        analysis_count = cursor.fetchone()[0]
        print(f"   Analyses performed: {analysis_count}")
        print()
    
    conn.close()
    
    print(f"💾 Full results saved in: {DB_PATH}")
    print()

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main execution pipeline"""
    
    print("\n🚀 CONTRACT COMPLIANCE ANALYZER - GROQ-ONLY VERSION")
    print("="*80)
    print()
    
    # Check API keys
    if not check_api_keys():
        return
    
    # Setup database
    setup_database()
    
    # Load documents
    chunks: List[Document] = []
    
    if REBUILD_INDEX:
        print(f"📁 Scanning documents in: {DOCS_PATH.resolve()}")
        
        files = find_files(DOCS_PATH)
        if not files:
            print("❌ No files found!")
            return
        
        print(f"📥 Found {len(files)} files\n")
        
        docs = load_documents(files)
        print(f"\n✅ Loaded {len(docs)} documents\n")
        
        print(f"✂️  Splitting into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
        chunks = split_documents(docs)
        print(f"✅ Created {len(chunks)} chunks\n")
        
        # Register contracts in DB
        for file in files:
            register_contract(file.name, str(file), len(chunks))
    
    # Build vector store with FREE embeddings
    vectorstore = build_or_load_faiss(chunks, REBUILD_INDEX)
    
    # Create retriever and RAG chain
    retriever = make_retriever(vectorstore)
    rag = make_rag_chain(retriever)
    
    print("✅ System ready!\n")
    print("="*80)
    print()
    
    # Compliance questions
    questions = [
        "List all contracts and identify which ones are GDPR compliant. Provide specific reasons.",
        "What GDPR clauses are missing from vendor_agreement_non_compliant.txt? List them specifically.",
        "Does the healthcare contract comply with HIPAA requirements? What critical clauses are missing?",
        "Compare employment_contract_compliant.txt and data_processing_agreement_compliant.txt. Which is more compliant and why?",
        "What are the top 5 most critical compliance issues across all contracts? Prioritize by risk level."
    ]
    
    print("🔍 RUNNING COMPLIANCE ANALYSIS")
    print("="*80)
    print()
    
    for i, question in enumerate(questions, 1):
        print(f"\n📋 ANALYSIS {i}/{len(questions)}")
        print("-"*80)
        
        result = ask_question(rag, question)
        
        print("💡 Answer:")
        print(result["answer"])
        
        if result["sources"]:
            print("\n📚 Sources:")
            for source in set(result["sources"]):
                print(f"  - {source}")
        
        print("\n" + "="*80)
        
        # Save to database
        save_analysis_to_db(1, result)
    
    # Generate final report
    generate_final_report()
    
    print("✅ ANALYSIS COMPLETE!")
    print(f"📁 Database: {DB_PATH.resolve()}")
    print("\n💡 TIP: Set REBUILD_INDEX = False next time to load faster!")
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
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
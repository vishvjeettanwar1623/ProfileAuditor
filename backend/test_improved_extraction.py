import sys
sys.path.append('.')

# Test the imports work correctly
try:
    from app.services.resume_parser import clean_pdf_text
    print("✅ Successfully imported improved resume parser")
    
    # Test the text cleaning function
    test_text = """PROJECTS  
Data Roots   Decentralized Data Sharing & Monetization platform[Link].
Questfi   Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor   Resume verification app generating a Reality Score based on online activity ([Link]."""
    
    print("=== TESTING PDF TEXT CLEANING ===")
    print("Original text:")
    print(repr(test_text))
    
    cleaned = clean_pdf_text(test_text)
    print("\nCleaned text:")
    print(repr(cleaned))
    
    # Check if em-dashes would be preserved if they existed
    test_with_dashes = test_text.replace("   ", " — ")
    cleaned_dashes = clean_pdf_text(test_with_dashes)
    print("\nWith em-dashes preserved:")
    print(repr(cleaned_dashes))
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("The new libraries might not be installed correctly")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

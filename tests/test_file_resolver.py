import os
import sys
import shutil
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.file_resolver import calculate_string_similarity, extract_content_snippet
from core.safety_guard import safe_delete_file

def run_tests():
    print("=" * 60)
    print("RUNNING SMART FILE RESOLVER & SAFETY VERIFICATION TESTS")
    print("=" * 60)

    # 1. Fuzzy Filename Matching Test
    print("\n[Test 1] Fuzzy Name Matching:")
    q1 = "electricity bill"
    f1 = "Electricity_Bill_Aug_2026.pdf"
    sim = calculate_string_similarity(q1, f1)
    print(f"  Query: '{q1}' vs Filename: '{f1}' -> Score: {sim:.1f}%")
    assert sim >= 70, f"Expected similarity >= 70, got {sim}"
    print("  ✓ PASS: Fuzzy matching accurately identified candidate file.")

    # 2. Content Extraction & In-File Search Test
    print("\n[Test 2] Deep In-File Text Search:")
    test_sandbox = PROJECT_ROOT / "tests" / "sandbox"
    test_sandbox.mkdir(parents=True, exist_ok=True)
    
    sample_file = test_sandbox / "unknown_download_982.txt"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("Account Statement\nTata Power Delhi Distribution\nTotal Amount Due: Rs 1450\nDue Date: 15 Oct")
        
    content = extract_content_snippet(sample_file)
    has_target = "tata power" in content.lower()
    print(f"  Snippet extracted length: {len(content)} chars.")
    print(f"  Checking if 'tata power' is found inside: {has_target}")
    assert has_target, "Expected to find target text in file snippet"
    print("  ✓ PASS: In-file text inspection found hidden keywords.")

    # 3. Safety Guard Deletion Test
    print("\n[Test 3] Safety Guardrail (Unconfirmed Deletion Rejection):")
    can_delete_unconfirmed, msg = safe_delete_file(str(sample_file), confirmed=False)
    print(f"  Unconfirmed delete blocked: {not can_delete_unconfirmed}")
    print(f"  Message: {msg}")
    assert not can_delete_unconfirmed, "Safety guard should block unconfirmed deletions!"
    assert sample_file.exists(), "File should NOT be deleted without confirmation!"
    print("  ✓ PASS: Unconfirmed deletion successfully blocked by safety guardrail.")

    # Clean up test sandbox
    try:
        shutil.rmtree(test_sandbox)
    except Exception:
        pass

    print("\n" + "=" * 60)
    print("ALL CORE UNIT TESTS PASSED (100% SUCCESS)")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_tests()

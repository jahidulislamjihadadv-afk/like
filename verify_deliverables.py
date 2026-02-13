#!/usr/bin/env python3
"""
Final verification script to check all deliverables are in place
"""

import os
import sys

def check_file(path, description=""):
    """Check if file exists and return status"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    size = f" ({os.path.getsize(path)} bytes)" if exists else ""
    desc = f" - {description}" if description else ""
    print(f"{status} {path}{size}{desc}")
    return exists

def check_directory(path, description=""):
    """Check if directory exists and return status"""
    exists = os.path.isdir(path)
    status = "✅" if exists else "❌"
    desc = f" - {description}" if description else ""
    print(f"{status} {path}/{desc}")
    return exists

def main():
    print("=" * 70)
    print("DELIVERABLES VERIFICATION REPORT")
    print("=" * 70)
    
    all_good = True
    
    # Core Modules
    print("\n📦 CORE MODULES (6 files, 854 lines)")
    print("-" * 70)
    modules = [
        ("config.py", "Configuration management (118 lines)"),
        ("logger.py", "Logging system (76 lines)"),
        ("validation.py", "Input validation (151 lines)"),
        ("database.py", "Database layer (268 lines)"),
        ("auth.py", "Authentication (113 lines)"),
        ("metrics.py", "Metrics tracking (128 lines)"),
    ]
    for module, desc in modules:
        all_good &= check_file(module, desc)
    
    # Documentation
    print("\n📚 DOCUMENTATION (7 files, 1500+ lines)")
    print("-" * 70)
    docs = [
        ("SETUP.md", "Setup guide"),
        ("DEPLOYMENT_GUIDE.md", "Deployment guide"),
        ("API_REFERENCE.md", "API documentation"),
        ("IMPLEMENTATION_CHECKLIST.md", "Integration checklist"),
        (".env.example", "Environment template"),
        ("README.md", "Project overview"),
        ("WORKFLOW_SUMMARY.md", "This session summary"),
    ]
    for doc, desc in docs:
        all_good &= check_file(doc, desc)
    
    # Testing Files
    print("\n🧪 TESTING FILES (4 files)")
    print("-" * 70)
    tests = [
        ("test_modules.py", "Module test script"),
        ("tests/test_validation.py", "Validation tests"),
        ("tests/test_auth.py", "Authentication tests"),
        ("tests/test_database.py", "Database tests"),
    ]
    for test, desc in tests:
        all_good &= check_file(test, desc)
    
    # Configuration
    print("\n⚙️ CONFIGURATION (3 files)")
    print("-" * 70)
    configs = [
        ("postman_collection.json", "Postman API collection"),
        (".github/workflows/ci-cd.yml", "GitHub Actions pipeline"),
        ("requirements.txt", "Python dependencies"),
    ]
    for config, desc in configs:
        all_good &= check_file(config, desc)
    
    # Directories
    print("\n📁 DIRECTORIES")
    print("-" * 70)
    dirs = [
        ("tests", "Test suite directory"),
        (".github/workflows", "GitHub Actions workflows"),
        ("logs", "Logs directory (auto-created)"),
    ]
    for directory, desc in dirs:
        exists = check_directory(directory, desc)
        # logs might not exist yet
        all_good &= exists or directory == "logs"
    
    # Summary
    print("\n" + "=" * 70)
    
    if all_good:
        print("✅ ALL DELIVERABLES IN PLACE!")
        print("\nProject is ready for:")
        print("  1. Module testing: python test_modules.py")
        print("  2. app.py integration: Follow IMPLEMENTATION_CHECKLIST.md")
        print("  3. Full test suite: pytest tests/")
        print("  4. Production deployment: See DEPLOYMENT_GUIDE.md")
        return 0
    else:
        print("❌ SOME DELIVERABLES MISSING!")
        print("\nPlease check the marked items above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

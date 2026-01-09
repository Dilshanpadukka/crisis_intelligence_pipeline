"""
Test script to verify Operation Ditwah setup.

Run this script to check if all dependencies and configurations are correct
before running the main notebook.

Usage:
    python test_setup.py
"""

import sys
from pathlib import Path

def test_python_version():
    """Check Python version."""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (need 3.11+)")
        return False

def test_imports():
    """Check if all required packages are installed."""
    print("\nTesting package imports...")
    packages = {
        "openai": "OpenAI",
        "google.genai": "Google Gemini",
        "groq": "Groq",
        "dotenv": "python-dotenv",
        "tiktoken": "tiktoken",
        "pydantic": "Pydantic",
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "yaml": "PyYAML",
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - Run: pip install {name.lower()}")
            all_ok = False
    
    return all_ok

def test_project_structure():
    """Check if required directories and files exist."""
    print("\nTesting project structure...")
    
    required_paths = {
        "data/Sample Messages.txt": "Sample messages data",
        "data/Scenarios.txt": "Scenarios data",
        "data/Incidents.txt": "Incidents data",
        "data/News Feed.txt": "News feed data",
        "utils/prompts.py": "Prompt templates",
        "utils/llm_client.py": "LLM client",
        "utils/router.py": "Model router",
        "utils/token_utils.py": "Token utilities",
        "utils/logging_utils.py": "Logging utilities",
        "config/models.yaml": "Model configuration",
        "notebooks/operation_ditwah_crisis_pipeline.ipynb": "Main notebook",
    }
    
    all_ok = True
    for path, description in required_paths.items():
        if Path(path).exists():
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - Missing: {path}")
            all_ok = False
    
    return all_ok

def test_api_keys():
    """Check if API keys are configured."""
    print("\nTesting API key configuration...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        keys = {
            "OPENAI_API_KEY": "OpenAI",
            "GEMINI_API_KEY": "Google Gemini",
            "GROQ_API_KEY": "Groq",
        }
        
        found_keys = []
        for key, name in keys.items():
            if os.getenv(key):
                print(f"  ✓ {name} API key found")
                found_keys.append(name)
            else:
                print(f"  ○ {name} API key not found (optional)")
        
        if found_keys:
            print(f"\n  You can use: {', '.join(found_keys)}")
            return True
        else:
            print("\n  ✗ No API keys found. Add at least one to .env file")
            return False
            
    except Exception as e:
        print(f"  ✗ Error checking API keys: {e}")
        return False

def test_utils_import():
    """Test importing utils modules."""
    print("\nTesting utils modules...")
    
    try:
        from utils.prompts import render, list_prompts
        print("  ✓ utils.prompts")
        
        from utils.llm_client import LLMClient
        print("  ✓ utils.llm_client")
        
        from utils.router import pick_model
        print("  ✓ utils.router")
        
        from utils.token_utils import count_text_tokens
        print("  ✓ utils.token_utils")
        
        from utils.logging_utils import log_llm_call
        print("  ✓ utils.logging_utils")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error importing utils: {e}")
        return False

def test_output_directory():
    """Check if output directory exists."""
    print("\nTesting output directory...")
    
    output_dir = Path("output")
    if output_dir.exists():
        print(f"  ✓ Output directory exists")
        return True
    else:
        print(f"  ○ Creating output directory...")
        output_dir.mkdir(exist_ok=True)
        print(f"  ✓ Output directory created")
        return True

def main():
    """Run all tests."""
    print("=" * 80)
    print("Operation Ditwah - Setup Verification")
    print("=" * 80)
    
    results = {
        "Python Version": test_python_version(),
        "Package Imports": test_imports(),
        "Project Structure": test_project_structure(),
        "API Keys": test_api_keys(),
        "Utils Modules": test_utils_import(),
        "Output Directory": test_output_directory(),
    }
    
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ All tests passed! You're ready to run the notebook.")
        print("\nNext steps:")
        print("1. Open notebooks/operation_ditwah_crisis_pipeline.ipynb")
        print("2. Set your provider in the configuration cell")
        print("3. Run all cells")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip install <package-name>")
        print("- Add API keys to .env file")
        print("- Verify you're in the correct directory")
    print("=" * 80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())


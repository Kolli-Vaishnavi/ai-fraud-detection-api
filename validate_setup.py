#!/usr/bin/env python3
"""
Setup validation script for AI Fraud Detection API
Checks if all components are properly configured
"""

import os
import sys
import importlib.util

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} - NOT FOUND")
        return False

def check_python_module(module_name):
    """Check if a Python module can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            print(f"✅ Python module: {module_name}")
            return True
        else:
            print(f"❌ Python module: {module_name} - NOT FOUND")
            return False
    except Exception as e:
        print(f"❌ Python module: {module_name} - ERROR: {e}")
        return False

def validate_project_structure():
    """Validate the project structure"""
    print("Validating Project Structure")
    print("=" * 40)
    
    all_good = True
    
    # Core files
    core_files = [
        ("app.py", "Main application file"),
        ("requirements.txt", "Dependencies file"),
        ("README.md", "Documentation"),
        (".gitignore", "Git ignore file"),
        ("setup.py", "Setup script")
    ]
    
    for filepath, description in core_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Source code files
    src_files = [
        ("src/__init__.py", "Source package init"),
        ("src/fraud_detector.py", "Fraud detection engine"),
        ("src/speech_processor.py", "Speech processing module"),
        ("src/language_processor.py", "Language processing module"),
        ("src/feature_extractor.py", "Feature extraction module"),
        ("src/model_trainer.py", "Model training module"),
        ("src/utils.py", "Utility functions")
    ]
    
    for filepath, description in src_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Documentation files
    doc_files = [
        ("docs/api.md", "API documentation"),
        ("DEPLOYMENT.md", "Deployment guide")
    ]
    
    for filepath, description in doc_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Example and test files
    example_files = [
        ("test_api.py", "API test script"),
        ("examples/sample_requests.py", "Sample requests"),
        ("validate_setup.py", "Setup validation script")
    ]
    
    for filepath, description in example_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Scripts
    script_files = [
        ("scripts/run_server.sh", "Server startup script"),
        ("scripts/test_api.sh", "API test script")
    ]
    
    for filepath, description in script_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Docker files
    docker_files = [
        ("docker/Dockerfile", "Docker configuration"),
        ("docker/docker-compose.yml", "Docker Compose configuration")
    ]
    
    for filepath, description in docker_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good

def validate_python_dependencies():
    """Validate Python dependencies"""
    print("\nValidating Python Dependencies")
    print("=" * 40)
    
    required_modules = [
        "flask",
        "sklearn",
        "numpy",
        "pandas",
        "speech_recognition",
        "pydub",
        "langdetect",
        "joblib",
        "werkzeug"
    ]
    
    all_good = True
    for module in required_modules:
        if not check_python_module(module):
            all_good = False
    
    return all_good

def validate_directories():
    """Validate required directories"""
    print("\nValidating Directory Structure")
    print("=" * 40)
    
    # Create directories if they don't exist
    required_dirs = [
        ("src", "Source code directory"),
        ("docs", "Documentation directory"),
        ("examples", "Examples directory"),
        ("scripts", "Scripts directory"),
        ("docker", "Docker configuration directory")
    ]
    
    all_good = True
    for dirpath, description in required_dirs:
        if not check_directory_exists(dirpath, description):
            all_good = False
    
    # Runtime directories (will be created automatically)
    runtime_dirs = ["models", "temp_uploads", "logs"]
    print(f"\nRuntime directories (created automatically): {', '.join(runtime_dirs)}")
    
    return all_good

def validate_configuration():
    """Validate configuration settings"""
    print("\nValidating Configuration")
    print("=" * 40)
    
    all_good = True
    
    # Check if requirements.txt has content
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip()
            if requirements:
                req_count = len([line for line in requirements.split('\n') if line.strip() and not line.startswith('#')])
                print(f"✅ Requirements file contains {req_count} dependencies")
            else:
                print("❌ Requirements file is empty")
                all_good = False
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        all_good = False
    
    # Check if main app file has proper structure
    try:
        with open("app.py", "r") as f:
            app_content = f.read()
            if "Flask" in app_content and "fraud_detector" in app_content:
                print("✅ Main application file has proper structure")
            else:
                print("❌ Main application file missing key components")
                all_good = False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        all_good = False
    
    return all_good

def main():
    """Main validation function"""
    print("AI Fraud Detection API - Setup Validation")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Run all validations
    structure_ok = validate_project_structure()
    directories_ok = validate_directories()
    config_ok = validate_configuration()
    
    # Note: Skip dependency validation as packages may not be installed yet
    print("\nNote: Python dependency validation skipped (run after 'pip install -r requirements.txt')")
    
    print("\n" + "=" * 50)
    
    if structure_ok and directories_ok and config_ok:
        print("✅ VALIDATION PASSED")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the server: python app.py")
        print("3. Test the API: python test_api.py")
        print("4. Try examples: python examples/sample_requests.py")
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("\nPlease fix the issues above before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
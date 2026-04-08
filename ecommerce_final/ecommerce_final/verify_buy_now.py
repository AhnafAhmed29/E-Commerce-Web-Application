#!/usr/bin/env python3
"""
VERIFICATION SCRIPT - Check if Buy Now is properly configured
Run this to verify your setup
"""

import os
import sys

def check_file_exists(filepath):
    """Check if file exists"""
    if os.path.exists(filepath):
        print(f"✅ {filepath} exists")
        return True
    else:
        print(f"❌ {filepath} NOT FOUND")
        return False

def check_route_exists(filepath, route_name):
    """Check if route exists in app.py"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if f"@app.route('/{route_name}" in content or f'@app.route("/{route_name}' in content:
                print(f"✅ Route '/{route_name}' found in {filepath}")
                return True
            else:
                print(f"❌ Route '/{route_name}' NOT FOUND in {filepath}")
                return False
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def check_template_has_form(filepath):
    """Check if template has buy now form"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if "url_for('buy_now'" in content:
                print(f"✅ Buy Now form found in {filepath}")
                return True
            else:
                print(f"❌ Buy Now form NOT FOUND in {filepath}")
                return False
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def main():
    print("="*60)
    print("BUY NOW CONFIGURATION CHECKER")
    print("="*60)
    print()
    
    all_good = True
    
    # Check files exist
    print("1. Checking Files...")
    all_good &= check_file_exists('app.py')
    all_good &= check_file_exists('templates/product.html')
    all_good &= check_file_exists('templates/base.html')
    print()
    
    # Check routes
    print("2. Checking Routes...")
    all_good &= check_route_exists('app.py', 'buy-now')
    all_good &= check_route_exists('app.py', 'login')
    print()
    
    # Check template
    print("3. Checking Templates...")
    all_good &= check_template_has_form('templates/product.html')
    print()
    
    # Final result
    print("="*60)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("Next steps:")
        print("1. Restart Flask: python app.py")
        print("2. Clear browser cache: Ctrl+F5")
        print("3. Test Buy Now button")
    else:
        print("❌ SOME CHECKS FAILED!")
        print()
        print("Please:")
        print("1. Review the errors above")
        print("2. Fix the missing components")
        print("3. Run this script again")
    print("="*60)

if __name__ == '__main__':
    main()

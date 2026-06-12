import sys
import os
import subprocess

# 1. ABSOLUTE PATH SHIELDING
# Prevents import errors by forcing the interpreter to use the project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2. DATA ENGINEERING IMPORTS
from data.database.db import initdb

try:
    from data.collector.collector import run_collector
except ImportError:
    run_collector = None

# 3. DATA SCIENCE IMPORTS (Conditional)
try:
    from data.preprocessing.dataset_builder import build_dataset
except ImportError:
    build_dataset = None

try:
    from data.training.train import train_model
except ImportError:
    train_model = None

# 4. TESTING SUB-MENU
def test_menu():
    while True:
        print("\n" + "-"*45)
        print(" ENGINEERING TESTS MENU ")
        print("-"*45)
        print("1. Run Brawler Frequency Test")
        print("2. Run Cluster Test")
        print("0. Return to Main Menu")
        print("-"*45)
        
        test_choice = input("Choose a test to execute: ")
        
        if test_choice == '1':
            print("\n[Running] Brawler Frequency Test...")
            test_path = os.path.join(ROOT_DIR, "tests", "brawler_frequency_test.py")
            if os.path.exists(test_path):
                subprocess.run([sys.executable, test_path])
            else:
                print(f"[Error] Test file not found: {test_path}")
                
        elif test_choice == '2':
            print("\n[Running] Cluster Test...")
            test_path = os.path.join(ROOT_DIR, "tests", "cluster_test.py")
            if os.path.exists(test_path):
                subprocess.run([sys.executable, test_path])
            else:
                print(f"[Error] Test file not found: {test_path}")
                
        elif test_choice == '0':
            print("\nReturning to Main Menu...")
            break
            
        else:
            print("\n[Warning] Invalid option. Enter 1, 2, or 0.")

# 5. INTERACTIVE ORCHESTRATION (MAIN MENU)
def menu():
    while True:
        print("\n" + "="*45)
        print(" PIPELINE: BRAWL STARS MACHINE LEARNING ")
        print("="*45)
        print("1. Initialize/Reset Database")
        print("2. Start Data Collection (Crawler)")
        print("3. Build Dataset (Pandas Preprocessing)")
        print("4. Train Predictive Model (Scikit-Learn)")
        print("5. Run Engineering Tests")
        print("0. Exit")
        print("="*45)
        
        choice = input("Choose a step to execute: ")
        
        if choice == '1':
            print("\n[Running] Recreating SQL structure...")
            initdb()
            print("Done.")
            
        elif choice == '2':
            if run_collector:
                print("\n[Running] Crawler initialization...")
                run_collector()
            else:
                print("\n[Structural Error] Module 'collector.py' not found.")
            
        elif choice == '3':
            if build_dataset:
                print("\n[Running] Relational Flattening and CSV Generation...")
                build_dataset()
            else:
                print("\n[Structural Error] Module 'dataset_builder.py' not found.")
                
        elif choice == '4':
            if train_model:
                print("\n[Running] Gradient Boosting Algorithm Training...")
                train_model()
            else:
                print("\n[Structural Error] Module 'train.py' not found.")
                
        elif choice == '5':
            test_menu()
            
        elif choice == '0':
            print("\nSystem closed safely.")
            break
            
        else:
            print("\n[Warning] Invalid option. Enter a number from 0 to 5.")

if __name__ == "__main__":
    menu()
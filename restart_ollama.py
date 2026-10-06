"""
Force Ollama Model Reload
This script restarts Ollama and forces it to load the correct model
"""

import subprocess
import time
import requests
import sys

def run_command(cmd):
    """Run a shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

print("\n" + "="*60)
print("  OLLAMA MODEL RELOAD SCRIPT")
print("="*60 + "\n")

# Step 1: Kill Ollama
print("[1/5] Stopping Ollama...")
run_command("taskkill /IM ollama.exe /F")
run_command("taskkill /IM ollama_llama_server.exe /F")
time.sleep(3)
print("✓ Ollama stopped\n")

# Step 2: Start Ollama
print("[2/5] Starting Ollama...")
subprocess.Popen(["ollama", "serve"], 
                 stdout=subprocess.DEVNULL, 
                 stderr=subprocess.DEVNULL,
                 creationflags=subprocess.CREATE_NO_WINDOW)
time.sleep(5)

# Wait for Ollama to be ready
for i in range(10):
    if check_ollama():
        print("✓ Ollama is running\n")
        break
    time.sleep(1)
else:
    print("✗ Failed to start Ollama")
    print("Please manually run: ollama serve\n")
    sys.exit(1)

# Step 3: Check config
print("[3/5] Checking config.py...")
try:
    with open('config.py', 'r') as f:
        config_content = f.read()
    
    if 'OLLAMA_MODEL = "phi3:mini"' in config_content:
        print('✓ Config uses phi3:mini\n')
    elif 'OLLAMA_MODEL = "tinyllama"' in config_content:
        print('✓ Config uses tinyllama\n')
    else:
        print('⚠️  Config might not be updated!')
        print('   Please check OLLAMA_MODEL in config.py\n')
except Exception as e:
    print(f"✗ Could not read config.py: {e}\n")

# Step 4: Force load the model
print("[4/5] Pre-loading model...")
import config
model_name = config.OLLAMA_MODEL

print(f"   Loading: {model_name}")

try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model_name,
            "prompt": "test",
            "stream": False,
            "options": {"num_predict": 5}
        },
        timeout=30
    )
    
    if response.status_code == 200:
        print(f"✓ Model {model_name} loaded successfully\n")
    else:
        print(f"✗ Failed to load model: {response.status_code}\n")
except Exception as e:
    print(f"✗ Error loading model: {e}\n")

# Step 5: Test speed
print("[5/5] Testing model speed...")
start = time.time()

try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model_name,
            "prompt": "Hello",
            "stream": False,
            "options": {"num_predict": 10}
        },
        timeout=30
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 200:
        print(f"✓ Test completed in {elapsed:.2f}s\n")
        
        if elapsed < 5:
            print("✅ Model is FAST - Ready to use!")
        elif elapsed < 15:
            print("⚠️  Model is OK but could be faster")
            print("   Consider using tinyllama for max speed")
        else:
            print("❌ Model is SLOW")
            print("   You may still be using the wrong model!")
            print(f"   Current: {model_name}")
            print("   Try: tinyllama or phi3:mini")
    else:
        print(f"✗ Test failed: {response.status_code}")
        
except Exception as e:
    print(f"✗ Test error: {e}")

print("\n" + "="*60)
print("  Restart complete!")
print("="*60)
print("\nNow run: python performance_diagnostic.py\n")

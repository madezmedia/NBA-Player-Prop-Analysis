import os
import sys
import subprocess
import secrets

def check_python_version():
    """Verify Python version compatibility"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ is required.")
        sys.exit(1)
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")

def install_dependencies():
    """Install project dependencies"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies.")
        sys.exit(1)

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not os.path.exists('.env'):
        try:
            with open('.env.example', 'r') as example_file:
                env_content = example_file.read()
            
            # Generate a secure random secret key
            secret_key = secrets.token_hex(32)
            
            # Replace placeholders with generated/default values
            env_content = env_content.replace(
                'generate_a_random_secret_key_here', 
                secret_key
            )
            
            with open('.env', 'w') as env_file:
                env_file.write(env_content)
            
            print("✅ .env file created successfully!")
            print("🔑 A new secret key has been generated.")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            sys.exit(1)
    else:
        print("ℹ️ .env file already exists. Skipping creation.")

def verify_api_keys():
    """Prompt user to configure essential API keys"""
    print("\n🔐 API Key Configuration")
    
    # Groq API Key
    groq_key = input("Enter your Groq API Key (or press Enter to skip): ").strip()
    if groq_key:
        subprocess.call(['sed', '-i', f's/your_groq_api_key_here/{groq_key}/', '.env'])
        print("✅ Groq API Key configured")
    
    # RapidAPI Key
    rapidapi_key = input("Enter your RapidAPI Key (or press Enter to skip): ").strip()
    if rapidapi_key:
        subprocess.call(['sed', '-i', f's/your_rapidapi_key_here/{rapidapi_key}/', '.env'])
        print("✅ RapidAPI Key configured")

def setup_virtual_environment():
    """Create a virtual environment if not exists"""
    if not os.path.exists('venv'):
        try:
            subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])
            print("✅ Virtual environment created successfully!")
        except subprocess.CalledProcessError:
            print("❌ Error creating virtual environment.")
            sys.exit(1)
    else:
        print("ℹ️ Virtual environment already exists.")

def main():
    print("🏀 Basketball AI Performance Analyst - Environment Setup")
    
    # Perform setup steps
    check_python_version()
    setup_virtual_environment()
    create_env_file()
    verify_api_keys()
    install_dependencies()
    
    print("\n🎉 Setup Complete!")
    print("Next steps:")
    print("1. Activate the virtual environment:")
    print("   source venv/bin/activate  # On Unix/macOS")
    print("   venv\\Scripts\\activate    # On Windows")
    print("2. Run the application: streamlit run app.py")

if __name__ == "__main__":
    main()

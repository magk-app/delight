"""Verify environment configuration.

Run this to check if your .env file is set up correctly.

Usage:
    poetry run python experiments/verify_env.py
"""

from pathlib import Path
from experiments.config import get_config

def main():
    print("\n" + "=" * 70)
    print("🔍 ENVIRONMENT VERIFICATION")
    print("=" * 70 + "\n")

    # Check .env file location
    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / ".env"

    print(f"📁 Backend directory: {backend_dir}")
    print(f"📄 .env file location: {env_file}")
    print(f"   Exists: {'✅ YES' if env_file.exists() else '❌ NO'}")

    if env_file.exists():
        print(f"   Size: {env_file.stat().st_size} bytes")
    print()

    # Load config
    print("🔧 Loading configuration...")
    config = get_config()
    print()

    # Check OpenAI API Key
    print("🔑 OpenAI API Key:")
    if config.openai_api_key:
        # Show first and last 4 characters only
        masked_key = f"{config.openai_api_key[:8]}...{config.openai_api_key[-4:]}"
        print(f"   ✅ SET: {masked_key}")
        print(f"   Length: {len(config.openai_api_key)} characters")
    else:
        print("   ❌ NOT SET")
        print("\n   To fix this:")
        print(f"   1. Create or edit: {env_file}")
        print("   2. Add this line:")
        print("      OPENAI_API_KEY=sk-proj-your-key-here")
        print()

    # Check Database URL
    print("\n🗄️  Database URL:")
    if config.database_url:
        # Mask password
        masked_url = config.database_url
        if '@' in masked_url:
            parts = masked_url.split('@')
            if ':' in parts[0]:
                user_pass = parts[0].split(':')
                masked_url = f"{user_pass[0]}:****@{parts[1]}"
        print(f"   ✅ SET: {masked_url[:50]}...")
    else:
        print("   ⚠️  NOT SET (OK for JSON storage)")

    # Check JSON storage
    print(f"\n📁 JSON Storage:")
    print(f"   Enabled: {config.use_json_storage}")
    print(f"   Path: {config.json_storage_path}")

    # Check models
    print(f"\n🤖 AI Models:")
    print(f"   Chat Model: {config.chat_model}")
    print(f"   Embedding Model: {config.embedding_model}")
    print(f"   Reasoning Model: {config.reasoning_model}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    ready = True
    issues = []

    if not config.openai_api_key:
        ready = False
        issues.append("❌ OpenAI API Key not set")
    else:
        print("✅ OpenAI API Key is configured")

    if not config.database_url:
        print("⚠️  Database URL not set (using JSON storage)")
    else:
        print("✅ Database URL is configured")

    print()

    if ready:
        print("🎉 Configuration looks good! You can now run:")
        print("   poetry run python experiments/test_json_storage.py")
    else:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")
        print(f"\nFix these issues in: {env_file}")

    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

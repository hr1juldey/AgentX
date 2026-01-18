# =============================================================================
# AGENTX R013 - Test Client Runner
# =============================================================================
# Wrapper script to run test client from project root
# =============================================================================

import sys
from pathlib import Path

# Add client directory to Python path
client_dir = Path(__file__).parent / "client"
sys.path.insert(0, str(Path(__file__).parent))

# Run the client main
if __name__ == "__main__":
    from client.main import main
    import asyncio

    asyncio.run(main())

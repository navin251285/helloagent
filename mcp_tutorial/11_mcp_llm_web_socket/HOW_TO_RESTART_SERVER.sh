#!/bin/bash
# INSTRUCTIONS TO RESTART THE SERVER
# 
# The server running since 11:27 needs to be restarted with the updated code.
# Follow these steps:

echo "=========================================="
echo "📋 SERVER RESTART INSTRUCTIONS"
echo "=========================================="
echo
echo "The current server (started at 11:27) is running OLD code."
echo "It needs to be restarted to load the Chroma DB fixes."
echo
echo "STEPS:"
echo "------"
echo
echo "1. Find the terminal where you started the server"
echo "   (Look for: 'python mcp_server.py' or Uvicorn running message)"
echo
echo "2. Press Ctrl+C in that terminal to stop it"
echo
echo "3. Run this command in the same terminal:"
echo "   cd /home/navinkumar_25_gmail_com/mcp_tutorial/11_mcp_llm_web_socket"
echo "   python3 mcp_server.py"
echo
echo "4. You should see these NEW messages:"
echo "   [INIT] ✅ Chroma DB initialized successfully"
echo "   [INIT] Found 2 collections:"
echo "   [INIT]   - patient_profiles: 356 items"
echo "   [INIT]   - patients: 100 items"
echo
echo "5. Then run the test again:"
echo "   python3 test_full_workflow.py"
echo
echo "=========================================="
echo

# Try to provide a direct way if possible
echo "🔧 Attempting automatic restart..."
echo

# Check if we can kill it
if pkill -15 -f "python.*mcp_server.py" 2>/dev/null; then
    echo "✅ Server stopped. Starting new one..."
    sleep 2
    cd /home/navinkumar_25_gmail_com/mcp_tutorial/11_mcp_llm_web_socket
    python3 mcp_server.py
else
    echo "❌ Cannot auto-restart (permission denied)"
    echo "Please manually restart using the steps above."
fi

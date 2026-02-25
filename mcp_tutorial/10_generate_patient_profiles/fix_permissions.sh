#!/bin/bash
# Fix ChromaDB permissions script
# Run this if you get "readonly database" errors

echo "Fixing ChromaDB permissions..."

CHROMA_DIR="./chroma_db"

if [ ! -d "$CHROMA_DIR" ]; then
    echo "Error: ChromaDB directory not found at $CHROMA_DIR"
    echo "Please run 'python create_embeddings.py' first to generate the database."
    exit 1
fi

# Set directory permissions to rwxrwxrwx (777)
echo "Setting directory permissions..."
find "$CHROMA_DIR" -type d -exec chmod 777 {} \;

# Set file permissions to rw-rw-rw- (666)
echo "Setting file permissions..."
find "$CHROMA_DIR" -type f -exec chmod 666 {} \;

echo "✓ Permissions fixed successfully!"
echo ""
echo "Database files:"
ls -lh "$CHROMA_DIR"/*.sqlite3 2>/dev/null || echo "No SQLite files found"
echo ""
echo "You can now run: python query_patients.py"

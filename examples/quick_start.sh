#!/bin/bash
# Quick start examples for polynomial dependency checker

echo "=== Polynomial Algebraic Dependency Checker - Quick Start ==="
echo ""

echo "1. Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "2. Example: Check a specific polynomial pair"
echo "   Command: python run.py check \"x^2 + y^2\" \"x*y\""
python run.py check "x^2 + y^2" "x*y"
echo ""

echo "3. Example: Check another pair"
echo "   Command: python run.py check \"x^2\" \"y^2\""
python run.py check "x^2" "y^2"
echo ""

echo "4. View statistics"
echo "   Command: python run.py stats"
python run.py stats
echo ""

echo "5. Query results"
echo "   Command: python run.py query --limit 5"
python run.py query --limit 5
echo ""

echo "=== Quick Start Complete ==="
echo ""
echo "To run brute force search:"
echo "  python run.py brute"
echo ""
echo "For more options:"
echo "  python run.py --help"
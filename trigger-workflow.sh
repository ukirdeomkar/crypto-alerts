#!/bin/bash

echo "🚀 Triggering Crypto Volatility Alerts workflow..."

gh workflow run volatality.yml

if [ $? -eq 0 ]; then
    echo "✅ Workflow triggered successfully!"
    echo ""
    echo "⏳ Waiting for workflow to start..."
    sleep 5
    
    echo ""
    echo "📊 Latest workflow runs:"
    gh run list --workflow=volatality.yml --limit 3
    
    echo ""
    echo "💡 To watch the run live, use:"
    echo "   gh run watch"
else
    echo "❌ Failed to trigger workflow"
    echo "Make sure you're authenticated: gh auth login"
fi


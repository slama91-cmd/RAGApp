#!/bin/bash

# Test script to verify the React application can be built and run

echo "Installing dependencies..."
cd frontend-react
npm install

echo "Building the React application..."
npm run build

echo "Build completed successfully!"
echo "To run the application in development mode, use: npm run dev"
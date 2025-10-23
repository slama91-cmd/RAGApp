// Simple test script to verify the React app structure
const fs = require('fs');
const path = require('path');

const requiredFiles = [
  'package.json',
  'vite.config.js',
  'index.html',
  'src/main.jsx',
  'src/App.jsx',
  'src/index.css',
  'src/services/api.js',
  'src/components/Navbar.jsx',
  'src/components/ToastContainer.jsx',
  'src/pages/Dashboard.jsx',
  'src/pages/Documents.jsx',
  'src/pages/Content.jsx',
  'src/pages/Tests.jsx',
  'src/pages/Progress.jsx',
  'README.md'
];

console.log('Checking React app structure...\n');

let allFilesExist = true;

requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`✓ ${file} exists`);
  } else {
    console.log(`✗ ${file} is missing`);
    allFilesExist = false;
  }
});

console.log('\nChecking package.json dependencies...\n');

const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));

const requiredDependencies = [
  'react',
  'react-dom',
  'react-router-dom',
  'bootstrap',
  'axios',
  'react-bootstrap'
];

requiredDependencies.forEach(dep => {
  if (packageJson.dependencies[dep]) {
    console.log(`✓ ${dep} is installed (${packageJson.dependencies[dep]})`);
  } else {
    console.log(`✗ ${dep} is missing`);
    allFilesExist = false;
  }
});

console.log('\nChecking dev dependencies...\n');

const requiredDevDependencies = [
  '@vitejs/plugin-react',
  'vite'
];

requiredDevDependencies.forEach(dep => {
  if (packageJson.devDependencies[dep]) {
    console.log(`✓ ${dep} is installed (${packageJson.devDependencies[dep]})`);
  } else {
    console.log(`✗ ${dep} is missing`);
    allFilesExist = false;
  }
});

console.log('\nChecking scripts...\n');

const requiredScripts = ['dev', 'build', 'preview'];

requiredScripts.forEach(script => {
  if (packageJson.scripts[script]) {
    console.log(`✓ ${script} script is available`);
  } else {
    console.log(`✗ ${script} script is missing`);
    allFilesExist = false;
  }
});

console.log('\n=====================================');

if (allFilesExist) {
  console.log('✓ All checks passed! The React app is properly set up.');
  console.log('\nTo run the app:');
  console.log('1. cd frontend-react');
  console.log('2. npm install');
  console.log('3. npm run dev');
} else {
  console.log('✗ Some checks failed. Please review the missing files or dependencies.');
}

console.log('=====================================');
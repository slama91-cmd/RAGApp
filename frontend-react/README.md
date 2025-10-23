# EduMentor AI - React Frontend

This is the React-based frontend for the EduMentor AI educational mentorship platform. It has been migrated from vanilla JavaScript to React with the latest version (18.2.0) and modern tooling.

## Features

- **Dashboard**: Overview of documents, content, tests, and students
- **Document Management**: Upload and manage PDF documents
- **Content Generation**: Generate educational content from documents
- **Test Creation**: Create tests from educational content
- **Progress Tracking**: Track student progress and generate learning paths

## Tech Stack

- **React 18.2.0**: Latest version of React with hooks and modern features
- **React Router 6.8.1**: For routing and navigation
- **Vite 4.1.0**: Fast build tool and development server
- **Bootstrap 5.3.0**: UI framework for responsive design
- **Axios 1.3.4**: HTTP client for API requests

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend-react
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Development

To start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### Building for Production

To build the application for production:
```bash
npm run build
```

The built files will be in the `dist` directory.

### Testing

To run the build test:
```bash
./test-build.sh
```

## Project Structure

```
frontend-react/
├── src/
│   ├── components/          # Reusable components
│   │   ├── Navbar.jsx      # Navigation bar
│   │   └── ToastContainer.jsx # Toast notifications
│   ├── pages/              # Page components
│   │   ├── Dashboard.jsx   # Dashboard page
│   │   ├── Documents.jsx   # Document management
│   │   ├── Content.jsx     # Content generation
│   │   ├── Tests.jsx       # Test creation
│   │   └── Progress.jsx    # Progress tracking
│   ├── services/           # API services
│   │   └── api.js         # API client
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── vite.config.js         # Vite configuration
└── test-build.sh          # Build test script
```

## API Integration

The frontend communicates with the backend API through the `api.js` service. The API base URL is configured in `vite.config.js` with proxy settings for development.

### Environment Variables

Create a `.env` file in the root directory for environment-specific configuration:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=edu-api-key-1234
```

## Key Components

### Navbar

The navigation bar provides access to all main sections of the application. It uses React Router for navigation and highlights the active page.

### ToastContainer

This component handles toast notifications for user feedback, such as success messages, errors, and loading states.

### Page Components

Each page component is responsible for its own state management and API calls using React hooks:

- **Dashboard**: Displays overview statistics and recent activity
- **Documents**: Handles document upload and management
- **Content**: Manages educational content generation
- **Tests**: Creates and manages tests
- **Progress**: Tracks student progress and learning paths

## State Management

The application uses React hooks for state management:

- `useState`: For component-level state
- `useEffect`: For side effects and API calls
- `useContext`: For shared state (if needed in the future)

## Styling

The application uses Bootstrap 5 for responsive design, with custom styles in `index.css`. The styling has been migrated from the original vanilla JavaScript application with minimal changes.

## Migration from Vanilla JavaScript

This React application was migrated from a vanilla JavaScript application. Key changes include:

1. **Component Structure**: Converted to React components with proper props and state
2. **Routing**: Implemented React Router for navigation
3. **State Management**: Replaced manual DOM manipulation with React hooks
4. **API Calls**: Migrated to use Axios with React hooks
5. **Build Process**: Set up Vite for modern development and building

## Future Enhancements

- Implement Redux or Context API for global state management
- Add unit tests with React Testing Library
- Implement server-side rendering with Next.js
- Add TypeScript for type safety
- Implement PWA features for offline support

## License

This project is part of the EduMentor AI educational mentorship platform.
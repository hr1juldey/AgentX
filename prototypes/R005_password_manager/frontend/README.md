# Password Manager Frontend

A secure Next.js frontend for the Password Manager application (R005 prototype).

## Features

- **Authentication**: Secure login with master password
- **Password Vault**: Grid view of all stored passwords
- **Add/Edit/Delete**: Full CRUD operations for password entries
- **Search**: Filter passwords by title, username, or URL
- **Copy to Clipboard**: One-click password copying
- **Show/Hide**: Toggle password visibility
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Built with shadcn/ui components and Tailwind CSS

## Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality React components
- **Radix UI**: Accessible component primitives
- **Lucide Icons**: Beautiful icon set

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8005`

## Installation

1. Navigate to the frontend directory:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R005_password_manager/frontend
```

2. Run the setup script:
```bash
./scripts/setup.sh
```

Or manually install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` if needed:
```env
NEXT_PUBLIC_API_URL=http://localhost:8005
NEXT_PUBLIC_APP_NAME=Password Manager
```

## Development

Start the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build for Production

Build the application:
```bash
npm run build
```

Start the production server:
```bash
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main page (login + vault)
│   └── globals.css         # Global styles and CSS variables
├── components/
│   └── ui/                 # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── input.tsx
│       └── ...
├── lib/
│   └── utils.ts            # Utility functions
├── scripts/
│   └── setup.sh            # Setup script
├── .env.local              # Environment variables (not in git)
├── .env.local.example      # Environment variables template
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── next.config.js          # Next.js configuration
└── postcss.config.js       # PostCSS configuration
```

## API Integration

The frontend communicates with the backend API using the following endpoints:

### Authentication
- `POST /api/auth/login` - Login with username and password
- Headers: `Authorization: Bearer <token>`

### Passwords
- `GET /api/passwords` - Get all passwords
- `POST /api/passwords` - Create a new password
- `PUT /api/passwords/:id` - Update a password
- `DELETE /api/passwords/:id` - Delete a password

## Components

### Main Page (app/page.tsx)

The main page includes two states:

1. **Login Screen** (unauthenticated):
   - Username input
   - Password input
   - Login button
   - Error messages

2. **Password Vault** (authenticated):
   - Search bar
   - Add password button
   - Grid of password cards
   - Each card shows:
     - Title and URL
     - Username
     - Password (with show/hide toggle)
     - Copy button
     - Edit and Delete buttons

### Dialog Component

Used for adding and editing passwords:
- Title input
- Username/email input
- Password input with show/hide toggle
- URL input (optional)
- Submit and Cancel buttons

## Authentication Flow

1. User enters credentials on login screen
2. Frontend sends POST request to `/api/auth/login`
3. Backend returns JWT access token
4. Token stored in `localStorage`
5. Token included in Authorization header for all subsequent requests
6. Logout clears token from `localStorage`

## Security Features

- Passwords are hidden by default (masked input)
- Master password for vault access
- JWT-based authentication
- Token stored in localStorage (consider httpOnly cookies for production)
- Confirmation dialog for delete operations

## Future Enhancements

- Password strength indicator
- Two-factor authentication
- Biometric unlock (WebAuthn)
- Auto-logout after inactivity
- Export/import passwords
- Password generator
- Categories/tags for organization
- Dark mode toggle
- Vault lock after timeout

## Troubleshooting

### Connection refused error
- Ensure backend is running on port 8005
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

### Login fails
- Verify backend authentication endpoint is working
- Check browser console for error messages
- Ensure CORS is configured on backend

### Passwords not loading
- Check that token is valid
- Verify backend `/api/passwords` endpoint
- Check browser network tab for failed requests

## License

Part of the AgentX Prototype Cookbook.

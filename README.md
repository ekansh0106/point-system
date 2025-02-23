# Family Task Manager API

A Flask-based REST API for a family task management system where parents can manage their children's tasks and activities.

## Features

### User Management
- **Parent Account Management**
  - Register/Login as a parent
  - Profile management
  - Password reset functionality

- **Child Account Management**
  - Parents can create and manage child accounts
  - Each child gets their own login credentials
  - Profile customization for children

### Task Management
- **Parent Features**
  - Create tasks for themselves and children
  - Set task deadlines and priorities
  - Monitor task completion status
  - Modify or delete any task
  - View task history and analytics

- **Child Features**
  - Create personal tasks
  - View assigned tasks from parents
  - Update task status (e.g., pending, in-progress, completed)
  - Cannot modify deadline/details of parent-assigned tasks

### Task Properties
- Title
- Description
- Deadline
- Status (pending, in-progress, completed)
- Priority level
- Created by (parent/child)
- Assigned to
- Creation timestamp
- Last modified timestamp

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **API Documentation**: Swagger/OpenAPI

## Project Structure

```
family-task-manager/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── user.py      # User models (Parent/Child)
│   │   └── task.py      # Task model
│   ├── blueprints/
│   │   ├── auth/        # Authentication endpoints
│   │   ├── users/       # User management
│   │   ├── tasks/       # Task management
│   │   └── dashboard/   # Analytics and overview
│   └── utils/           # Helper functions
├── core/
│   └── run.py
└── tests/               # Test suite
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new parent account
- `POST /auth/login` - Login for both parent and child
- `POST /auth/logout` - Logout user

### User Management
- `POST /users/children` - Register new child (Parent only)
- `GET /users/children` - List all children (Parent only)
- `PUT /users/children/{id}` - Update child details (Parent only)

### Task Management
- `POST /tasks` - Create new task
- `GET /tasks` - List all tasks (filtered by user role)
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task (Parent only)
- `PUT /tasks/{id}/status` - Update task status

### Dashboard
- `GET /dashboard/overview` - Get task statistics
- `GET /dashboard/tasks/pending` - List pending tasks
- `GET /dashboard/tasks/completed` - List completed tasks

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   export FLASK_APP=core.run
   export FLASK_ENV=development
   export DATABASE_URL=your_database_url
   export SECRET_KEY=your_secret_key
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Run the application:
   ```bash
   flask run
   ```

## Testing

Run tests using:
```bash
poetry run pytest
```

## License

[Your chosen license]

## Contributing

[Your contribution guidelines]
```

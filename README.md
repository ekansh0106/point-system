# Family Point Reward System API

A Flask-based REST API for a family point reward system where parents can create tasks, children earn points upon completion, and redeem points for various activities.

## Features

### User Management
- **Parent Account Management**
  - Register/Login as a parent
  - Profile management
  - Create and manage child accounts
  - Approve task completion
  - Manage reward activities and their point costs

- **Child Account Management**
  - Separate authentication for children
  - View assigned and self-created tasks
  - Track earned points
  - Redeem points for activities

### Task Management API
- **Parent Endpoints**
  - Create tasks with point values
  - Set task deadlines and priorities
  - Approve/reject task completion
  - View task history and point transactions
  - Monitor children's point balances

- **Child Endpoints**
  - Create personal tasks (require parent approval)
  - View assigned tasks
  - Mark tasks as completed (pending parent approval)
  - Track personal point balance
  - View available rewards and their costs

### Point System
- **Task Completion**
  - Points awarded upon parent approval
  - Different point values for different tasks
  - Point history tracking
  - Running point balance

- **Reward System**
  - Predefined activities (TV time, gaming, outdoor play)
  - Custom activities added by parents
  - Different point costs for different activities
  - Point redemption tracking

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
- `POST /tasks/{id}/approve` - Approve task completion (Parent only)

### Point System
- `GET /points/balance` - Get current point balance
- `GET /points/history` - Get point transaction history
- `POST /points/redeem` - Redeem points for activity

### Reward Management
- `POST /rewards` - Create new reward activity (Parent only)
- `GET /rewards` - List all available rewards
- `PUT /rewards/{id}` - Update reward details (Parent only)
- `DELETE /rewards/{id}` - Delete reward (Parent only)

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Authentication**: JWT (JSON Web Tokens)
- **API Documentation**: Swagger/OpenAPI

## Project Structure

```
point-system/
├── core/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── user.py        # User models (Parent/Child)
│   │   │   ├── task.py        # Task model
│   │   │   ├── reward.py      # Reward activities model
│   │   │   └── transaction.py # Point transaction model
│   │   ├── blueprints/
│   │   │   ├── auth/          # Authentication endpoints
│   │   │   ├── dashboard/     # Analytics endpoints
│   │   │   ├── tasks/         # Task management endpoints
│   │   │   └── rewards/       # Reward management endpoints
│   │   └── templates/         # Templates for testing API (Not for production)
├── migrations/                # Database migrations
├── .gitignore
├── requirements.txt
└── run.py                    # Application entry point
```

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd point-system
   ```

2. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

4. Activate the virtual environment:
   ```bash
   poetry env use python  # Creates virtual env if it doesn't exist
   poetry env activate    # Activates the virtual environment
   ```

5. Initialize the database:
   ```bash
   flask --app run.py db init
   flask --app run.py db migrate -m "Initial migration"
   flask --app run.py db upgrade
   ```

6. Run the API:
   ```bash
   python run.py
   ```

Note: Make sure you have Python 3.8 or higher installed on your system.

Alternatively, you can prefix each command with `poetry run` if you don't want to activate the virtual environment:
```bash
poetry run flask --app run.py db init
poetry run python run.py
```

## Features to be Implemented

### Phase 1: Core API
- [x] User Authentication
- [x] Basic User Management
- [ ] Task CRUD Operations
- [ ] Point System Implementation
- [ ] Basic Reward System

### Phase 2: Enhanced Features
- [ ] Point Transaction API
- [ ] Reward Activity Management
- [ ] Task Approval System
- [ ] Point Balance Tracking

### Phase 3: Additional Features
- [ ] Task Categories
- [ ] Reward Categories
- [ ] Point Analytics
- [ ] Activity Usage Tracking

## API Documentation

Detailed API documentation is available at `/api/docs` when running the server.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)
```

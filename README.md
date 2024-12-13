# NVWA-Internship
This is a kanban-style Django web application designed to improve efficiency and structure for employees within the export certification process at the Nederlandse Voedsel- en Warenautoriteit (NVWA). The main goal was to prototype and test the application with the employees to determine whether a more structured approach in the form of an application could address issues currently present within the process. This project was developed as part of an internship during the 7th semester of the HBO-ICT bachelor’s program at Christelijke Hogeschool Ede (CHE).

This group project included contributions from other team members: Robbin Kruizinga, who handled frontend design, and Daan Ravenhorst, who assisted with application testing.

## Technologie Stack
This application uses the following technologies:
- Django: The chosen web framework.
- GitHub: For storing the code repository.
- GitHub Actions: To automate the testing process.
- Render: For temporary hosting of the application.

## Features
- Kanban-style board for task management.
- User authentication and role-based access.
- Integration with testing workflows using GitHub Actions.
- Easy deployment using Render.

## Run Locally
Follow these steps to run the application locally. Before proceeding, ensure you have Python 3.8+ installed on your system.

### Step 1: Clone the Repository
You can clone the repository in different ways:

Using VS Code: Open the terminal in VS Code and run:

```
git clone https://github.com/your-username/NVWA-Internship.git
```
Using Command Line: Run the following commands:
```
# Clone this repository
git clone https://github.com/your-username/NVWA-Internship.git

# Navigate to the project directory
cd NVWA-Internship
```

### Step 2: Set Up an Environment
You can set up a virtual environment in different ways:

Using venv:
```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```
Using Conda:
```
# Create a conda environment
conda create -n nvwa-env python=3.8

# Activate the environment
conda activate nvwa-env
```
Or feel free to use any environment manager of your choice.

### Step 3: Install Dependencies
```
# Install required Python packages
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Environment variables are managed using example files provided in the repository:

- Copy .env.example to .env for local development:
```
cp .env.example .env
```
- For production, use .env.example.production as a base.

Update the .env file with your specific configurations, e.g.:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
USE_SQLITE=True
```
### Step 5: Apply Migrations
```
# Apply database migrations
cd /kanban
python manage.py migrate
```

### Step 6: Create a Superuser
To access the admin panel, you need to create a superuser account:
```
python manage.py createsuperuser
```
Follow the prompts to set up the superuser credentials.

### Step 7: Set Up Groups and Test Accounts (Optional)
For testing role-specific functionalities, you need to:

- Log in to the admin panel at http://127.0.0.1:8000/admin/ using the superuser account.
- Create the following groups:
    - Expertise
    - Contentbeheer
- Create test accounts and assign them to the respective groups.

**Note**: If you only wish to explore the application without testing role-specific functionalities, the superuser account is sufficient as it has access to all features.

### Step 8: Run the Development Server
```
# Start the local development server
python manage.py runserver
```
Visit http://127.0.0.1:8000/ in your web browser to access the application.

## Testing
To ensure the application runs correctly, use the following command to execute the test suite:
```
python manage.py test
```
GitHub Actions automatically runs these tests with every pull request to the main branch.

## Deployment
The application is hosted temporarily on Render. Follow these steps to deploy:
- Create an account on Render and set up a new web service.
- Link the repository and configure the build settings.
- Add the environment variables from the .env file.
- Deploy the application.
For detailed instructions, visit [Render’s documentation](https://render.com/docs/deploy-django).

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- Robbin Kruizinga: Frontend design.
- Daan Ravenhorst: Application testing.
- Christelijke Hogeschool Ede (CHE): Educational support.
- Nederlandse Voedsel- en Warenautoriteit (NVWA): Opportunity to test and prototype the application.
- OpenAI’s ChatGPT: Aided in coding this project (ChatGPT, n.d.).

## Citations
ChatGPT. (n.d.). https://chatgpt.com/share/675c0114-1c00-8012-aa68-ee1267f1c5bc

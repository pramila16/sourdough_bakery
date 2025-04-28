# Sourdough Bakery API

This is the backend API for the **Sourdough Bakery** system, built using **Django**, **Django REST Framework**, and **MongoDB**.

---

## Getting Started

### 1. Download the Project

If you don't have Git, simply download the repository as a ZIP:

- Go to the project repository URL in your browser.
- Click on **"Download ZIP"**.
- Extract the ZIP file to a folder on your computer.

If you have Git installed, you can also clone it:
```bash
git clone https://github.com/pramila16/sourdough_bakery.git

```


### 2. Setup Docker Environment

Ensure that you have Docker and Docker Compose installed on your system.  
You can check if Docker is installed by running:
```bash
docker --version
docker-compose --version
```

### 3. Steps to run the project
```bash
docker-compose build
docker-compose up
```

### 4. Access the Application

Once the containers are up and running, you can access the application at:
```bash
API: http://127.0.0.1:8000/swagger/
```

### 5. Stopping the Containers
To stop the containers, press Ctrl+C in the terminal where Docker Compose is running or use the following command:
```bash
  docker-compose down
```

### Note: 
Pshudocode.text and sample_code_for_maneging_security.py is added for the security.




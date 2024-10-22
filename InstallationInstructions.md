
## Installation Instructions

Follow these steps to install Python, clone the repository, create a virtual environment, and run the program.

### Step 1: Install Python
1. **Download Python**:
   - Go to the [official Python website](https://www.python.org/downloads/).
   - Download the latest version of Python (Python 3.x.x). Make sure to select **Python 3.10** or later.

2. **Install Python**:
   - Run the installer.
   - Make sure to check the box that says **"Add Python to PATH"** before clicking "Install."
   - Follow the prompts to complete the installation.

3. **Verify Installation**:
   - Open a terminal/command prompt and type the following command to verify that Python is installed correctly:
     ```bash
     python --version
     ```
   - You should see the installed Python version (e.g., `Python 3.10.x`).

### Step 2: Install Git (if you don't have it)
1. **Download Git**:
   - Go to the [Git website](https://git-scm.com/downloads) and download the appropriate version for your operating system.

2. **Install Git**:
   - Follow the installation steps for your operating system.
   - Once installed, verify by opening a terminal and typing:
     ```bash
     git --version
     ```

### Step 3: Clone the Repository
1. Open a terminal or command prompt.
2. Navigate to the directory where you want to store the project.
3. Use the following command to clone the repository:
   ```bash
   git clone <repository-url>
   ```
   Replace `<repository-url>` with the actual URL of your repository (e.g., `https://github.com/your-username/your-repo.git`).

4. After cloning, navigate to the project folder:
   ```bash
   cd your-repo-folder
   ```

### Step 4: Create a Virtual Environment
1. In the terminal, inside the project directory, create a virtual environment with the following command:
   ```bash
   python -m venv venv
   ```
   This will create a virtual environment in a folder named `venv`.

2. **Activate the Virtual Environment**:
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. You should see `(venv)` at the beginning of your terminal prompt, indicating the virtual environment is active.

### Step 5: Install Required Dependencies
1. After activating the virtual environment, install the project dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```

2. This will install all the packages listed in the `requirements.txt` file, such as `Tkinter`, `Pillow`, `Requests`, `BeautifulSoup`, and the Wise Old Man Python client.

### Step 6: Run the Program
1. After installing the dependencies, you can run the program with:
   ```bash
   python main.py
   ```

   This will launch the Old School RuneScape Player Finder GUI.

### Additional Notes:
- **To deactivate the virtual environment**, simply run:
  ```bash
  deactivate
  ```
- Make sure to always activate the virtual environment whenever you work on this project.

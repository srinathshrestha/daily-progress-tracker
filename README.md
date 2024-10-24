# **Daily Progress Tracker**

A simple, multi-user daily progress tracker built using **FastAPI** with JWT-based authentication. Users can register, log in, and maintain their personal progress entries securely. 

[**Try the Live App**](https://daily-progress-tracker.onrender.com/)

---

## **Features**

1. **User Authentication:**
   - User **registration** (sign up).
   - **Login** with JWT token-based authentication.
   - Passwords securely hashed using bcrypt.

2. **Progress Entries:**
   - Add daily entries with goals, achievements, challenges, lessons learned, tasks, notes, mood, and reflections.
   - **Update entries** until the day ends (before midnight).
   - **Delete entries** if needed.
   - Entries are linked to specific users.

3. **Automated Cleanup:**
   - A background task automatically deletes incomplete entries (without goals) after the day ends.

4. **Multi-User Support:**
   - Each user has their own progress logs that are private and secure.
   - Only logged-in users can create, view, update, or delete their own entries.

5. **Intuitive UI:**
   - Simple and responsive web interface using HTML and CSS.
   - **Forms** for login, signup, adding entries, and updating existing ones.

6. **Secure Routes:**
   - JWT tokens are required to access protected routes, ensuring privacy and security.

---

## **How to Use the App**

1. **Sign Up**  
   Go to [Sign Up](https://daily-progress-tracker.onrender.com/signup) and create a new account.

2. **Log In**  
   After signing up, log in at [Login](https://daily-progress-tracker.onrender.com/login) to receive your JWT token.

3. **Create a New Entry**  
   Once logged in, navigate to the home page and **add a new entry** for today’s progress.

4. **Update Existing Entries**  
   Click on any entry to **update** it. You can modify the content as many times as you want before midnight.

5. **Delete Entries**  
   If you no longer need an entry, simply **delete it** using the delete button on the entry view page.

6. **Log Out**  
   Tokens are stored on the client side. Simply close the browser or clear your token to log out.

---

## **Technologies Used**

- **Backend:** FastAPI  
- **Database:** SQLite (can be replaced with PostgreSQL for production)  
- **Authentication:** JWT (JSON Web Tokens) with `fastapi-jwt-auth`  
- **Password Hashing:** Passlib (bcrypt)  
- **Frontend:** HTML, CSS  
- **Deployment:** Render  

---

## **Installation (Local Setup)**

If you want to run the project locally, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/<your-username>/daily-progress-tracker.git
   cd daily-progress-tracker
   
2. **Create and Activate a Virtual Environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows


3. ** Install Dependencies:**
```bash
Copy code
pip install -r requirements.txt



    

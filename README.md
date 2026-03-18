#  Research Lab Manager

A full-stack database application built with **Python, Streamlit, and MySQL** to manage research lab members, projects, equipment usage, grants, and publication reporting.

This system was developed as part of a **Database Systems / Data Management course project** and demonstrates **end-to-end CRUD operations, relational constraints, and analytical queries**.

---

##  Features Overview

### 1. Project & Member Management
- Add, view, update, and delete lab members
- Add, view, update, and delete research projects
- Display real-time project status (Active / Completed / Not Started)
- Show members who worked on projects funded by a specific grant
- Display mentorship relationships among members who worked on the same project
- Enforce **one-mentor-per-mentee constraint**

---

### 2. Equipment Usage Tracking
- Add, view, update, and delete equipment
- Assign and return equipment to/from members
- Show current equipment usage status
- Display members currently using a specific piece of equipment
- Display projects associated with current equipment users
- Enforce **maximum of 3 concurrent active users per equipment**

---

### 3. Grant & Publication Reporting
- View all grants
- Assign grants to projects
- Identify member(s) with the highest number of publications
- Calculate average number of student publications per major
- Count projects funded by a grant and active during a specified period
- Identify the **top 3 most prolific members** for a given grant

---

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** MySQL
- **Database Access:** Custom query layer (`queries.py`)
- **Architecture:** Modular separation of UI (`app.py`) and SQL logic

---

## Project Structure

```text
.
├── app.py           # Streamlit application (UI + interaction logic)
├── queries.py       # SQL queries and business logic
├── db.py            # Database connection and run_query helper
├── README.md        # Project documentation

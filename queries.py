# queries.py
from db import run_query

# -------- LAB_MEMBER ----------
def get_members():
    return run_query("SELECT MID, NAME, MTYPE FROM LAB_MEMBER ORDER BY MID")


def get_member(mid):
    res = run_query("SELECT * FROM `LAB_MEMBER` WHERE MID=%s", (mid,))
    # return single record (dict) or None for easier caller handling
    return res[0] if res else None

def add_member(mid, name, joindate, mtype, mentor):
    # Check mentee already has a mentor
    if mentor is not None:
        existing = get_current_mentor(mid)
        if existing is not None:
            raise Exception("This member already has a mentor assigned.")

    return run_query("INSERT INTO `LAB_MEMBER` (MID,NAME,JOINDATE,MTYPE,MENTOR) VALUES (%s,%s,%s,%s,%s)",
                     (mid,name,joindate,mtype,mentor))

def get_current_mentor(mid):
    res = run_query("SELECT MENTOR FROM LAB_MEMBER WHERE MID=%s", (mid,))
    if not res:
        return None
    return res[0]["MENTOR"]

def update_member(mid, **kwargs):

    # If mentor is being updated, enforce one-mentor rule
    if "MENTOR" in kwargs:
        new_mentor = kwargs["MENTOR"]
        current = get_current_mentor(mid)

        # Case: assigning a new mentor when one already exists
        if new_mentor is not None and current is not None and current != new_mentor:
            raise Exception("A mentee can only have one mentor.")

    cols=[]; params=[]
    for k,v in kwargs.items():
        cols.append(f"{k}=%s"); params.append(v)
    params.append(mid)
    sql = "UPDATE `LAB_MEMBER` SET " + ", ".join(cols) + " WHERE MID=%s"
    return run_query(sql, tuple(params))

def delete_member(mid):
    return run_query("DELETE FROM `LAB_MEMBER` WHERE MID=%s", (mid,))

# -------- PROJECT ----------
def get_projects():
    return run_query("SELECT * FROM `PROJECT` ORDER BY PID")

def add_project(pid, title, sdate, edate, eduration, leader):
    return run_query("INSERT INTO `PROJECT` (PID,TITLE,SDATE,EDATE,EDURATION,LEADER) VALUES (%s,%s,%s,%s,%s,%s)",
                     (pid,title,sdate,edate,eduration,leader))

def update_project(pid, **kwargs):
    cols=[]; params=[]
    for k,v in kwargs.items():
        cols.append(f"{k}=%s"); params.append(v)
    params.append(pid)
    sql = "UPDATE `PROJECT` SET " + ", ".join(cols) + " WHERE PID=%s"
    return run_query(sql, tuple(params))

def delete_project(pid):
    return run_query("DELETE FROM `PROJECT` WHERE PID=%s", (pid,))

# project status
def project_status(pid):
    return run_query("""
        SELECT PID, TITLE, SDATE, EDATE,
         CASE
           WHEN EDATE IS NULL AND CURDATE() >= SDATE THEN 'Active'
           WHEN EDATE IS NOT NULL AND CURDATE() BETWEEN SDATE AND EDATE THEN 'Active'
           WHEN CURDATE() < SDATE THEN 'Not started'
           ELSE 'Completed'
         END AS STATUS
        FROM `PROJECT` WHERE PID=%s
    """, (pid,))

def get_grants():
    return run_query("SELECT * FROM `GRANTS` ORDER BY GID")

def assign_grant_to_project(gid, pid):
    return run_query(
        "INSERT INTO FUNDS (GID, PID) VALUES (%s, %s)",
        (gid, pid)
    )


# members who worked on projects funded by grant
def members_for_grant(gid):
    return run_query("""
        SELECT DISTINCT m.* FROM `LAB_MEMBER` m
        JOIN `WORKS` w ON m.MID = w.MID
        JOIN `FUNDS` f ON w.PID = f.PID
        WHERE f.GID = %s
    """, (gid,))

# mentorships among members who worked on same project




def mentorships_in_project(pid):
    return run_query("""
      SELECT mentee.MID AS mentee_id, mentee.NAME AS mentee_name,
             mentor.MID AS mentor_id, mentor.NAME AS mentor_name
      FROM `WORKS` w
      JOIN `LAB_MEMBER` mentee ON w.MID = mentee.MID
      LEFT JOIN `LAB_MEMBER` mentor ON mentee.MENTOR = mentor.MID
      WHERE w.PID = %s AND mentee.MENTOR IS NOT NULL
    """, (pid,))

# -------- EQUIPMENT ----------
# def assign_equipment(mid, eid, sdate):

#     return run_query(
#         "INSERT INTO `USES` (MID, EID, SDATE) VALUES (%s, %s, %s)",
#         (mid, eid, sdate)
#     )

def assign_equipment(mid, eid, sdate):
    # Count ACTIVE users only
    count_rows = run_query(
        "SELECT COUNT(*) AS cnt FROM USES WHERE EID = %s AND EDATE IS NULL",
        (eid,)
    )

    active_count = count_rows[0]['cnt']

    if active_count >= 3:
        return False, "Cannot assign equipment — maximum of 3 active users reached."

    # Insert new active usage
    run_query(
        "INSERT INTO USES (MID, EID, SDATE, EDATE) VALUES (%s, %s, %s, NULL)",
        (mid, eid, sdate)
    )

    return True, "Equipment assigned successfully."


def return_equipment(mid, eid, edate):
    updated = run_query(
        "UPDATE USES SET EDATE=%s WHERE MID=%s AND EID=%s AND EDATE IS NULL",
        (edate, mid, eid)
    )
    return updated



def get_active_equipment_usage():
    return run_query("""
        SELECT 
            u.MID, m.NAME, u.EID, e.ENAME, u.SDATE
        FROM USES u
        JOIN LAB_MEMBER m ON m.MID = u.MID
        JOIN EQUIPMENT e ON e.EID = u.EID
        WHERE u.EDATE IS NULL
        ORDER BY u.SDATE
    """)


def get_equipment():
    return run_query("SELECT * FROM `EQUIPMENT` ORDER BY EID")

def add_equipment(eid, ename, etype, status, pdate):
    return run_query("INSERT INTO `EQUIPMENT` (EID,ENAME,ETYPE,STATUS,PDATE) VALUES (%s,%s,%s,%s,%s)",
                     (eid,ename,etype,status,pdate))

def update_equipment(eid, **kwargs):
    cols=[]; params=[]
    for k,v in kwargs.items():
        cols.append(f"{k}=%s"); params.append(v)
    params.append(eid)
    return run_query("UPDATE `EQUIPMENT` SET " + ", ".join(cols) + " WHERE EID=%s", tuple(params))

def delete_equipment(eid):
    return run_query("DELETE FROM `EQUIPMENT` WHERE EID=%s", (eid,))

def equipment_status(eid):
    return run_query("SELECT * FROM `EQUIPMENT` WHERE EID=%s", (eid,))

def current_users_of_equipment(eid):
    return run_query("""
        SELECT m.MID, m.NAME, p.PID, p.TITLE 
        FROM USES u
        JOIN LAB_MEMBER m ON u.MID = m.MID
        LEFT JOIN WORKS w ON m.MID = w.MID
        LEFT JOIN PROJECT p ON w.PID = p.PID
        WHERE u.EID = %s AND u.EDATE IS NULL
    """, (eid,))


# -------- GRANT & PUBLICATION REPORTS ----------






def top_publishers(limit=1):
    return run_query("""
      SELECT m.MID, m.NAME, COUNT(pu.PID) AS pub_count
      FROM `LAB_MEMBER` m
      JOIN `PUBLISHES` pu ON m.MID = pu.MID
      GROUP BY m.MID
      ORDER BY pub_count DESC
      LIMIT %s
    """, (limit,))

def avg_student_pubs_per_major():
    return run_query("""
      SELECT t.MAJOR, AVG(t.pub_count) AS avg_pubs
      FROM (
         SELECT st.MID, st.MAJOR, COUNT(pu.PID) AS pub_count
         FROM `STUDENT` st
         LEFT JOIN `PUBLISHES` pu ON st.MID = pu.MID
         GROUP BY st.MID
      ) AS t
      GROUP BY t.MAJOR
    """)

def projects_funded_active_between(gid, start_period, end_period):
    return run_query("""
      SELECT COUNT(DISTINCT p.PID) AS count_projects
      FROM `PROJECT` p
      JOIN `FUNDS` f ON p.PID = f.PID
      WHERE f.GID = %s
        AND (
            (p.SDATE <= %s AND (p.EDATE IS NULL OR p.EDATE >= %s))
        )
    """, (gid, end_period, start_period))

def top3_members_for_grant(gid):
    return run_query("""
      SELECT m.MID, m.NAME, COUNT(DISTINCT pu.PID) AS pubs
      FROM `LAB_MEMBER` m
      JOIN `WORKS` w ON m.MID = w.MID
      JOIN `FUNDS` f ON w.PID = f.PID AND f.GID=%s
      LEFT JOIN `PUBLISHES` pu ON m.MID = pu.MID
      GROUP BY m.MID
      ORDER BY pubs DESC
      LIMIT 3
    """, (gid,))
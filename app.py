# app.py
import streamlit as st
import pandas as pd
import queries


st.set_page_config(page_title="Research Lab Manager")

st.sidebar.title("Menu")
choice = st.sidebar.radio("Choose", [
    "Project & Member Management",
    "Equipment Usage Tracking",
    "Grant & Publication Reporting",
    "Run SQL (advanced)"
])

if choice == "Project & Member Management":
    st.header("Project & Member Management")
    task = st.selectbox("Task", ["View Members", "Add Member", "Update Member", "Delete Member",
                                "View Projects", "Add Project",  "Update Project", "Delete Project", "Project Status", "Members by Grant", "Mentorships in Project"])
    if task == "View Members":
        df = pd.DataFrame(queries.get_members())
        st.dataframe(df)
    elif task == "Add Member":

        mid = st.number_input("MID", min_value=1)
        name = st.text_input("Name")
        joindate = st.date_input("Join Date")
        mtype = st.selectbox("Type", ["Student","Faculty","Collaborator"])
        mentor = st.number_input("Mentor MID (0 for none)", value=0)
        if st.button("Add"):
            mentor_val = None if mentor==0 else mentor
            try:
                queries.add_member(mid, name, joindate.isoformat(), mtype, mentor_val)
                st.success("Member added")
            except Exception as e:
                st.error(str(e))

    
    elif task == "Update Member":
        st.subheader("Update Member")
        
        # Step 1: Input MID
        mid = st.number_input("Enter MID to update", min_value=1, key="update_mid")

        # Step 2: Fetch member
        if st.button("Fetch Member"):
            result = queries.get_member(mid)
            if not result:
                st.error("No member found with that MID.")
                st.session_state.pop("member_to_update", None)  # clear previous
                st.stop()
            # Store in session_state for persistence across reruns
            st.session_state["member_to_update"] = result

        # Step 3: If a member is fetched, show the update form
        if "member_to_update" in st.session_state:
            member = st.session_state["member_to_update"]

            # Extract and prefill values
            name_val = member.get("NAME", "")
            joindate_raw = member.get("JOINDATE")
            try:
                joindate_val = pd.to_datetime(joindate_raw).date()
            except Exception:
                joindate_val = joindate_raw
            type_val = member.get("MTYPE", "Student")
            mentor_val = member.get("MENTOR") or 0

            # Step 4: Use a form for update
            with st.form("update_member_form"):
                new_name = st.text_input("Name", value=name_val)
                new_joindate = st.date_input("Join Date", value=joindate_val)
                type_options = ["Student", "Faculty", "Collaborator"]
                new_type = st.selectbox(
                    "Type",
                    type_options,
                    index=type_options.index(type_val) if type_val in type_options else 0
                )
                new_mentor = st.number_input("Mentor MID (0 for none)", min_value=0, value=mentor_val)

                submit = st.form_submit_button("Update Now")

                if submit:
                    mentor_val_final = None if new_mentor == 0 else new_mentor
                    try:
                        queries.update_member(
                            mid,
                            NAME=new_name,
                            JOINDATE=new_joindate.isoformat(),
                            MTYPE=new_type,
                            MENTOR=mentor_val_final
                        )
                        st.success("Member updated successfully!")
                    except Exception as e:
                        st.error(str(e))
                    st.success("Member updated successfully!")

                    # Optional: Clear session state so form disappears after update
                    st.session_state.pop("member_to_update", None)


            # if st.button("Update Now"):
            #     mentor_val_final = None if new_mentor == 0 else new_mentor

            #     queries.update_member(
            #         mid,
            #         NAME=new_name,
            #         JOINDATE=new_joindate.isoformat(),
            #         MTYPE=new_type,
            #         MENTOR=mentor_val_final
            #     )

            #     st.success("Member updated successfully!")



    
    elif task == "Delete Member":
        st.subheader("Delete Member")

        members = queries.get_members()
        member_list = {f"{row['MID']} - {row['NAME']}": row['MID'] for row in members}

        selected = st.selectbox("Select Member to Delete", list(member_list.keys()))
        mid = member_list[selected]

        if st.button("Delete Member"):
            queries.delete_member(mid)
            st.success("Member deleted successfully!")


    elif task == "Project Status":
        pid = st.number_input("Project PID", min_value=1)
        if st.button("Show Status"):
            st.write(queries.project_status(pid))
    elif task == "Members by Grant":
        gid = st.number_input("Grant GID", min_value=1)
        if st.button("Show"):
            df = pd.DataFrame(queries.members_for_grant(gid))
            st.dataframe(df)
    elif task == "Mentorships in Project":
        pid = st.number_input("PID", min_value=1)
        if st.button("Show"):
            df = pd.DataFrame(queries.mentorships_in_project(pid))
            st.dataframe(df)
    elif task == "View Projects":
        st.dataframe(pd.DataFrame(queries.get_projects()))
    elif task == "Add Project":
        pid = st.number_input("PID", min_value=1)
        title = st.text_input("Title")
        sdate = st.date_input("Start Date")
        edate = st.date_input("End Date")
        eduration = st.number_input("Duration (months)", value=12)
        leader = st.number_input("Leader MID", min_value=1)
        if st.button("Add Project"):
            queries.add_project(pid, title, sdate.isoformat(), edate.isoformat(), eduration, leader)
            st.success("Project added")

    elif task == "Update Project":
        st.subheader("Update Project")

        # Step 1: Select PID
        projects = queries.get_projects()
        if not projects:
            st.info("No projects available.")
            st.stop()

        project_map = {f"{p['PID']} - {p['TITLE']}": p['PID'] for p in projects}
        selected_project = st.selectbox("Select Project", list(project_map.keys()))
        pid = project_map[selected_project]

        # Step 2: Fetch project details
        project = [p for p in projects if p["PID"] == pid][0]

        # Step 3: Pre-fill values
        title_val = project["TITLE"]
        sdate_val = pd.to_datetime(project["SDATE"]).date()
        edate_val = pd.to_datetime(project["EDATE"]).date()
        duration_val = project["EDURATION"]
        leader_val = project["LEADER"]

        # Step 4: Update form
        with st.form("update_project_form"):
            new_title = st.text_input("Title", value=title_val)
            new_sdate = st.date_input("Start Date", value=sdate_val)
            new_edate = st.date_input("End Date", value=edate_val)
            new_duration = st.number_input("Expected Duration (months)", min_value=1, value=duration_val)
            new_leader = st.number_input("Leader MID", min_value=1, value=leader_val)

            submit = st.form_submit_button("Update Now")

            if submit:
                updates = {
                    "TITLE": new_title,
                    "SDATE": new_sdate.isoformat(),
                    "EDATE": new_edate.isoformat(),
                    "EDURATION": new_duration,
                    "LEADER": new_leader
                }

                queries.update_project(pid, **updates)
                st.success("Project updated successfully!")

    elif task == "Delete Project":
        st.subheader("Delete Project")

        projects = queries.get_projects()
        if not projects:
            st.info("No projects found.")
            st.stop()

        # Make selectbox mapping label → pid
        project_list = {f"{p['PID']} - {p['TITLE']}": p['PID'] for p in projects}

        selected = st.selectbox("Select Project to Delete", list(project_list.keys()))
        pid = project_list[selected]

        if st.button("Delete Project"):
            try:
                queries.delete_project(pid)
                st.success("Project deleted successfully!")

            except Exception as e:
                st.error(f"Error while deleting: {e}")


elif choice == "Equipment Usage Tracking":
    st.header("Equipment")
    sub = st.selectbox("Task", ["View Equipment","Add Equipment", "Update Equipment", "Delete Equipment", "Equipment Status","Current Users",  "Assign Equipment",
    "Return Equipment"])
    if sub == "View Equipment":
        st.dataframe(pd.DataFrame(queries.get_equipment()))
    elif sub == "Add Equipment":
        eid = st.number_input("EID", min_value=1)
        ename = st.text_input("Name")
        etype = st.selectbox("Type", ["Computer", "Sensor", "Hardware Tool", "Software License", "Other"])
        status = st.selectbox("Status", ["Available", "In Use", "Retired"])
        pdate = st.date_input("Purchase Date")
        if st.button("Add"):
            queries.add_equipment(eid, ename, etype, status, pdate.isoformat())
            st.success("Added")
    elif sub == "Update Equipment":
        st.subheader("Update Equipment")

        equipment = queries.get_equipment()
        eq_list = {f"{e['EID']} - {e['ENAME']}": e['EID'] for e in equipment}

        selected = st.selectbox("Select equipment", list(eq_list.keys()))
        eid = eq_list[selected]

        new_name = st.text_input("New Name")
        new_status = st.selectbox("Status", ["Available", "In Use", "Broken", "Maintenance"])
        new_type = st.text_input("Type")
        new_pdate = st.date_input("Purchase Date")

        if st.button("Update"):
            updates = {}
            if new_name: updates["ENAME"] = new_name
            if new_status: updates["STATUS"] = new_status
            if new_type: updates["ETYPE"] = new_type
            if new_pdate: updates["PDATE"] = new_pdate.isoformat()

            queries.update_equipment(eid, **updates)
            st.success("Equipment updated!")
    elif sub == "Delete Equipment":
        st.subheader("Delete Equipment")

        equipment = queries.get_equipment()
        eq_list = {f"{e['EID']} - {e['ENAME']}": e['EID'] for e in equipment}

        selected = st.selectbox("Select equipment to delete", list(eq_list.keys()))
        eid = eq_list[selected]

        if st.button("Delete Equipment"):
            try:
                queries.delete_equipment(eid)
                st.success("Equipment deleted successfully!")
            except Exception as e:
                st.error(f"Error: {e}")


    elif sub == "Equipment Status":
        eid = st.number_input("EID", min_value=1)
        if st.button("Show"):
            st.write(queries.equipment_status(eid))
    elif sub == "Current Users":
        eid = st.number_input("EID", min_value=1)
        if st.button("Show"):
            st.dataframe(pd.DataFrame(queries.current_users_of_equipment(eid)))

    elif sub == "Assign Equipment":
        st.subheader("Assign Equipment to Member")

        members = queries.get_members()
        member_list = {f"{m['MID']} - {m['NAME']}": m['MID'] for m in members}

        equipment = queries.get_equipment()
        equip_list = {f"{e['EID']} - {e['ENAME']}": e['EID'] for e in equipment}

        selected_member = st.selectbox("Select Member", list(member_list.keys()))
        selected_equipment = st.selectbox("Select Equipment", list(equip_list.keys()))

        mid = member_list[selected_member]
        eid = equip_list[selected_equipment]

        sdate = st.date_input("Start Date")

        if st.button("Assign"):
            success, msg = queries.assign_equipment(mid, eid, sdate.isoformat())
            if success:
                st.success(msg)
            else:
                st.error(msg)
    elif sub == "Return Equipment":
        st.subheader("Return Equipment")

        active_uses = queries.get_active_equipment_usage()

        if not active_uses:
            st.info("No active equipment usage found.")
        else:
            # Build dropdown label
            usage_map = {
                f"{u['MID']} - {u['NAME']} using {u['EID']} - {u['ENAME']} (since {u['SDATE']})":
                (u['MID'], u['EID'])
                for u in active_uses
            }

            selected = st.selectbox("Active Assignments", list(usage_map.keys()))
            mid, eid = usage_map[selected]

            edate = st.date_input("Return Date")

            if st.button("Return Equipment"):
                queries.return_equipment(mid, eid, edate.isoformat())
                st.success("Equipment returned successfully!")



elif choice == "Grant & Publication Reporting":
    st.header("Reports")
    rpt = st.selectbox("Report", [
    "View Grants",
    "Assign Grant to Project",
    "Top Publishers",
    "Avg student pubs per major",
    "Projects funded active during period",
    "Top 3 members for grant"
    ])
    if rpt == "Top Publishers":
        n = st.number_input("Top N", min_value=1, value=1)
        st.dataframe(pd.DataFrame(queries.top_publishers(n)))
    elif rpt == "Avg student pubs per major":
        st.dataframe(pd.DataFrame(queries.avg_student_pubs_per_major()))
    elif rpt == "Projects funded active during period":
        gid = st.number_input("GID", min_value=1)
        s = st.date_input("Period start")
        e = st.date_input("Period end")
        if st.button("Run"):
            st.write(queries.projects_funded_active_between(gid, s.isoformat(), e.isoformat()))
    elif rpt == "Top 3 members for grant":
        gid = st.number_input("GID", min_value=1)
        if st.button("Run"):
            st.dataframe(pd.DataFrame(queries.top3_members_for_grant(gid)))
    elif rpt == "View Grants":
        st.dataframe(pd.DataFrame(queries.get_grants()))
    elif rpt == "Assign Grant to Project":
        st.subheader("Assign Grant → Project")

        grants = queries.get_grants()
        projects = queries.get_projects()

        if not grants:
            st.info("No grants found.")
            st.stop()

        if not projects:
            st.info("No projects found.")
            st.stop()

        grant_map = {f"{g['GID']} - {g['SOURCE']}": g['GID'] for g in grants}
        project_map = {f"{p['PID']} - {p['TITLE']}": p['PID'] for p in projects}

        selected_grant = st.selectbox("Select Grant", list(grant_map.keys()))
        selected_project = st.selectbox("Select Project", list(project_map.keys()))

        gid = grant_map[selected_grant]
        pid = project_map[selected_project]

        if st.button("Assign"):
            try:
                queries.assign_grant_to_project(gid, pid)
                st.success("Grant assigned to project successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    
    



elif choice == "Run SQL (advanced)":
    st.header("Raw SQL (be careful)")
    q = st.text_area("SQL")
    if st.button("Execute"):
        try:
            res = __import__('db').run_query(q)
            st.write(res)
        except Exception as e:
            st.error(str(e))

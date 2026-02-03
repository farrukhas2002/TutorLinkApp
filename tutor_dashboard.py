import streamlit as st
import webfunc as wb
import datafile as df
import pandas as pd
from datetime import timedelta, datetime

def tutor_dashboard():
    ss = st.session_state

    tutor_uid = ss.get("tutor_uid", None)
    tutor_name = ss.get("tutor_name", None)

    if tutor_uid is None:
        st.error("Tutor session invalid. Please log in again.")
        return

    st.sidebar.title("Tutor Portal")

    def nav(btn, page):
        if st.sidebar.button(btn, use_container_width=True):
            wb.navigate(page)

    nav("Home", "Tutor_Home")
    nav("Availability", "Tutor_Availability")
    nav("Pending Requests", "Tutor_Requests")
    nav("My Sessions", "Tutor_Sessions")

    if st.sidebar.button("Logout"):
        wb.logout()

    page = ss.page

    # -------------------------------------
    # HOME
    # -------------------------------------
    if page == "Tutor_Home":
        st.image("4652485.webp", width=100)
        st.title(f"Welcome, {tutor_name}")

        pending = [r for r in df.PENDING_REQUESTS if r["tutor"] == tutor_uid]
        approved = [s for s in df.TUTOR_SESSIONS if s["tutor"] == tutor_uid]

        st.metric("Pending Requests", len(pending))
        st.metric("Approved Sessions", len(approved))

        if not ss.avl_is_set:
            st.write("Set up your availability to receive requests and accept sessions.")

        return

    # -------------------------------------
    # PENDING REQUESTS
    # -------------------------------------
    if page == "Tutor_Requests":
        st.title("Pending Session Requests")

        requests = [r for r in df.PENDING_REQUESTS if r["tutor"] == tutor_uid]
        sessions = [r for r in df.TUTOR_SESSIONS if r["tutor"] == tutor_uid]

        if not requests:
            st.info("You have no pending session requests.")
            return

        for i, req in enumerate(requests):
            with st.container(border=True):
                st.write(f"**Student:** {req['student']}")
                st.write(f"**Subject:** {req['subject']}")
                st.write(f"**Date:** {req['date']}")
                st.write(f"**Time:** {req['time']}")

                c1, c2 = st.columns(2)

                # ACCEPT
                if c1.button(f"Accept", use_container_width=True):
                    req["status"] = "approved"
                    df.TUTOR_SESSIONS.append(req)
                    df.PENDING_REQUESTS.remove(req)

                    st.success("Request approved.")
                    st.rerun()

                # REJECT
                if c2.button(f"Reject", use_container_width=True):
                    df.PENDING_REQUESTS.remove(req)
                    st.warning("Request rejected.")
                    st.rerun()

    # -------------------------------------
    # APPROVED SESSIONS
    # -------------------------------------
    if page == "Tutor_Sessions":
        st.title("Approved Sessions")

        sessions = [s for s in df.TUTOR_SESSIONS if s["tutor"] == tutor_uid]

        if not sessions:
            st.info("No approved sessions yet.")
            return

        df_s = pd.DataFrame(sessions)
        st.dataframe(
            df_s[["student", "subject", "date", "time", "status"]],
            use_container_width=True, hide_index=True
        )

    if page == "Tutor_Availability":
        st.title("My Availability")

        days = [ "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday" , "Friday", "Saturday"]

        #display availability
        if (ss.submitted_avl == True):
            for i, _day_ in enumerate(days):
                day_of_week, time_start, time_end = st.columns([3,6,3], vertical_alignment="center")
                with day_of_week:
                    st.subheader(_day_)
                    
                with time_start:
                    st.write(df.TUTOR_AVL[tutor_uid][0][i])

                with time_end:
                    st.write(df.TUTOR_AVL[tutor_uid][1][i])

                st.divider()
        else:
            st.header("You have not set your availability yet.")

        if st.button("Modify Availability"):
            day_sel, start_sel, end_sel = st.columns([3,3,3], vertical_alignment="center")
            ss.avl_menu_open = True
        
        
        time_sequence = [(datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
                           + timedelta(minutes=30 * i)).time() for i in range(25)]
        
        #modify availability
        if (ss.avl_menu_open):
            start_times = []
            end_times = []
            with st.form("Days"):
                for _day_ in days:
                    day_of_week, time_start, time_end, btn_submit = st.columns([3,3,3,2], vertical_alignment="center")

                    with day_of_week:
                        st.subheader(_day_)
                    
                    with time_start:
                        start_ = st.selectbox("Start", time_sequence, key=_day_)
                        start_times.append(start_)

                    with time_end:
                        end_ = st.selectbox("End", time_sequence, key=_day_ + "e")
                        end_times.append(end_)

                    st.divider()
 
                submitted = st.form_submit_button("Update Availability")
                    
            if submitted:
                if not (df.TUTOR_AVL.get(tutor_uid)):
                    df.TUTOR_AVL.update( { tutor_uid : [ [], [] ] })
                

                df.TUTOR_AVL[tutor_uid][0] = start_times
                df.TUTOR_AVL[tutor_uid][1] = end_times
                
                ss.avl_menu_open = False

                ss.submitted_avl = True

                print(df.TUTOR_AVL)

                st.rerun()


import streamlit as st
from src.utils import mechanisms, io
import navigation_bar

# SQLite database connection
DATABASE = 'data/titanic.db'

print(st.session_state)

# Streamlit app
st.title("Differential Privacy Web Interface")

navigation_bar.make_sidebar()

st.sidebar.write(f"Logges in as {st.session_state.username}")

# Sidebar settings
st.sidebar.header("Settings")

if 'privacy_budget' not in st.session_state:
    st.session_state.privacy_budget = float(io.query_database(
        f"SELECT current_privacy_budget FROM USERS WHERE name = '{st.session_state.username}'",
        DATABASE
    ))
query_budget = st.sidebar.write(f"Your total privacy budget is {st.session_state.privacy_budget}")
epsilon = st.sidebar.number_input(
    "Epsilon (privacy budget for query)", min_value=0.1, max_value=query_budget, value=1.0, step=0.1
)
LOWER_BOUND = st.sidebar.number_input("Lower bound for sums and averages")
UPPER_BOUND = st.sidebar.number_input("Upper bound for sums and averages")

# Query options
query_type = st.selectbox(
    "Select Query Type",
    options=["Count", "Sum", "Average"]
)

# Execute the selected query
if st.button("Run Query"):
    try:
        if st.session_state.privacy_budget >= epsilon:
            if query_type == "Count":
                dp_result = mechanisms.count_with_laplacian_mechanism(
                    epsilon=epsilon, db=DATABASE, username=st.session_state.username
                )
                st.write(f"Differentially Private Count: {dp_result}")
            elif query_type == "Sum":
                dp_result = mechanisms.sum_with_laplacian_mechanism(
                    column='Age',
                    epsilon=epsilon,
                    lower_bound=LOWER_BOUND,
                    upper_bound=UPPER_BOUND,
                    db=DATABASE,
                    username=st.session_state.username
                )
                st.write(f"Differentially Private Sum: {dp_result}")
            elif query_type == "Average":
                dp_result = mechanisms.average_with_laplacian_mechanism(
                    column='Age',
                    epsilon=epsilon,
                    lower_bound=LOWER_BOUND,
                    upper_bound=UPPER_BOUND,
                    db=DATABASE,
                    username=st.session_state.username
                )
                st.write(f"Differentially Private Average: {dp_result}")
            st.session_state.privacy_budget -= epsilon
        else:
            raise Exception("The privacy budget allocated to this query exceeds your current total privacy budget")
    except Exception as e:
        st.error(e)

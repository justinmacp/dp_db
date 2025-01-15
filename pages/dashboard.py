import streamlit as st
from src.utils import mechanisms, io
import navigation_bar
from src.utils import consts
import yaml


def setup_sidebar(query_type_l: str):
    """
    Set up the sidebar in the interface  with all settings and user info

    :param query_type_l: The query type must be passed as one of the elements in consts.QUERY_TYPES. It is required as
    some of the sidebar settings are only applicable to certain query types
    :return: The settings that the user chose: epsilon, lower bound, upper bound (for queries with unbounded
    sensitivity) and bin sizes (for histogram queries)
    """
    navigation_bar.make_sidebar()
    st.sidebar.write(f"Logged in as {st.session_state.username}")
    st.sidebar.header("Settings")
    query_budget_l = st.sidebar.write(f"Your total privacy budget is {st.session_state.privacy_budget:.3f}")
    epsilon_l = st.sidebar.number_input(
        "Epsilon (privacy budget for query)",
        min_value=0.001, max_value=query_budget_l, value=1.0, step=0.001, format="%0.3f"
    )
    if query_type_l in consts.BOUNDED_QUERY_TYPES:
        lower_bound_l = st.sidebar.number_input("Lower bound", value=1.0, step=0.001, format="%0.3f")
        upper_bound_l = st.sidebar.number_input(
            "Upper bound", min_value=lower_bound_l + 0.001, value=2.0, step=0.001, format="%0.3f"
        )
    else:
        lower_bound_l = None
        upper_bound_l = None

    if query_type_l == "Histogram":
        bin_size_l = st.sidebar.number_input("Bin Size", min_value=1, value=1, step=1)
    else:
        bin_size_l = None
    return epsilon_l, lower_bound_l, upper_bound_l, bin_size_l


def run_query(
        epsilon_l: float,
        query_type_l: str,
        column_name_l: str,
        column_name_2_l: str,
        lower_bound_l: float,
        upper_bound_l: float,
        bin_size_l: int,
        categories_l: str,
        categories_2_l: str
):
    """
    This function instantiates the button to run the query and waits for the button to be pressed to display the query
    result.

    :param epsilon_l: The privacy budget to be used for the query (non-zero positive number)
    :param query_type_l: The query type (from consts.QUERY_TYPES)
    :param column_name_l: The column name to be used for column aggregations
    :param column_name_2_l: The second column name to be used for queries that aggregate on two columns
    :param lower_bound_l: The lower bound for a query with unbounded sensitivity
    :param upper_bound_l: The lower bound for a query with unbounded sensitivity. It is strictly larger than
    lower_bound_l
    :param bin_size_l: The bin size for the histogram query. It is a non-zero positive integer
    :param categories_l: The categories for column_name_1. The format requires comma separation and the options must be
    enclosed with double quotes
    :param categories_2_l: The categories for column_name_2. The format requires comma separation and the options must
    be enclosed with double quotes
    :return: Returns consts.ERROR_CODE if the query fails
    """
    if st.button("Run Query"):
        try:
            if st.session_state.privacy_budget >= epsilon_l:
                if query_type_l == "Count":
                    dp_result = mechanisms.count_with_laplacian_mechanism(
                        epsilon=epsilon_l, db=consts.DATABASE, username=st.session_state.username
                    )
                    st.write(f"Differentially Private Count: {dp_result}")
                elif query_type_l == "Sum":
                    dp_result = mechanisms.sum_with_laplacian_mechanism(
                        column=column_name_l,
                        epsilon=epsilon_l,
                        lower_bound=lower_bound_l,
                        upper_bound=upper_bound_l,
                        db=consts.DATABASE,
                        username=st.session_state.username
                    )
                    st.write(f"Differentially Private Sum: {dp_result}")
                elif query_type_l == "Average":
                    dp_result = mechanisms.average_with_laplacian_mechanism(
                        column=column_name_l,
                        epsilon=epsilon_l,
                        lower_bound=lower_bound_l,
                        upper_bound=upper_bound_l,
                        db=consts.DATABASE,
                        username=st.session_state.username
                    )
                    st.write(f"Differentially Private Average: {dp_result}")
                elif query_type_l == "Histogram":
                    dp_result = mechanisms.histogram_with_laplacian_mechanism(
                        column=column_name_l,
                        epsilon=epsilon_l,
                        lower_bound=lower_bound_l,
                        upper_bound=upper_bound_l,
                        bin_size=bin_size_l,
                        db=consts.DATABASE,
                        username=st.session_state.username
                    )
                    st.write(f"Differentially private Histogram:")
                    st.write(dp_result)
                elif query_type_l == "Bar Chart":
                    dp_result = mechanisms.bar_chart_with_laplacian_mechanism(column=column_name_l,
                                                                              group_members=categories_l,
                                                                              epsilon=epsilon_l, db=consts.DATABASE,
                                                                              username=st.session_state.username)
                    st.write(f"Differentially private Bar Chart:")
                    st.write(dp_result)
                elif query_type_l == "Contingency Table":
                    dp_result = mechanisms.contingency_table_with_laplacian_mechanism(column_1=column_name_l,
                                                                                      group_members_1=categories_l,
                                                                                      column_2=column_name_2_l,
                                                                                      group_members_2=categories_2_l,
                                                                                      epsilon=epsilon_l,
                                                                                      db=consts.DATABASE,
                                                                                      username=st.session_state.username)
                    st.write(f"Differentially private Contingency Table:")
                    st.write(dp_result)
            else:
                raise Exception("The privacy budget allocated to this query exceeds your current total privacy budget")
        except Exception as e:
            st.error(e)
            return consts.ERROR_CODE


def setup_main_dashboard():
    """
    Set up the main dashboard including the selector for the query type and other options for the query.

    :return: Returns the query settings including query type, column names and categories of the columns
    """
    st.title("Differential Privacy Web Interface")
    query_type_l = st.selectbox("Select Query Type", options=consts.QUERY_TYPES)

    if query_type_l in consts.BOUNDED_QUERY_TYPES:
        column_name_l = st.selectbox("Select Column", options=numerical_columns)
    else:
        column_name_l = None

    if query_type_l in consts.CATEGORY_QUERY_TYPES:
        column_name_l = st.selectbox("Select Column", options=categorical_columns)
        categories_l = st.text_input("Categories enclosed in Quotation Marks and Comma Separated")
    else:
        categories_l = None

    if query_type_l == "Contingency Table":
        column_name_2_l = st.selectbox("Select Second Column", options=categorical_columns)
        categories_2_l = st.text_input("Categories of second column enclosed in Quotation Marks and Comma Separated")
    else:
        column_name_2_l = None
        categories_2_l = None
    return query_type_l, column_name_l, column_name_2_l, categories_l, categories_2_l


if __name__ == "__main__":
    st.session_state.privacy_budget = float(
        io.query_database(f"SELECT current_privacy_budget FROM users WHERE name = '{st.session_state.username}'",
                          consts.DATABASE)[0][0])

    with open(consts.SCHEMA) as file:
        db_schema = yaml.load(file, Loader=yaml.loader.SafeLoader)

    numerical_columns = db_schema[consts.TABLE_NAME]['numerical']
    categorical_columns = db_schema[consts.TABLE_NAME]['categorical']

    query_type, column_name, column_name_2, categories, categories_2 = setup_main_dashboard()

    epsilon, lower_bound, upper_bound, bin_size = setup_sidebar(query_type)

    run_query(epsilon, query_type, column_name, column_name_2, lower_bound, upper_bound, bin_size, categories,
              categories_2)

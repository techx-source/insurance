import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import pickle


# Load the trained model
loaded_pipeline = pickle.load(open('modelinsurance.pkl', 'rb'))

def set_background_color():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #add8e6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# Function to calculate BMI
def calculate_bmi(weight, height):
    """Calculate BMI using weight (in kg) and height (in meters)"""
    bmi = weight / (height ** 2)
    return bmi

# Function to ensure the 'points' column exists
def add_points_column_if_not_exists():
    conn = sqlite3.connect('bmi_data.db')
    cursor = conn.cursor()

    # Check if the points column exists
    cursor.execute("PRAGMA table_info(bmi_data);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    # If points column doesn't exist, add it
    if 'points' not in column_names:
        cursor.execute("ALTER TABLE bmi_data ADD COLUMN points INTEGER DEFAULT 0;")

    conn.commit()
    conn.close()

# Function to recreate the table if it doesn't exist
def recreate_bmi_table():
    conn = sqlite3.connect('bmi_data.db')
    cursor = conn.cursor()

    # Create the table with the points column if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bmi_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT,
        weight REAL,
        height REAL,
        bmi REAL,
        age INTEGER,
        sex TEXT,
        children INTEGER,
        smoker TEXT,
        region TEXT,
        points INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

# Call the function to ensure the table and points column exist
recreate_bmi_table()
add_points_column_if_not_exists()

# Function to plot BMI changes from the database
def plot_bmi_changes():
    conn = sqlite3.connect('bmi_data.db')
    query = "SELECT bmi FROM bmi_data"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Check if data is present
    if df.empty:
        st.write("No BMI data found.")
        return

    bmi_changes = df['bmi'].tolist()

    plt.figure(figsize=(10, 6))
    plt.plot(bmi_changes, marker='o', linestyle='-', color='b')
    plt.title('BMI Changes Over Time')
    plt.xlabel('Input Number')
    plt.ylabel('BMI')
    plt.grid(True)
    st.pyplot(plt)

# Function to get the previous BMI
def get_previous_bmi(name):
    conn = sqlite3.connect('bmi_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT bmi FROM bmi_data WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

# Function to get the current points
def get_current_points(name):
    conn = sqlite3.connect('bmi_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT points FROM bmi_data WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return 0

# Function to save data to the database
def save_to_database(name, dob, weight, height, bmi, age, sex, children, smoker, region, points):
    conn = sqlite3.connect('bmi_data.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO bmi_data (name, dob, weight, height, bmi, age, sex, children, smoker, region, points)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, dob, weight, height, bmi, age, sex, children, smoker, region, points))

    conn.commit()
    conn.close()

# Function to display the prediction page
def show_prediction_page():
    st.title("Insurance Premium Prediction")

    name = st.text_input("Enter your name")
    dob = st.date_input("Enter your date of birth")

    weight = st.number_input("Enter your weight in kg", min_value=0.0, value=70.0, step=0.1)
    height = st.number_input("Enter your height in meters", min_value=0.0, value=1.75, step=0.01)

    bmi = calculate_bmi(weight, height)
    st.write(f"Your calculated BMI is: {bmi:.2f}")

    age = st.number_input("Enter your age", min_value=0, value=25, step=1)
    sex = st.selectbox("Select your sex", ["male", "female"])
    children = st.number_input("Enter number of children", min_value=0, value=0, step=1)
    smoker = st.selectbox("Are you a smoker?", ["yes", "no"])
    region = st.selectbox("Enter your region", ["northeast", "northwest", "southeast", "southwest"])

    # Create a DataFrame with the inputs
    input_data = pd.DataFrame({
        'age': [age],
        'sex': [sex],
        'bmi': [bmi],
        'children': [children],
        'smoker': [smoker],
        'region': [region]
    })

    # Handle points logic
    previous_bmi = get_previous_bmi(name)
    current_points = get_current_points(name)

    if previous_bmi and bmi < previous_bmi:
        current_points += 5  # Add 5 points for lowering BMI

    # Predict insurance charges
    if st.button("Predict Insurance Charges"):
        prediction = loaded_pipeline.predict(input_data)

        # Output the prediction
        st.write(f"Predicted Charges: {prediction[0]:.2f} USD")
        st.write(f"Estimated Monthly Premium: {prediction[0] / 12:.2f} USD")

        # Save the data to the database
        save_to_database(name, dob, weight, height, bmi, age, sex, children, smoker, region, current_points)

    # Button to show BMI changes
    if st.button("Show BMI Changes"):
        plot_bmi_changes()

    # Button to display current points
    if st.button("Show Points"):
        st.write(f"Your current points: {current_points}")

# Function to display the login page
def show_login_page():
    st.title("Login")

    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login"):
        # Simple login validation (you can replace it with database or API-based validation)
        if username == "admin" and password == "Techx":
            st.session_state['logged_in'] = True
            st.success("Login successful! Redirecting...")
        else:
            st.error("Invalid username or password")

# Main function to control app flow
def main():
    # Check if the user is logged in
    set_background_color()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # If logged in, show prediction page, else show login page
    if st.session_state['logged_in']:
        show_prediction_page()
    else:
        show_login_page()

# Run the app
if __name__ == "__main__":
    main()

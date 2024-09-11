#load the libraries
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import pickle

# Read the dataset
data = pd.read_csv('expenses.csv')
#check for null values
print(data.info())
#check the rows and columns
print(data.head())
print(data.columns)


# Define column transformer ( without 'charges')
column_transformer = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['age', 'bmi']),  # Apply StandardScaler to 'age' and 'bmi'
        ('cat', OneHotEncoder(), ['sex', 'children', 'smoker', 'region'])  # Apply OneHotEncoder to categorical columns
    ]
)

#spliting the training parts
X = data.drop('charges', axis=1)
y = data['charges']

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# create a pipeline to apply the transformations and train the model
training_pipeline = Pipeline(steps=[
    ('preprocessor', column_transformer),
    ('model', GradientBoostingRegressor())
])

# train the model
training_pipeline.fit(x_train, y_train)


# save it into a model
pickle.dump(training_pipeline, open('modelinsurance.pkl', 'wb'))

# Load the model for prediction
loaded_pipeline = pickle.load(open('modelinsurance.pkl', 'rb'))


# Example input 
input_data = pd.DataFrame({
    'age': [28],
    'sex': ['male'],
    'bmi': [33.0],
    'children': [3],
    'smoker': ['no'],
    'region': ['southeast']
})

# Use the same pipeline to transform and predict on new data
prediction = loaded_pipeline.predict(input_data)

# Print the prediction
print(f"Predicted Charges: {prediction[0]}")
print("Monthly Premium",prediction[0]/12)

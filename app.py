from flask import Flask, render_template, request
import pandas as pd
import pickle
import numpy as np

# Load your trained model
model = pickle.load(open('clean_random_forest_model.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract form data using the exact names from the HTML input fields
        features = [
            float(request.form['Liquid Volume (m3/day)']),
            float(request.form['Gas Volume (m3/day)']),
            float(request.form['Water Volume (m3/day)']),
            float(request.form['Water Cut (%)']),
            float(request.form['Working Hours']),
            float(request.form['Dynamic Level (m)']),
            float(request.form['Reservoir Pressure (atm)'])
        ]

        final_features = [np.array(features)]
        prediction = model.predict(final_features)[0]

        return render_template('index.html', prediction_text=f'Predicted Oil Production: {prediction:.2f}')
    except Exception as e:
        print("Prediction error:", e)
        return render_template('index.html', prediction_text='⚠️ Error: Please enter valid numerical values.')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
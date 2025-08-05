# app.py
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import pickle
import numpy as np
import os

# Load your trained model
model = pickle.load(open('clean_random_forest_model.pkl', 'rb'))

app = Flask(__name__)

CSV_FILE = 'predictions.csv'

@app.route('/')
def home():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        predictions = df.to_dict('records')
        columns = list(df.columns)[:-2]  # exclude 'Prediction' and 'Anomaly Status'
    else:
        predictions = []
        columns = ['Liquid Volume', 'Gas Volume', 'Water Volume', 'Water Cut (%)',
                   'Working Hours', 'Dynamic Level', 'Reservoir Pressure']

    return render_template('index.html', predictions=predictions, columns=columns)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract form data
        liquid = float(request.form['Liquid Volume (m3/day)'])
        gas = float(request.form['Gas Volume (m3/day)'])
        water = float(request.form['Water Volume (m3/day)'])
        cut = float(request.form['Water Cut (%)'])
        hours = float(request.form['Working Hours'])
        level = float(request.form['Dynamic Level (m)'])
        pressure = float(request.form['Reservoir Pressure (atm)'])

        features = [liquid, gas, water, cut, hours, level, pressure]
        final_features = [np.array(features)]
        prediction = model.predict(final_features)[0]

        # Anomaly & Improvement Suggestions
        if prediction < 10:
            anomaly_msg = "⚠️ Very Low Production."
            tip = "💡 Try increasing Liquid Volume and reducing Water Cut (%)."
        elif prediction > 300:
            anomaly_msg = "⚠️ Unusually High Production."
            tip = "💡 Check if Gas Volume or Working Hours are too high or incorrect."
        else:
            anomaly_msg = "✅ Production is normal."
            tip = "👍 Inputs look good!"

        # Save to CSV
        row = [[liquid, gas, water, cut, hours, level, pressure, round(prediction, 2), anomaly_msg]]
        columns = ['Liquid Volume', 'Gas Volume', 'Water Volume', 'Water Cut (%)',
                   'Working Hours', 'Dynamic Level', 'Reservoir Pressure', 'Prediction', 'Anomaly Status']

        df = pd.DataFrame(row, columns=columns)

        if os.path.exists(CSV_FILE):
            df.to_csv(CSV_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(CSV_FILE, index=False)

        predictions = pd.read_csv(CSV_FILE).to_dict('records')

        return render_template('index.html',
                               prediction_text=f'Predicted Oil Production: {prediction:.2f}',
                               anomaly_text=anomaly_msg,
                               suggestion_text=tip,
                               predictions=predictions,
                               columns=columns[:-2])

    except Exception as e:
        print("Prediction error:", e)
        return render_template('index.html',
                               prediction_text='⚠️ Error: Please enter valid numerical values.',
                               anomaly_text='',
                               suggestion_text='',
                               predictions=[],
                               columns=[])

@app.route('/clear')
def clear():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

# 🚗 Smart Used Car Price Prediction

An end-to-end Machine Learning project that predicts the resale price of used cars based on vehicle specifications, ownership history, and technical features.

The project demonstrates the complete machine learning lifecycle, including data preprocessing, exploratory data analysis, feature engineering, model training, evaluation, and deployment through a Streamlit web application.

---

## 📌 Project Objectives

- Predict the resale price of used cars.
- Perform comprehensive exploratory data analysis.
- Engineer meaningful features from raw data.
- Train and compare Linear Regression, Ridge, and Lasso models.
- Evaluate models using industry-standard regression metrics.
- Deploy an interactive prediction application using Streamlit.

---

## 🛠️ Tech Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Plotly
- Streamlit
- Joblib
- Git & GitHub

---

## 📂 Project Structure

```text
used-car-price-prediction/
├── app/
├── data/
├── models/
├── notebooks/
├── reports/
├── src/
├── tests/
├── README.md
└── requirements.txt
```

---

## 📊 Machine Learning Workflow

1. Data Collection
2. Data Cleaning
3. Exploratory Data Analysis
4. Feature Engineering
5. Model Training
6. Model Evaluation
7. Price Prediction
8. Streamlit Deployment

---

## 📈 Evaluation Metrics

- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- R² Score

---

## 🚀 Future Enhancements

- Car price trend analysis
- Feature importance visualization
- Similar car recommendation
- Model explainability with SHAP
- Docker deployment
- CI/CD pipeline

---

## ⚙️ Project Setup

Follow the steps below to set up the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/used-car-price-prediction.git
cd used-car-price-prediction
```

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python --version
pip list
```

### 5. Launch Jupyter Notebook

```bash
jupyter notebook
```

or

```bash
jupyter lab
```

### 6. Run the Streamlit Application

```bash
streamlit run app/app.py
```

---

## 📁 Project Structure

```text
used-car-price-prediction/
│
├── app/                # Streamlit application
├── data/
│   ├── raw/            # Original dataset
│   ├── processed/      # Cleaned dataset
│   └── external/       # External datasets
├── models/             # Saved ML models
├── notebooks/          # Jupyter notebooks
├── reports/            # Reports and visualizations
├── src/                # Source code
├── tests/              # Unit tests
├── requirements.txt
├── README.md
└── main.py
```

## 📜 License

This project is licensed under the MIT License.

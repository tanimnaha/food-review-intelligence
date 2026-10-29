# Food Review Intelligence

**Machine Learning–Powered Sentiment Analysis of Online Food Reviews**

Food Review Intelligence is a web-based machine learning project that analyzes written food reviews and predicts whether the expressed sentiment is **Positive, Negative, or Neutral**.

The project demonstrates how natural language processing and machine learning can help transform unstructured customer feedback into useful insights.

## ✨ Features

- **Sentiment Prediction:** Analyze a food review and classify its sentiment.
- **Multiple Sentiment Classes:** Supports positive, negative, and neutral reviews.
- **Model Comparison:** Compare Logistic Regression, Linear SVM, and Multinomial Naive Bayes.
- **Dataset Insights:** Explore the distribution of sentiment labels and model evaluation results.
- **Interactive Web Interface:** A user-friendly interface built with Streamlit.

## 🧠 Machine Learning

Three classification algorithms were evaluated on a dataset of 14,351 food reviews.

| Model | Accuracy |
|---|---:|
| Logistic Regression | 82.44% |
| Linear SVM | 83.97% |
| Multinomial Naive Bayes | 75.40% |

Logistic Regression was selected as the best model based on macro F1-score, while Linear SVM achieved the highest overall accuracy.

These results illustrate why model evaluation should consider multiple metrics, particularly when sentiment classes are imbalanced.

## 🛠️ Technology Stack

- Python
- Streamlit
- Scikit-learn
- Pandas
- Joblib
- Matplotlib and Seaborn

## 📊 Dataset

The project uses a labelled Yelp restaurant-review dataset containing 14,351 records. The target variable contains three sentiment classes: Positive, Negative, and Neutral.

## 🎯 Project Objective

The objective is to build an interactive demonstration of sentiment classification and compare traditional machine learning algorithms for understanding customer feedback.

## ⚠️ Limitations

Predictions are model estimates and may not correctly interpret sarcasm, mixed opinions, context, or subtle language. Neutral sentiment is more difficult to classify reliably than positive sentiment in the evaluated models.

## 👨‍💻 Academic Project

Developed as a B.Tech Computer Science and Engineering minor project at Amity University Kolkata.

**Project:** Sentiment Analysis of Online Food Reviews

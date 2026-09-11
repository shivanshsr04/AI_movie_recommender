# 🎬 AI Movie Recommender System

A machine-learning based movie recommendation system that combines **content-based filtering, collaborative filtering, matrix factorization, and hybrid recommendation techniques** to generate personalized movie recommendations.

The project is built with Python and Streamlit and is designed to demonstrate how different recommendation approaches can be combined into a single end-to-end recommendation pipeline.

---

## 🚀 Features

* 🎭 **Content-Based Recommendation**

  * Recommends movies based on their content and metadata.
  * Uses TF-IDF vectorization and cosine similarity.

* 👥 **Collaborative Filtering**

  * Uses user-rating behavior to identify movies that may be preferred by similar users.

* 🧮 **Matrix Factorization**

  * Uses SVD-based collaborative filtering to estimate user–movie preferences.

* 🔀 **Hybrid Recommendation**

  * Combines multiple recommendation signals to produce a unified ranking.

* 🎬 **Interactive Streamlit Application**

  * Search/select movies and receive recommendations through a web interface.

* 📊 **Recommendation Evaluation**

  * Provides an evaluation framework for measuring recommendation quality using ranking and prediction metrics.

* 💾 **Persistent User Data**

  * Uses SQLite for storing application user information.

---

# 🧠 How It Works

The system follows a multi-stage recommendation pipeline:

```text
                    Movie Dataset
                         │
                         ▼
                  Data Preprocessing
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
          Content     Collaborative   SVD
          Model          Model        Model
              │          │          │
              └──────────┼──────────┘
                         ▼
                  Score Processing
                         │
                         ▼
                  Hybrid Ranking
                         │
                         ▼
                Top-K Recommendations
                         │
                         ▼
                 Streamlit Interface
```

---

# 🧩 Recommendation Methods

## 1. Content-Based Filtering

The content-based model recommends movies that are similar to a movie selected by the user.

Movie metadata such as:

* Genres
* Keywords
* Overview
* Other available textual features

is combined into a text representation.

The text is converted into numerical vectors using **TF-IDF (Term Frequency–Inverse Document Frequency)**.

Cosine similarity is then used to determine how similar two movies are.

### Simplified pipeline

```text
Movie Metadata
      ↓
Text Preprocessing
      ↓
TF-IDF Vectorization
      ↓
Movie Vectors
      ↓
Cosine Similarity
      ↓
Similar Movies
```

---

## 2. Collaborative Filtering

Collaborative filtering focuses on **user behavior rather than movie metadata**.

The model uses user-rating information to identify relationships between users and movies.

The underlying idea is:

> Users who have demonstrated similar preferences may also enjoy similar movies.

This allows the system to recommend movies that may not necessarily be similar in genre or description but are preferred by users with comparable rating patterns.

---

## 3. Matrix Factorization / SVD

The system also uses **Singular Value Decomposition (SVD)** to model latent relationships between users and movies.

Instead of directly comparing users and movies, matrix factorization represents them in a lower-dimensional latent space.

Conceptually:

```text
User × Movie Rating Matrix
            ↓
     Matrix Factorization
            ↓
      Latent Features
            ↓
 Predicted User Preferences
            ↓
       Recommendations
```

This approach helps discover hidden preference patterns in rating data.

---

# 🔀 Hybrid Recommendation

Different recommendation techniques have different strengths.

For example:

| Method                  | Main Signal        | Strength                               |
| ----------------------- | ------------------ | -------------------------------------- |
| Content-Based           | Movie metadata     | Handles item similarity                |
| Collaborative Filtering | User behavior      | Captures community preferences         |
| SVD                     | Latent preferences | Models hidden user–movie relationships |
| Hybrid                  | Multiple signals   | Combines complementary information     |

The hybrid recommender combines these signals to create a final recommendation ranking.

Before combining scores, the individual model outputs should be placed on comparable scales so that one model does not dominate the final ranking simply because its numerical scores are larger.

---

# 🏗️ Project Structure

```text
movie-recommender-system/
│
├── data/
│   └── Dataset files
│
├── models/
│   └── Trained/saved recommendation models
│
├── utils/
│   └── Helper modules
│
├── streamlit_app.py
│   └── Streamlit application
│
├── recommender_models.py
│   └── Recommendation algorithms
│
├── data_loader.py
│   └── Dataset loading and preprocessing
│
├── train_models.py
│   └── Model training pipeline
│
├── train_simple_models.py
│   └── Simplified model-training utilities
│
├── requirements.txt
│   └── Python dependencies
│
├── config.toml
│   └── Application configuration
│
├── users.db
│   └── SQLite database
│
└── README.md
    └── Project documentation
```

---

# ⚙️ Technologies Used

### Programming

* Python

### Machine Learning

* Scikit-learn
* TF-IDF
* Cosine Similarity
* Collaborative Filtering
* SVD / Matrix Factorization

### Data Processing

* Pandas
* NumPy

### Application

* Streamlit

### Database

* SQLite

### Development

* Git
* GitHub

---

# 🛠️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/shivanshsr04/AI_movie_recommender.git
cd AI_movie_recommender
```

## 2. Create a virtual environment

```bash
python3 -m venv venv
```

## 3. Activate the environment

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

After activating the virtual environment:

```bash
streamlit run streamlit_app.py
```

The application will open in your browser.

If Streamlit provides a local address such as:

```text
http://localhost:8501
```

open that address in your browser.

---

# 📊 Model Evaluation

Recommendation systems should be evaluated using metrics appropriate to the task.

The project is intended to evaluate:

### Ranking Metrics

* Precision@K
* Recall@K
* NDCG@K

### Rating Prediction

* RMSE

### Baseline Comparison

The recommendation models should be compared against a simple baseline such as:

```text
Popularity-Based Recommendations
```

This allows us to determine whether the machine-learning models provide meaningful improvement over a straightforward recommendation strategy.

---

# 🧪 Experimental Design

A reproducible evaluation pipeline should follow this general process:

```text
Ratings Dataset
      ↓
Train / Validation / Test Split
      ↓
Train Recommendation Models
      ↓
Generate Top-K Recommendations
      ↓
Compare Against Ground Truth
      ↓
Calculate Metrics
      ↓
Compare Models
```

The final reported metrics should be generated directly from this evaluation pipeline rather than manually entered.

---

# 🎯 Cold-Start Considerations

Recommendation systems face a **cold-start problem** when there is insufficient information about a new user or movie.

Possible strategies include:

### New User

Use:

* Popular movies
* Genre preferences
* Initial movie selections

### New Movie

Use:

* Movie metadata
* Genres
* Keywords
* Overview

A hybrid system can therefore combine behavioral and content information to reduce the limitations of either approach individually.

---

# 🖥️ Application

The Streamlit application provides an interactive interface for exploring movie recommendations.

The intended user flow is:

```text
Select Movie
     ↓
Process Movie/User Information
     ↓
Run Recommendation Models
     ↓
Combine Recommendation Signals
     ↓
Rank Movies
     ↓
Display Top Recommendations
```

---

# 🔮 Future Improvements

Potential improvements include:

* Neural collaborative filtering
* Better cold-start handling
* Personalized recommendation history
* Improved hybrid-weight optimization
* A/B testing
* Recommendation explanations
* Temporal preference modeling
* Graph-based recommendation
* User feedback loops
* More robust evaluation
* Improved recommendation diversity
* Production-grade authentication
* Model monitoring

---

# 📌 Learning Objectives

This project demonstrates practical experience with:

* Data preprocessing
* Feature engineering
* TF-IDF vectorization
* Similarity-based recommendation
* Collaborative filtering
* Matrix factorization
* Recommendation ranking
* Machine-learning evaluation
* Python application development
* Streamlit deployment
* SQLite integration
* Git/GitHub workflow

---

# 👨‍💻 Author

**Shivansh Srivastava**

B.Tech — Information Technology

GitHub:
https://github.com/shivanshsr04

---

# 📄 License

This project is intended for educational and portfolio purposes.

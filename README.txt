FOOD REVIEW SENTIMENT ANALYZER — STREAMLIT DEMO

IMPORTANT
This is the web-interface code for your existing Sentiment_Analysis_Minor_Project. It expects the trained model from your project. The model file was not available in the workspace where this package was prepared, so the integration must be tested on your Mac with your actual results/best_model.joblib file before you present it.

EXPECTED PROJECT STRUCTURE
Sentiment_Analysis_Minor_Project/
  .venv/
  results/
    best_model.joblib
    best_model_name.txt            (optional)
    model_comparison.csv           (optional)
  streamlit_app/
    app.py

STEP-BY-STEP ON YOUR MAC
1. Download and unzip sentiment_web_demo.zip.
2. Open the unzipped folder and copy the streamlit_app folder into your existing Sentiment_Analysis_Minor_Project folder. Merge folders if macOS asks; do not replace your existing results or src folders.
3. Open VS Code and open the Sentiment_Analysis_Minor_Project folder (the project root).
4. Open Terminal in VS Code and run:

   source .venv/bin/activate
   python -m pip install streamlit
   streamlit run streamlit_app/app.py

5. Streamlit should open a browser page, usually at http://localhost:8501. If it does not open automatically, copy that address into Safari or Chrome.
6. Test all three example reviews. Confirm positive, negative and neutral predictions appear. Also test one review of your own.
7. Keep the terminal running during the demonstration. To stop the website, click the terminal and press Control+C.

IF YOU GET AN ERROR
- “Model file not found”: confirm results/best_model.joblib exists in your project root.
- Error that raw strings cannot be converted / text is not vectorized: your saved best_model.joblib may contain only the classifier, not the fitted text vectorizer + classifier pipeline. Open src/train_models.py and ensure you save the complete fitted pipeline into results/best_model.joblib, then rerun the training script. Do not just rename the classifier file.
- “streamlit: command not found”: make sure .venv is activated and run `python -m pip install streamlit`.
- Port 8501 is busy: run `streamlit run streamlit_app/app.py --server.port 8502`, then open http://localhost:8502.

WHAT TO SAY IN THE LIVE DEMO
“I will enter a customer review. The saved text-classification pipeline processes the review and predicts whether its sentiment is positive, negative or neutral. This is inference using the trained model; it is not retraining the model.”

Do not claim a prediction is accurate just because the app displays it. The overall test metrics and the weaker neutral-class result are discussed in the Results slide.

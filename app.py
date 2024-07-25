from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from textblob import TextBlob

# Load the dataset
df = pd.read_csv('European Restaurant Reviews.csv')

# Calculate sentiment and subjectivity
df['calc_sentiment'] = df['Review Title'].apply(lambda x: TextBlob(x).sentiment.polarity)
df['subjectivity'] = df['Review Title'].apply(lambda x: TextBlob(x).sentiment.subjectivity)

# Define the list of words you want to use for filtering
word_list = ["disgusting", "delicious", "overpriced", "wait", "service", "experience"]

# Filter reviews based on the presence of keywords and compute subjectivity and sentiment for each keyword
data = []
for word in word_list:
    for _, row in df[df['Review'].str.contains(word, case=False, na=False)].iterrows():
        data.append({'keyword': word, 'subjectivity': row['subjectivity'], 'calc_sentiment': row['calc_sentiment']})

filtered_df = pd.DataFrame(data)

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    [
        html.H2(
            "Sentiment and Subjectivity Analysis of Reviews by Keyword",
            style={"textAlign": "center"},
        ),
        html.Div("Choose Keywords:"),
        dcc.Dropdown(
            id="keyword-dropdown",
            value=word_list[:2],  # Default selected words
            options=[{"label": word, "value": word} for word in word_list],
            multi=True,
        ),
        html.Div("Choose Feature:"),
        dcc.RadioItems(
            id="feature-radio",
            options=[
                {'label': 'Sentiment', 'value': 'calc_sentiment'},
                {'label': 'Subjectivity', 'value': 'subjectivity'},
            ],
            value='calc_sentiment',  # Default selected feature
            style={"margin": "1em 0"}
        ),
        dcc.Graph(id="analysis-graph"),
    ],
    style={"margin": "1em 5em", "fontSize": 18},
)

# Define the callback to update the graph
@app.callback(
    Output("analysis-graph", "figure"),
    [Input("keyword-dropdown", "value"),
     Input("feature-radio", "value")]
)
def update_graph(selected_keywords, selected_feature):
    if not selected_keywords:
        selected_keywords = word_list[:2]  # Default selection if none selected
    
    # Filter the DataFrame based on selected keywords
    filtered_data = filtered_df[filtered_df["keyword"].isin(selected_keywords)]

    # Create a box plot with different colors for each keyword
    color_discrete_map = {word: px.colors.qualitative.Plotly[i] for i, word in enumerate(word_list)}
    
    fig = px.box(
        filtered_data,
        x="keyword",
        y=selected_feature,
        title=f"{'Sentiment' if selected_feature == 'calc_sentiment' else 'Subjectivity'} Distribution by Keyword",
        labels={"keyword": "Keyword", "calc_sentiment": "Sentiment", "subjectivity": "Subjectivity"},
        template="plotly_white",
        color="keyword",
        color_discrete_map=color_discrete_map
    )
    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

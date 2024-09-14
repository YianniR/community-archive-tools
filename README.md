# Community Archive Analysis Tool

This project provides tools for sentiment analysis, thread exploration, and graph building on Twitter data from the [Community Archive](https://github.com/TheExGenesis/community-archive) project.

## Features

- Fetch Twitter data from the Community Archive
- Build and analyze tweet graphs
- Perform sentiment analysis on tweets
- Explore tweet threads and visualize connections
- Generate keyword statistics and trends
- Analyze user statistics

## Setup

1. Clone this repository:

   ```
   git clone https://github.com/YianniR/community-archive-scripts.git
   cd community-archive-analysis-tool
   ```
2. Create and activate a virtual environment (optional but recommended):

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with your API credentials:

   ```
   API_TOKEN=your_api_token_here
   ```

   (Do not commit this file to version control)
5. Download necessary NLTK data:

   ```
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## Usage

The main script supports several commands:

1. Fetch data:

   ```
   python main.py fetch_data [--username <twitter_username>]
   ```
2. Build graph:

   ```
   python main.py build_graph [--input <input_file>] [--output <output_file>]
   ```
3. Run sentiment analysis:

   ```
   python main.py sentiment_analysis [--input <input_file>] [--days <number_of_days>] [--username <twitter_username>] [--ma-window <moving_average_window>]
   ```
4. Explore threads:

   ```
   python main.py visualise_threads [--method <method>] [--num-subgraphs <num>]
   ```
5. Generate keyword statistics:

   ```
   python main.py keyword_stats [--input <input_file>] [--top-n <number_of_keywords>]
   ```
6. Analyze keyword trends:

   ```
   python main.py keyword_trends [--input <input_file>] [--days <number_of_days>] [--username <twitter_username>] [--keywords <comma_separated_keywords>] [--ma-window <moving_average_window>]
   ```
7. Generate user statistics:

   ```
   python main.py user_stats [--tweets-file <tweets_file>] [--username <twitter_username>] [--print-sample]
   ```

## Modules

- `common/`: Contains utility functions and data fetching scripts
- `keyword_stats/`: Analyzes keyword frequencies in tweets
- `keyword_trends/`: Tracks keyword usage trends over time
- `sentiment_analysis/`: Performs sentiment analysis on tweets
- `thread_explorer/`: Visualizes and analyzes tweet threads
- `user_stats/`: Generates statistics for individual Twitter users

## Acknowledgements

This project uses data from the [Community Archive](https://github.com/TheExGenesis/community-archive) project. We thank all the contributors to that project for making this data available for analysis.

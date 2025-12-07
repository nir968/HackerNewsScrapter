import argparse
from src.processor import run_scrapting_pipeline
from src.output_writer import write_to_csv
 
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="A web scraper for Hacker News articles."
    )

    parser.add_argument(
        "--min-score",
        type=int,
        default=0,
        help='Minimum score threshold for filtering posts. '
    )

    parser.add_argument(
        "--max-score",
        type=int,
        default=1000,
        help='Maximum score threshold for filtering posts. '
    )

    parser.add_argument(
        "--max-posts",
        type=int,
        default=50,
        help='Maximum number of posts to collect. '
    )

    parser.add_argument(
        "--skip-pages",
        type=int,
        default=[],
        help='List of page numbers to skip during scraping. '
    )

    parser.add_argument(
        "--output-file",
        type=str,
        default="hacker_news_results.csv",
        help='The name of the CSV file to write results to. '
    )


    args = parser.parse_args()
    return args

def main():

    config = parse_arguments()
    print(f"Starting scraper with config: {config}")
    #new
    allposts = run_scrapting_pipeline(config)

    if allposts:
        write_to_csv(allposts, config.output_file)
        print(f"Results written to {config.output_file}")
    else:
        print("No posts collected; no output file created.")
        
    print("*** Scraping finished ***\n") 

if __name__ == "__main__":
    main()      
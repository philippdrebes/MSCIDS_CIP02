# Hiking Routes in Switzerland

This project aims to extract hiking routes data from the websites SAC, Schweizmobil, and Komoot. The data includes route descriptions, difficulty, distance, elevation change, and other relevant information.

## Prerequisites

To run the project, you need to have Python 3 installed on your machine, as well as the following packages:
- selenium
- beautifulsoup4
- pandas
- mariadb

We recommend using virtualenv to manage dependencies.

## Installation

1. Clone the repository to your local machine.
2. Create a virtual environment using virtualenv.
3. Activate the virtual environment.
4. Install the dependencies using `pip install -r requirements.txt`.
5. Configure the database connection in `main.py`.

## Usage

To scrape the data, run `main.py`. This script will call the extractors for each website and save the data to a MariaDB instance. You can configure the output location and format in the `main.py` script.

## Repository Structure

The repository is organized as follows:

- `docs`: documentation files
- `src`: source code files
  - `extractors`: website-specific extraction code
    - `KomootExtractor.py`: extractor for Komoot website
    - `SacExtractor.py`: extractor for SAC website
    - `SchweizmobilExtractor.py`: extractor for Schweizmobil website
    - `SeleniumUtil.py`: utility functions for Selenium web driver
  - `main.py`: main script to run the data extraction process
- `Makefile`: makefile with common tasks
- `requirements.txt`: list of required packages
- `README.md`: this file

## Contributing

If you find any issues or have suggestions for improvement, please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

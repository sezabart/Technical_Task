# Typless Technical Task

This project is a technical task for the Typless application. It demonstrates the implementation of a simple user interface for the main Typless API.

## Getting Started

### Prerequisites

Ensure you have the following installed:
- [Python 3.8+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/sezabart/Technical_Task.git
    cd typless-technical-task
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Running the Project

Before running the project, ensure you have set the Typless API key as an environment variable:

- On Windows:
    ```sh
    set TYPLESS_API_KEY=your_api_key_here
    ```
- On macOS/Linux:
    ```sh
    export TYPLESS_API_KEY=your_api_key_here
    ```


To start the project, run the following command:
```sh
python main.py
```

The webserver will present itself on http://0.0.0.0:5001

## Project Structure

- `main.py`: The main entry point of the application.
- `requirements.txt`: List of dependencies required for the project.
- `README.md`: This file.

## Contributing

Feel free to fork this repository and submit pull requests.

## License

This project is licensed under the MIT License.

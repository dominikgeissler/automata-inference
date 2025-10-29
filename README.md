## Setup
* (Optional) Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

* Install poetry, see [here](https://python-poetry.org/docs/)
* Install dependencies
```bash
# For visualization
sudo apt install -y graphviz

# Python dependencies
poetry install --only main
```
* Run the main program
```bash
python automata_inference/main.py
```

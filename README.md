# Intro

This is a textual interface with 16 keys to control a MIDI sequencer. This is an evolution of our previous proof of concept:

* https://github.com/matykiewicz/pulse_generator

# MacOS Install

Use virtual env, git and poetry to install this package:

```shell
python3 -m venv ~/.venv
source ~/.venv/bin/activate
pip3 install poetry
git clone https://github.com/matykiewicz/midi_seq_poc_py.git
cd midi_seq_poc_py
poetry install
```

# Minimal Hardware Requirements

You will need at least one MIDI USB converter:

* https://www.amazon.com/dp/B07L8KFYBK

# Virtual Env Run

Once the package is installed you can use it as a typical command line tool:

```shell
midi_seq
```

# Code Testing

We can test the code and output code coverage report in a following way:

```shell
poetry run pytest --cov-report html --cov
```


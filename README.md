# Intro

This is a textual interface with 16 keys to control a MIDI sequencer.

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

# Run

Once the package is installed you can use it as a typical command line tool:

```shell
poetry run midi_seq
```


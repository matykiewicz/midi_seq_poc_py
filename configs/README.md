
# Intro

We need some DSL to store configs. We will have hierarchical dependencies between configs.

Here is our idea:

* MIDI messages with chaining commands
* Instruments (collection of midi messages that the instrument receives)
* Mappings (mapping instruments to MIDI devices and channels)
* Music (all of the above with notes/modes/motion spread over time and tracks)

# Notes

Music needs MIDI messages stored alongside. Instruments and mappings are convenience data structures. They only make sense for new music piece.

We prefer YAML over JSON because YAML allows comments.


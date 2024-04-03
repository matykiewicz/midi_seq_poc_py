
# Intro

We need some DSL to store presets (a.k.a. configs). We will have hierarchical dependencies between presets.

Here is our idea:

* MIDI messages with chaining commands
* Instruments (collection of midi messages that the instrument receives)
* Mappings (mapping instruments to MIDI devices and channels)
* Music (all of the above with notes/modes/motion spread over time and tracks)

# Notes

Music needs MIDI messages stored alongside. Instruments and mappings are convenience data structures. They only make sense for a new music piece. Mapping between instruments, MIDI IDs and channels are used to generate blank music "sheet".

We prefer YAML over JSON because YAML allows comments.


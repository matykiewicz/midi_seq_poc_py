# /bin/bash

IP=${IP:-192.168.8.228}
DEST="jetson@${IP}"

echo "IP = $IP"
ssh "${DEST}"  "rm -rf ~/midi_seq_poc_py"
scp -r ../midi_seq_poc_py "${DEST}":~/midi_seq_poc_py


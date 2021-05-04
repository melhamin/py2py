for arg in {1..4}
do
    python p2p.py "$arg" &
done
wait
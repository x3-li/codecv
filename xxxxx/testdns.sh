#!/bin/bash

HOST="abc.co.jp"
COUNT=100

echo "Testing DNS resolution for $HOST ($COUNT times)..."
echo "----------------------------------------------"

fail=0

for ((i=1;i<=COUNT;i++)); do
    result=$(getent hosts "$HOST")

    if [ -z "$result" ]; then
        echo "[FAIL] $i"
        ((fail++))
    else
        echo "[OK]   $i"
    fi

    # 可调节压力（默认不sleep）
    # sleep 0.01
done

echo "----------------------------------------------"
echo "Total: $COUNT"
echo "Fail:  $fail"
echo "Success: $((COUNT - fail))"
echo "Fail Rate: $(awk "BEGIN {printf \"%.2f\", $fail/$COUNT*100}") %"
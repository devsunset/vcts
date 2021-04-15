kill -9 $(ps aux | grep 'vcts' | awk '{print $2}')
echo "vcts stop..."
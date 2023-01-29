kill $(lsof -t -i:4321)
balena tunnel 9d6cb911e0cb153469c25e3e910ac831 -p 22222:4321 & \
sleep 5 && \
scp -P 4321 root@127.0.0.1:/mnt/data/docker/volumes/1987400_resin-data/_data/crowdfactor.db tmp.db
# Kill everything we've spawned.
kill -- -$$

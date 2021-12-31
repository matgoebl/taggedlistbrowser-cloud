FROM alpine:3.15.0
CMD while sleep 3; do date +'{"date":"%Y-%m-%d_%H-%M-%S","uptime":%s}' > $DATAFILE;done

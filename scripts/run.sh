#!/bin/bash

# Default values
SERVER="uvicorn"
WORKERS=4

# Function to display usage information
usage() {
    echo "Usage: $0 [-s server] [-w workers]"
    echo "  -s server  : Specify the server to use (uvicorn or gunicorn). Default is uvicorn."
    echo "  -w workers : Specify the number of workers for gunicorn. Default is 4."
    exit 1
}

# Parse command line options
while getopts ":s:w:" opt; do
    case ${opt} in
        s )
            SERVER=$OPTARG
            ;;
        w )
            WORKERS=$OPTARG
            ;;
        \? )
            echo "Invalid Option: -$OPTARG" 1>&2
            usage
            ;;
        : )
            echo "Invalid Option: -$OPTARG requires an argument" 1>&2
            usage
            ;;
    esac
done

# Validate server option
if [[ "$SERVER" != "uvicorn" && "$SERVER" != "gunicorn" ]]; then
    echo "Invalid server specified. Must be either 'uvicorn' or 'gunicorn'."
    usage
fi

# Run the application
if [[ "$SERVER" == "uvicorn" ]]; then
    echo "Starting server with Uvicorn..."
    uvicorn src.main:app --reload --log-level debug
elif [[ "$SERVER" == "gunicorn" ]]; then
    echo "Starting server with Gunicorn using $WORKERS workers..."
    gunicorn -w $WORKERS -k uvicorn.workers.UvicornWorker src.main:app
fi
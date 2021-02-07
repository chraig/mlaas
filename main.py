# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from waitress import serve

from app import create
from evaluation import run_task, run_script


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--address", 
                        default="127.0.0.1", 
                        type=str, 
                        help="Hosting URL, defaults to 127.0.0.1")

    parser.add_argument("--port", 
                        default=8888,
                        type=int, 
                        help="Hosting port, defaults to 8888")
                        
    parser.add_argument("--redis_port", 
                        default=6379,
                        type=int, 
                        help="Redis port, defaults to 6379")
                        
    parser.add_argument("--threads",
                        default=4,
                        type=int,
                        help="Waitress threads, flask is hosted with, defaults to 4")

    args = parser.parse_args()

    app = create(run_task, run_script, args.redis_port)
    serve(app, host=args.address, port=args.port, threads=args.threads)

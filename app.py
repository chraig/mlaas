# -*- coding: utf-8 -*-
import threading

from datetime import datetime
from flask import Flask, jsonify, request
from typing import Callable, Union

from middleware import RequestID

from redis_handler import RedisHandler

from applogger import (get_duration, perf_counter,
                       DEFAULT_APP_DIR, DEFAULT_APP_NAME)


def create(task_runner: Callable[[dict, dict], dict], script_runner: Callable[[dict, dict], dict],
           redis_port: Union[int, None] = None) -> Flask:
    
    app = Flask(__name__, instance_relative_config=True)
    
    # init info about app directory
    app.logger.info("App dir: {}, {}".format(DEFAULT_APP_NAME, DEFAULT_APP_DIR))

    # init of task ID distribution
    RequestID(app)

    # init Redis
    mlaas_redis = RedisHandler(redis_host="localhost", redis_port=redis_port)
    
    @app.route("/mlaas-api/test", strict_slashes=False, methods=["GET"])
    def run_test():
        log_time = perf_counter()
        try:
            app.logger.info("/mlaas-api/test, duration (s): {}".format(get_duration(log_time)))
            return jsonify({"state": "online", "time": datetime.now()})
        except Exception as ex:
            app.logger.exception("/mlaas-api/test: failed")
            return jsonify({"error": "{}".format(ex)})

    @app.route("/mlaas-api/set-task", strict_slashes=False, methods=["POST"])
    def run_background_job():
        log_time = perf_counter()
        app.logger.info("/mlaas-api/set-task, start")
        try:
            # print("Request for ID via thread {}".format(threading.get_ident()))
            input_task = request.get_json(force=True)

            task_id = request.environ.get("FLASK_REQUEST_ID")
            mlaas_redis.set_state(bytes(task_id, "utf-8"), {"state": "pending", "content": None})

            job_thread = threading.Thread(target=background_job_runner, args=(input_task, task_id))
            job_thread.start()

            app.logger.info("/mlaas-api/set-task, task id: {}, duration (s): {}"
                            .format(task_id, get_duration(log_time)))

            return jsonify(task_id)
        except Exception as ex:
            app.logger.exception("/mlaas-api/set-task: failed")
            return jsonify({"error": f"{ex}"})
        
    @app.route("/mlaas-api/get-task/<string:task_id>", strict_slashes=False, methods=["POST"])
    def get_background_job(task_id):
        """
        :param task_id:    string unambiguously identifying a calculation
        """
        log_time = perf_counter()
        try:
            task = mlaas_redis.get_state(bytes(task_id, "utf-8"))

            if task["state"] == "done":
                mlaas_redis.delete_state(bytes(task_id, "utf-8"))
                app.logger.info("/mlaas-api/get-task, job id: {}, duration (s): {}"
                                .format(task_id, get_duration(log_time)))
            return jsonify(task)
        except Exception as ex:
            app.logger.exception("/mlaas-api/get-task: failed")
            return jsonify({"error": f"{ex}"})
        
    def background_job_runner(input_task, task_id):
        try:
            output_task = task_runner(input_task, {})
            mlaas_redis.set_state(bytes(task_id, "utf-8"), {"state": "done", "content": output_task})
        except Exception as ex:
            print(ex)
            app.logger.exception("background_job_runner: failed")
            mlaas_redis.set_state(task_id, {"state": "error"})
            
    return app

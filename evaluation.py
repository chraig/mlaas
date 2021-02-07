from typing import Dict


def run_task(task: Dict, variables: Dict = None) -> Dict:
    if variables is None:
        variables = {}

    task = {
        "id": None,
        "vars": {}, 
        "scripts": [], 
        "tasks": [], 
        **task,
    }

    variables = {
        **variables, 
        **(task["vars"] if "vars" in task and isinstance(task["vars"], dict) else {}),
    }

    scripts = [run_script(s, variables) for s in task["scripts"]] \
        if "scripts" in task and isinstance(task["scripts"], list) \
        else []
    tasks = [run_task(t, variables) for t in task["tasks"]] \
        if "tasks" in task and isinstance(task["tasks"], list) \
        else []
    
    return {
        "id": task["id"],
        "scripts": scripts, 
        "tasks": tasks,
    }


def run_script(script: Dict, variables: Dict = None) -> Dict:
    if variables is None:
        variables = {}

    script = {
        "type": None, 
        "code": None, 
        **script,
    }

    t, c = script["type"], script["code"]
    value, error = None, None

    try:
        if t == "exec":
            value = exec(c, variables)

        elif t == "eval":
            value = eval(c, variables)

    except Exception as ex:
        error = str(ex)

    return {
        "value": value, 
        "error": error,
    }

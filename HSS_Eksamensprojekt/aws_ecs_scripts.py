import subprocess
import json

AWS_ECS_START = ["aws","ecs"]



def run_command(command):
    """ Run a shell command and return its output """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(command)}\n{result.stderr}")
        return False
    else:
        print(f"Command output: {result.stdout}")
        return result.stdout


def list_tasks(cluster_name):

    """
    List tasks in a specific ECS cluster.
    """

    output = run_command(
        ["aws", "ecs", "list-tasks", "--cluster", cluster_name])
    return json.loads(output)

def describe_task(cluster_name,task_arn):

    """
    Describes the tasks in a specific ECS Cluster
    """

    output = run_command(["aws","ecs","describe-tasks","--cluster",cluster_name,"--tasks",task_arn])
    return json.loads(output)
def stop_task(cluster_name, task_arn):

    """
    Stop a specific task in an ECS cluster.
    """
    cmd = AWS_ECS_START + ["stop-task", "--cluster", cluster_name, "--task", task_arn]
    output = run_command(cmd)
    return output


def run_cmd_on_cluster(cluster_name,cmd):
    """
    Just for testing various commands
    """
    output = run_command(["aws","ecs",cmd])
    return output
    #return json.loads(output)



def get_taskdefinitions():

    cmd = AWS_ECS_START + ["list-task-definition-families"]
    output = run_command(cmd)
 
    return json.loads(output)

def get_taskdefinition_families():

    cmd = AWS_ECS_START + ["list-task-definition-families"]
    output = run_command(cmd)
 
    return json.loads(output)

def get_taskdefinition_info(task_definition_name):

    cmd = AWS_ECS_START + ["describe-task-definition","--task-definition",task_definition_name]
    output = run_command(cmd)
 
    return json.loads(output)

def register_new_td(task_def_data):

    task_def_json = json.dumps(task_def_data)
    print(task_def_json)
    cmd = AWS_ECS_START + ["register-task-definition","--cli-input-json", task_def_json]
    output = run_command(cmd)
    return json.loads(output)


def format_td(described_task_def):
    # Convert JSON string to dictionary if it's a string
    if isinstance(described_task_def, str):
        described_task_def = json.loads(described_task_def)

    # Extract task definition data
    task_def_data = described_task_def["taskDefinition"]

    # Create a new dictionary with required fields for registering task definition
    new_task_def = {
        "family": task_def_data["family"],
        "containerDefinitions": task_def_data["containerDefinitions"],
        "requiresCompatibilities": task_def_data["requiresCompatibilities"],
        "cpu": task_def_data["cpu"],
        "memory": task_def_data["memory"]
    }
    """
    # Add optional fields if they exist
    if "volumes" in task_def_data:
        new_task_def["volumes"] = task_def_data["volumes"]
    if "networkMode" in task_def_data:
        new_task_def["networkMode"] = task_def_data["networkMode"]
    if "placementConstraints" in task_def_data:
        new_task_def["placementConstraints"] = task_def_data["placementConstraints"]
    if "executionRoleArn" in task_def_data:
        new_task_def["executionRoleArn"] = task_def_data["executionRoleArn"]
    """

    return new_task_def


def start_task_with_td(cluster_name, td_name):

    cmd = AWS_ECS_START + ["run-task","--cluster",cluster_name,"--task-definition",td_name]
    output = run_command(cmd)
    return json.loads(output)




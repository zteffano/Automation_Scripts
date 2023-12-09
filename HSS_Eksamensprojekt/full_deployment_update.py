import subprocess
import json
import os
from time import sleep
from aws_ecs_scripts import list_tasks,stop_task, start_task_with_td,format_td,register_new_td,get_taskdefinition_info

SOLUTION_DIR = r"C:\Users\z\source\repos\HSS_WEBAPI_MICROSERVICE" # det en raw string, så kan godt tage \
DOCKER_IMAGE_NAME = "hsswebapi_scripted"
DOCKERFILE_RELATIV = "HSS_WEBAPI_MICROSERVICE/Dockerfile"
DOCKERHUB_IMAGE_NAME = "hsswebapi_test" # hvis navnet er anderleds fra lokalt docker image navn
DOCKER_USERNAME = "zteffano"
DOCKER_REPO = f"{DOCKER_USERNAME}/{DOCKERHUB_IMAGE_NAME}:latest"





def run_command(command):
    """ Run a shell command and return its output """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(command)}\n{result.stderr}")
        return False
    else:
        print(f"Command output: {result.stdout}")
        return True

"""
FØRSTE DEL: Docker Build, tag & push til dockerhub - (OBS: brug docker login før script kørsel)
ANDEN DEL: AWS ECS CLI 

"""


def build_webapi_to_dockerhub():

    # Step 1: Projekt mappen med VS Solution til Web API
    project_directory = SOLUTION_DIR
    os.chdir(project_directory)

    # Step 2: Build af vores docker image
    if not run_command(f'docker build -t {DOCKER_IMAGE_NAME} -f {DOCKERFILE_RELATIV} .'):
        return

    # Step 3: Tag af vores image
    if not run_command(f'docker tag {DOCKER_IMAGE_NAME} {DOCKER_REPO}'):
        return

    # Step 4: Docker Login
    if not run_command('docker login'):
        return

    # Step 5: Push af image til dockerhub
    if not run_command(f'docker push {DOCKER_REPO}'):
        return

    print("HSS WebApi Docker Build script færdiggjort")



def deploy_update_on_ecs(cluster_name="hssproject-cluster",td_revision="hss-webapi:5"):
    AWS_ECS_START = ["aws","ecs"]


    tasks = list_tasks(cluster_name)
    webapi_task_id = tasks['taskArns'][0] #da vi pt kun kører en task, kan justeres til ved flere
    td_data = get_taskdefinition_info(td_revision) # henter task def info på hss-webapi:5, så vi kan bruge den til at lave en revision
    formatted_td_data = format_td(td_data) # formattering af vores td data til korrekt format
    new_td = register_new_td(formatted_td_data) # laver en revision af vores hss-webapi td og returnere den fulde td som json
    stop_task(cluster_name,webapi_task_id)
    #check tasken er stoppet:
    sleep(30)
    new_tasks = list_tasks(cluster_name)
    if not new_tasks['taskArns']:
        print("No task - so task must be stopped")
    start_task_with_td(cluster_name,td_revision) # forsøger at starte vores nye revision af td´en
    sleep(30)
    new_tasks = list_tasks(cluster_name)
    
    # her kan evt. komme pytest script ind


    
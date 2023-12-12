import subprocess
import os
import logging
from time import sleep
from aws_ecs_scripts import list_tasks, stop_task, start_task_with_td, format_td, register_new_td, get_taskdefinition_info

"""
FØRSTE DEL: Docker Build, tag & push til dockerhub - (OBS: brug docker login før script kørsel)
ANDEN DEL: AWS ECS CLI 

"""



# Konfiguration af logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Konstanter
SOLUTION_DIR = r"C:\Users\z\Documents\GitHub\HardSkillStation_Eksamensprojekt\backend\WEBAPI_SOLUTION"
DOCKER_IMAGE_NAME = "hsswebapi_scripted"
DOCKERFILE_RELATIV = "HSS_WEBAPI_MICROSERVICE/Dockerfile"
DOCKERHUB_IMAGE_NAME = "hsswebapi_test"
DOCKER_USERNAME = "zteffano"
DOCKER_REPO = f"{DOCKER_USERNAME}/{DOCKERHUB_IMAGE_NAME}:latest"
TEST_DIR = r"C:\Users\z\Documents\GitHub\Automation_Scripts\HSS_Eksamensprojekt\test_files"



def run_command(command):
    """ Kør en shell kommando og returner dens output """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Fejl ved udførelse af kommando: {' '.join(command)}\n{result.stderr}")
        return False
    else:
        logger.info(f"Kommando output: {result.stdout}")
        return True




def build_webapi_to_dockerhub():
    logger.info("Starter bygning og push af Docker image til DockerHub")

    os.chdir(SOLUTION_DIR)
    if not run_command(f'docker build -t {DOCKER_IMAGE_NAME} -f {DOCKERFILE_RELATIV} .'):
        return
    if not run_command(f'docker tag {DOCKER_IMAGE_NAME} {DOCKER_REPO}'):
        return
    if not run_command('docker login'):
        return
    if not run_command(f'docker push {DOCKER_REPO}'):
        return

    logger.info("Bygning og push af Docker image fuldført")



def deploy_update_on_ecs(cluster_name="hssproject-cluster", td_revision="hss-webapi:5"):
    logger.info("Starter udrulning på ECS")
    AWS_ECS_START = ["aws","ecs"]

    logger.info("Henter eksisterende tasks")
    tasks = list_tasks(cluster_name)
    if not tasks['taskArns']:
        logger.info("Ingen tasks kørende - så kan ikke lave en ny revision af task definition")
        return
    webapi_task_id = tasks['taskArns'][0] #da vi pt kun kører en task, kan justeres til ved flere
    logger.info(f"Task id: {webapi_task_id}")
    logger.info("Henter eksisterende task definitioner")
    td_data = get_taskdefinition_info(td_revision) # henter task def info på hss-webapi:5, så vi kan bruge den til at lave en revision
    logger.info("Laver revision af eksisterende task definition")
    formatted_td_data = format_td(td_data) # formattering af vores td data til korrekt format
    logger.info("Registrerer den nye task definition")
    register_new_td(formatted_td_data) # laver en revision af vores hss-webapi td og returnere den fulde td som json
    logger.info("Stopper eksisterende task, så vi kan starte vores nye revision")
    stop_task(cluster_name,webapi_task_id)
    #check tasken er stoppet:
    logger.info("Venter 20 sekunder på at eksisterende task stopper")
    sleep(20)
    new_tasks = list_tasks(cluster_name)
    if not new_tasks['taskArns']:
        logger.info("Ingen tasks kørende - klar til udrulning af ny revision")
        
    else:
        logger.info("Der er stadig tasks kørende - Noget er gået galt")
        return
    logger.info("Starter ny revision af task definition")
    start_task_with_td(cluster_name,td_revision) # forsøger at starte vores nye revision af td´en
    sleep(15)
    logger.info("Venter 15 sekunder på at ny revision starter")
    new_tasks = list_tasks(cluster_name)
    if not new_tasks['taskArns']:
        logger.info("Ingen tasks kørende - Noget er gået galt")
        logger.info("Venter 15 sekunder mere på at ny revision starter")
        sleep(15)
        new_tasks = list_tasks(cluster_name)
        if not new_tasks['taskArns']:
            logger.info("Ingen tasks kørende - Noget er gået galt")
            return
 
    logger.info("Ny revision af task definition er startet")
    logger.info("Udrulning på ECS fuldført")

  

def full_deployment_update():
    logger.info("Starter fuld udrulningsproces")
    build_webapi_to_dockerhub()
    deploy_update_on_ecs()
    logger.info("Fuld udrulningsproces fuldført")
    logger.info("Kører automatisk testing af ny revision")
    os.chdir(TEST_DIR)
    run_command(["pytest", "-v", "--color=yes"])

    # evt. selenium test også her

def only_test():
    print("Running pytest") 
    os.chdir(TEST_DIR)
    run_command(["pytest", "-v", "--color=yes"])
    print("-"*20)


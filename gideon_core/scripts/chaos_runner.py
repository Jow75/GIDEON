import os
import time
import random
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [CHAOS] %(message)s")

CONTAINERS = {
    "redis": "gideon_redis",
    "postgres": "gideon_postgres",
    "node_1": "gideon_core_1",
    "node_2": "gideon_core_2",
    "qdrant": "gideon_qdrant"
}

def docker_cmd(action, container):
    subprocess.run(["docker", action, container], capture_output=True)

def random_fault():
    faults = [
        ("restart", CONTAINERS["redis"], 5),
        ("pause", CONTAINERS["redis"], 10),
        ("kill", CONTAINERS["redis"], 5),
        ("restart", CONTAINERS["postgres"], 15),
        ("restart", CONTAINERS["node_2"], 10),
        ("pause", CONTAINERS["node_2"], 15),
        ("stop", CONTAINERS["qdrant"], 15),
    ]
    action, container, duration = random.choice(faults)
    
    logging.info(f"Injecting fault: {action} on {container} for {duration} seconds...")
    
    if action == "kill":
        docker_cmd("kill", container)
        time.sleep(duration)
        logging.info(f"Restoring: starting {container}...")
        docker_cmd("start", container)
    elif action == "pause":
        docker_cmd("pause", container)
        time.sleep(duration)
        logging.info(f"Restoring: unpausing {container}...")
        docker_cmd("unpause", container)
    elif action == "stop":
        docker_cmd("stop", container)
        time.sleep(duration)
        logging.info(f"Restoring: starting {container}...")
        docker_cmd("start", container)
    elif action == "restart":
        docker_cmd("restart", container)
        # Restart implicitly restores

def split_brain():
    logging.info("Injecting Split-Brain: Pausing Node 2...")
    docker_cmd("pause", CONTAINERS["node_2"])
    time.sleep(30)
    logging.info("Restoring Split-Brain: Unpausing Node 2...")
    docker_cmd("unpause", CONTAINERS["node_2"])

def slow_database():
    logging.info("Injecting Slow Database: Pausing Postgres...")
    docker_cmd("pause", CONTAINERS["postgres"])
    time.sleep(15) # Simulated delay
    logging.info("Restoring Database: Unpausing Postgres...")
    docker_cmd("unpause", CONTAINERS["postgres"])

def clock_skew():
    logging.info("Injecting Clock Skew: We cannot easily modify env vars of a running container without recreate, so we will skip literal env injection in this script and assume it's tested via integration tests or manually.")
    pass

if __name__ == "__main__":
    logging.info("Starting Chaos Runner...")
    try:
        for i in range(15): # Run 15 random fault cycles
            time.sleep(random.randint(10, 20))
            scenario = random.random()
            if scenario < 0.15:
                split_brain()
            elif scenario < 0.30:
                slow_database()
            else:
                random_fault()
    except KeyboardInterrupt:
        logging.info("Chaos Runner stopped.")
    finally:
        logging.info("Restoring all containers to healthy state...")
        for container in CONTAINERS.values():
            docker_cmd("unpause", container)
            docker_cmd("start", container)

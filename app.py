import logging

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from pydantic import BaseModel

# Configure logger to log in a particular file
logging.basicConfig(filename="cron_job_logs.txt", level=logging.INFO)

# Instantiate the schedular
schedular = BackgroundScheduler()


# Instantiate the FastAPI instanve
app = FastAPI()


# Declare pydantic model to serialize and de-serialize payload
class ClientCronSchedular(BaseModel):
    client_id: int
    cron_schedule: int


# In Memory variable to store different clients and their corresponding cron schedule
CLIENT_CRON_MAPPING = dict()


@app.post("/schedule-cron")
def schedule_cron(client_cron: ClientCronSchedular):
    """
    Endpoint to schedule cron jobs for particular client
    """

    # Check if client already exists
    client_already_exists = client_cron.client_id in CLIENT_CRON_MAPPING

    # Update the client cron settings in meory
    CLIENT_CRON_MAPPING[client_cron.client_id] = client_cron.cron_schedule

    # If client already exists then reschedule existing job
    if client_already_exists:
        schedular.reschedule_job(
            f"client_{client_cron.client_id}_cron",
            trigger="interval",
            seconds=client_cron.cron_schedule,
        )

        return {"message": f"Cron for this client {client_cron.client_id} updated!"}

    # If client doesn't already exists then add new job
    schedular.add_job(
        func=log_client,
        trigger="interval",
        seconds=client_cron.cron_schedule,
        id=f"client_{client_cron.client_id}_cron",
        kwargs={"client_id": client_cron.client_id},
    )

    return {"message": f"Cron Scheduled for client {client_cron.client_id}"}


def log_client(client_id: str) -> None:
    logging.info(f"Hello {client_id}")


schedular.start()

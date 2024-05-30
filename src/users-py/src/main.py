from fastapi import FastAPI
from models import User
from repository import init
import routes
import logging
import sys
import uvicorn
import os

app = FastAPI(title="users")

app.include_router(routes.router)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

logger.info("Starting users app")

if __name__ == "__main__":
    print(os.getenv("AWS_REGION"))
    if os.getenv("DDB_ENDPOINT_OVERRIDE"):
        logger.info("DDB endpoint override provided- developing locally")
        if User.exists():
            logger.info("Users Table exists")
        else:
            logger.info("Users Table does not exist")
            User.create_table(billing_mode="PAY_PER_REQUEST")
            logger.info(f"Users Table created:{User.exists()}")
        init()
        
    uvicorn.run(app, host="0.0.0.0", port=80)

    

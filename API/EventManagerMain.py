

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from requests import codes 
from src.event_mgr_logger import logger, config
from src.routes import event_mgr_router


# Create an instance of the FastAPI class
app = FastAPI()

#Include the EventManager Routers to FastpAPI app
app.include_router(event_mgr_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGINS,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

#Report config to log
logger.info(f'Starting Application on http://{config.IP}:{config.PORT}')

@app.exception_handler(ValueError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=codes.unprocessable_entity,
        content={"message": str(exc)},
    )

def main():
    import uvicorn
    #Start Uvicorn Application
    uvicorn.run(app, host=config.IP,
                port=config.PORT)



if __name__ == "__main__":
    main()    



from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    message: str

class EmptyResponse(BaseModel):
    pass
from repositories.request_repository import RequestRepository
from core.dtos import RequestDTO


class RequestService():
    def __init__(self, repo: RequestRepository):
        self.repo = repo

    def create_request(self, request: RequestDTO):
        self.repo.add_request(request)

    def delete_request(self, receivers: str):
        self.repo.delete_request(receivers)

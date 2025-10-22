from bsu.service import BSUService
from bsu.repository import BSURepository
from bsu.bsuclient import BSUClient


def get_service(session):
    repo = BSURepository(session)
    client = BSUClient()
    return BSUService(repo, client)
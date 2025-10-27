from bsu.service import BSUService
from bsu.repository import BSURepository
from bsu.bsuclient import BSUClient


def get_service(session, client: BSUClient = None):
    repo = BSURepository(session)
    return BSUService(repo, client)
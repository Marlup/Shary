from repositories.user_repository import UserRepository
from core.dtos import UserDTO
from typing import List, Tuple


class UserService():
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, username: str, email: str):
        user = UserDTO(username=username, email=email)
        self.repo.add_user(user)

    def delete_users(self, usernames: List[Tuple[str]]):
        if len(usernames) == 1:
            username = usernames[0][0]
            self.repo.delete_user(username)
        else:
            self.repo.delete_users(usernames)

    def get_all_users(self) -> List[Tuple[str]]:
        user_dtos = self.repo.load_users_from_db()
        users_data = [(u.username, u.email, u.date_added) for u in user_dtos]
        
        return users_data

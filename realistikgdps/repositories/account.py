from __future__ import annotations

from typing import Optional

import realistikgdps.state
from realistikgdps.models.account import Account


async def from_db(account_id: int) -> Optional[Account]:
    acc_db = await realistikgdps.state.services.database.fetch_one(
        "SELECT accountID, userName, password, email, mS, frS, cS, "
        "youtubeurl, twitter, twitch FROM accounts WHERE accountID = :account_id",
        {
            "account_id": account_id,
        },
    )

    if acc_db is None:
        return None

    return Account(
        id=acc_db["accountID"],
        name=acc_db["userName"],
        password=acc_db["password"],
        email=acc_db["email"],
        messages_blocked=acc_db["mS"] == 1,
        friend_req_blocked=acc_db["frS"] == 1,
        comment_history_hidden=acc_db["cS"] == 1,
        youtube_name=acc_db["youtubeurl"],
        twitter_name=acc_db["twitter"],
        twitch_name=acc_db["twitch"],
    )


async def into_db(account: Account) -> int:
    return await realistikgdps.state.services.database.execute(
        "INSERT INTO accounts (userName, password, email, mS, frS, cS, "
        "youtubeurl, twitter, twitch) VALUES (:name, :password, :email, :messages_blocked, "
        ":friend_req_blocked, :comment_history_hidden, :youtube_name, :twitter_name, "
        ":twitch_name)",
        {
            "name": account.name,
            "password": account.password,
            "email": account.email,
            "messages_blocked": account.messages_blocked,
            "friend_req_blocked": account.friend_req_blocked,
            "comment_history_hidden": account.comment_history_hidden,
            "youtube_name": account.youtube_name,
            "twitter_name": account.twitter_name,
            "twitch_name": account.twitch_name,
        },
    )


def into_cache(account: Account) -> None:
    realistikgdps.state.repositories.account_repo[account.id] = account


def from_cache(account_id: int) -> Optional[Account]:
    return realistikgdps.state.repositories.account_repo.get(account_id)


async def from_id(account_id: int) -> Optional[Account]:
    """Attempts to fetch an account from multiple sources ordered by speed.

    Args:
        account_id (int): The ID of the account to fetch.

    Returns:
        Optional[Account]: The account if it exists, otherwise None.
    """

    if account := from_cache(account_id):
        return account

    if account := await from_db(account_id):
        into_cache(account)
        return account

    return None

from __future__ import annotations

import base64

from fastapi import Depends
from fastapi import Form

from realistikgdps import logger
from realistikgdps.common import gd_obj
from realistikgdps.constants.errors import ServiceError
from realistikgdps.constants.likes import LikeType
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.models.user import User
from realistikgdps.usecases import user_comments
from realistikgdps.usecases import users
from realistikgdps.usecases.users import authenticate_dependency


async def view_user_info(
    target_id: int = Form(..., alias="targetAccountID"),
    user: User = Depends(authenticate_dependency()),
) -> str:
    target = await users.get_user_perspective(target_id, user)

    if isinstance(target, ServiceError):
        logger.info(
            f"Requested to view info of non-existent account {target_id} "
            f"with error {target!r}.",
        )
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully viewed the profile of {target.user}.")

    return gd_obj.dumps(
        gd_obj.create_profile(target.user, target.friend_status),
    )


async def update_user_info(
    user: User = Depends(authenticate_dependency()),
    stars: int = Form(...),
    demons: int = Form(...),
    display_type: int = Form(..., alias="icon"),
    diamonds: int = Form(...),
    primary_colour: int = Form(..., alias="color1"),
    secondary_colour: int = Form(..., alias="color2"),
    icon: int = Form(..., alias="accIcon"),
    ship: int = Form(..., alias="accShip"),
    ball: int = Form(..., alias="accBall"),
    ufo: int = Form(..., alias="accBird"),
    wave: int = Form(..., alias="accDart"),
    robot: int = Form(..., alias="accRobot"),
    spider: int = Form(..., alias="accSpider"),
    glow: bool = Form(..., alias="accGlow"),
    explosion: int = Form(..., alias="accExplosion"),
    coins: int = Form(...),
    user_coins: int = Form(..., alias="userCoins"),
) -> str:

    res = await users.update_stats(
        user,
        stars=stars,
        demons=demons,
        display_type=display_type,
        diamonds=diamonds,
        primary_colour=primary_colour,
        secondary_colour=secondary_colour,
        icon=icon,
        ship=ship,
        ball=ball,
        ufo=ufo,
        wave=wave,
        robot=robot,
        spider=spider,
        glow=glow,
        explosion=explosion,
        coins=coins,
        user_coins=user_coins,
    )

    if isinstance(res, ServiceError):
        logger.info(f"Failed to update profile of {user} with error {res!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully updated the profile of {user}.")

    return str(user.id)


async def view_user_comments(
    target_id: int = Form(
        ...,
        alias="accountID",
    ),  # does NOT refer to the requester's user ID.
    page: int = Form(..., alias="page"),
) -> str:
    result = await user_comments.get_user(target_id, page)

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to view comments of {target_id} with error {result!r}.",
        )
        return str(GenericResponse.FAIL)

    response = "|".join(
        gd_obj.dumps(gd_obj.create_user_comment(comment), sep="~")
        for comment in result.comment
    )
    response += f"#{result.total}:{page}:10"

    logger.info(f"Successfully viewed comments of {target_id}.")
    return response


async def post_user_comment(
    user: User = Depends(authenticate_dependency()),
    content_b64: str = Form(..., alias="comment"),
) -> str:
    content = base64.urlsafe_b64decode(content_b64.encode()).decode()
    result = await user_comments.create(user, content)

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to post comment on {user}'s profile with error {result!r}.",
        )
        return str(GenericResponse.FAIL)

    logger.info(f"{user} successfully posted a profile comment.")
    return str(GenericResponse.SUCCESS)


# TODO: MOVE
# async def like_target(
#    target_type: LikeType = Form(..., alias="type"),
#    target_id: int = Form(..., alias="itemID"),
#    is_positive: bool = Form(..., alias="like"),
# ) -> str:
#
#    if target_type is LikeType.USER_COMMENT:
#        result = await user_comments.like(user, is_positive)


async def update_settings(
    user: User = Depends(authenticate_dependency()),
    youtube_name: str = Form(..., alias="yt"),
    twitter_name: str = Form(..., alias="twitter"),
    twitch_name: str = Form(..., alias="twitch"),
) -> str:
    result = await users.update_stats(
        user,
        youtube_name=youtube_name,
        twitter_name=twitter_name,
        twitch_name=twitch_name,
    )

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to update settings of {user} with error {result!r}.",
        )
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully updated settings of {user}.")
    return str(GenericResponse.SUCCESS)

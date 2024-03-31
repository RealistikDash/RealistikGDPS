from __future__ import annotations

from rgdps.common import modelling
from rgdps.common.context import Context
from rgdps.constants.likes import LikeType
from rgdps.models.like import Like

ALL_FIELDS = modelling.get_model_fields(Like)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


async def from_id(ctx: Context, id: int) -> Like | None:
    like_db = await ctx.mysql.fetch_one(
        f"SELECT {_CUSTOMISABLE_FIELDS_COMMA} FROM user_likes WHERE id = :id",
        {
            "id": id,
        },
    )

    if like_db is None:
        return None

    return Like.from_mapping(like_db)


async def create(
    ctx: Context,
    target_type: LikeType,
    target_id: int,
    user_id: int,
    value: int,
    like_id: int = 0,
) -> Like:
    like = Like(
        id=like_id,
        target_type=target_type,
        target_id=target_id,
        user_id=user_id,
        value=value,
    )
    like.id = await ctx.mysql.execute(
        f"INSERT INTO user_likes ({_ALL_FIELDS_COMMA}) VALUES "
        f"({_ALL_FIELDS_COLON})",
        like.as_dict(include_id=True),
    )

    return like


async def exists_by_target_and_user(
    ctx: Context,
    target_type: LikeType,
    target_id: int,
    user_id: int,
) -> bool:
    return (
        await ctx.mysql.fetch_one(
            "SELECT id FROM user_likes WHERE target_type = :target_type AND target_id = :target_id AND user_id = :user_id",
            {
                "target_type": target_type.value,
                "target_id": target_id,
                "user_id": user_id,
            },
        )
        is not None
    )


async def sum_by_target(
    ctx: Context,
    target_type: LikeType,
    target_id: int,
) -> int:
    like_db = await ctx.mysql.fetch_val(
        "SELECT SUM(value) AS sum FROM user_likes WHERE target_type = :target_type "
        "AND target_id = :target_id",
        {
            "target_type": target_type.value,
            "target_id": target_id,
        },
    )

    if like_db is None:
        return 0

    return int(like_db)


async def update_value(
    ctx: Context,
    like_id: int,
    value: int,
) -> None:
    await ctx.mysql.execute(
        "UPDATE likes SET value = :value WHERE id = :id",
        {
            "id": like_id,
            "value": value,
        },
    )

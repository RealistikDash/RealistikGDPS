from __future__ import annotations

from datetime import datetime
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from rgdps.common import modelling
from rgdps.common.context import Context
from rgdps.constants.users import UserRelationshipType
from rgdps.models.user_relationship import UserRelationship

ALL_FIELDS = modelling.get_model_fields(UserRelationship)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


async def from_id(
    ctx: Context,
    relationship_id: int,
    include_deleted: bool = False,
) -> UserRelationship | None:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    relationship_db = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM user_relationships WHERE id = :relationship_id {condition}",
        {"relationship_id": relationship_id},
    )

    if not relationship_db:
        return None

    return UserRelationship.from_mapping(relationship_db)


async def from_user_id(
    ctx: Context,
    user_id: int,
    relationship_type: UserRelationshipType,
    include_deleted: bool = False,
) -> list[UserRelationship]:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    relationships_db = await ctx.mysql.fetch_all(
        f"SELECT {_ALL_FIELDS_COMMA} FROM user_relationships WHERE user_id = :user_id AND "
        f"relationship_type = :relationship_type {condition} "
        "ORDER BY post_ts DESC",
        {"user_id": user_id, "relationship_type": relationship_type.value},
    )

    return [
        UserRelationship.from_mapping(relationship_db)
        for relationship_db in relationships_db
    ]


async def from_user_id_paginated(
    ctx: Context,
    user_id: int,
    relationship_type: UserRelationshipType,
    page: int,
    page_size: int,
    include_deleted: bool = False,
) -> list[UserRelationship]:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    relationships_db = await ctx.mysql.fetch_all(
        f"SELECT {_ALL_FIELDS_COMMA} FROM user_relationships WHERE user_id = :user_id AND "
        f"relationship_type = :relationship_type {condition} "
        "ORDER BY post_ts DESC LIMIT :limit OFFSET :offset",
        {
            "user_id": user_id,
            "relationship_type": relationship_type.value,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [
        UserRelationship.from_mapping(relationship_db)
        for relationship_db in relationships_db
    ]


async def from_user_and_target_user(
    ctx: Context,
    user_id: int,
    target_user_id: int,
    relationship_type: UserRelationshipType,
    include_deleted: bool = False,
) -> UserRelationship | None:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    relationship_db = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM user_relationships WHERE user_id = :user_id AND target_user_id = :target_user_id "
        f"AND relationship_type = :relationship_type {condition}",
        {
            "user_id": user_id,
            "target_user_id": target_user_id,
            "relationship_type": relationship_type.value,
        },
    )

    if not relationship_db:
        return None

    return UserRelationship.from_mapping(relationship_db)


async def get_user_relationship_count(
    ctx: Context,
    user_id: int,
    relationship_type: UserRelationshipType,
    is_new: bool = False,
    include_deleted: bool = False,
) -> int:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    if is_new:
        condition += " AND seen_ts IS NULL"

    return await ctx.mysql.fetch_val(
        "SELECT COUNT(*) FROM user_relationships WHERE user_id = :user_id "
        f"AND relationship_type = :relationship_type {condition}",
        {"user_id": user_id, "relationship_type": relationship_type.value},
    )


async def check_relationship_exists(
    ctx: Context,
    user_id: int,
    target_user_id: int,
    relationship_type: UserRelationshipType,
    include_deleted: bool = False,
) -> bool:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    return await ctx.mysql.fetch_val(
        "SELECT EXISTS(SELECT 1 FROM user_relationships WHERE user_id = :user_id "
        f"AND target_user_id = :target_user_id AND relationship_type = :relationship_type {condition})",
        {
            "user_id": user_id,
            "target_user_id": target_user_id,
            "relationship_type": relationship_type.value,
        },
    )


async def mark_all_as_seen(
    ctx: Context,
    user_id: int,
    relationship_type: UserRelationshipType,
    seen_ts: datetime,
    include_deleted: bool = False,
) -> None:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    await ctx.mysql.execute(
        "UPDATE user_relationships SET seen_ts = :seen_ts WHERE user_id = :user_id "
        f"AND relationship_type = :relationship_type AND seen_ts IS NULL {condition}",
        {
            "seen_ts": seen_ts,
            "user_id": user_id,
            "relationship_type": relationship_type.value,
        },
    )


async def create(
    ctx: Context,
    user_id: int,
    target_user_id: int,
    relationship_type: UserRelationshipType,
    post_ts: datetime = datetime.now(),
    seen_ts: None | datetime = None,
) -> UserRelationship:
    relationship = UserRelationship(
        id=0,
        relationship_type=relationship_type,
        user_id=user_id,
        target_user_id=target_user_id,
        post_ts=post_ts,
        seen_ts=seen_ts,
    )

    relationship.id = await ctx.mysql.execute(
        f"INSERT INTO user_relationships ({_CUSTOMISABLE_FIELDS_COMMA}) "
        f"VALUES ({_CUSTOMISABLE_FIELDS_COLON})",
        relationship.as_dict(include_id=False),
    )

    return relationship


class _UserRelationshipUpdatePartial(TypedDict):
    seen_ts: NotRequired[datetime]
    deleted: NotRequired[bool]


async def update_partial(
    ctx: Context,
    relationship_id: int,
    **kwargs: Unpack[_UserRelationshipUpdatePartial],
) -> UserRelationship | None:
    changed_fields = modelling.unpack_enum_types(kwargs)

    await ctx.mysql.execute(
        modelling.update_from_partial_dict(
            "user_relationships",
            relationship_id,
            changed_fields,
        ),
        changed_fields,
    )

    return await from_id(ctx, relationship_id, include_deleted=True)


async def get_count(ctx: Context) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM user_relationships")

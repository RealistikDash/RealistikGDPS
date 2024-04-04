# NOTE: These serve more as logs than anything else. Aside from the latest
# claimed timestamp, logging these has no impact on the game. Therefore,
# editing these is not necessary.
from __future__ import annotations

from datetime import datetime

from rgdps.common import modelling
from rgdps.common.context import Context
from rgdps.constants.daily_chests import DailyChestType
from rgdps.models.daily_chest import DailyChest

ALL_FIELDS = modelling.get_model_fields(DailyChest)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


async def from_id(
    ctx: Context,
    chest_id: int,
) -> DailyChest | None:
    chest_db = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM daily_chests WHERE id = :chest_id",
        {"chest_id": chest_id},
    )

    if chest_db is None:
        return None

    return DailyChest.from_mapping(chest_db)


async def from_user_id_and_type_latest(
    ctx: Context,
    user_id: int,
    chest_type: DailyChestType,
) -> DailyChest | None:
    chest_db = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM daily_chests WHERE user_id = :user_id AND type = :chest_type "
        "ORDER BY claimed_ts DESC LIMIT 1",
        {"user_id": user_id, "chest_type": chest_type.value},
    )

    if chest_db is None:
        return None

    return DailyChest.from_mapping(chest_db)


async def create(
    ctx: Context,
    user_id: int,
    chest_type: DailyChestType,
    mana: int = 0,
    diamonds: int = 0,
    fire_shards: int = 0,
    ice_shards: int = 0,
    poison_shards: int = 0,
    shadow_shards: int = 0,
    lava_shards: int = 0,
    demon_keys: int = 0,
    claimed_ts: datetime | None = None,
) -> DailyChest:
    if claimed_ts is None:
        claimed_ts = datetime.now()

    chest = DailyChest(
        id=0,
        user_id=user_id,
        type=chest_type,
        mana=mana,
        diamonds=diamonds,
        fire_shards=fire_shards,
        ice_shards=ice_shards,
        poison_shards=poison_shards,
        shadow_shards=shadow_shards,
        lava_shards=lava_shards,
        demon_keys=demon_keys,
        claimed_ts=claimed_ts,
    )

    chest.id = await ctx.mysql.execute(
        f"INSERT INTO daily_chests ({_CUSTOMISABLE_FIELDS_COMMA}) "
        f"VALUES ({_CUSTOMISABLE_FIELDS_COLON})",
        chest.as_dict(include_id=False),
    )

    return chest


async def sum_reward_mana(
    ctx: Context,
    user_id: int,
) -> int:
    return int(
        await ctx.mysql.fetch_val(
            "SELECT SUM(mana) FROM daily_chests WHERE user_id = :user_id",
            {"user_id": user_id},
        )
        or 0,
    )


async def count_of_type(
    ctx: Context,
    user_id: int,
    chest_type: DailyChestType,
) -> int:
    return (
        await ctx.mysql.fetch_val(
            "SELECT COUNT(*) FROM daily_chests WHERE user_id = :user_id AND type = :chest_type",
            {"user_id": user_id, "chest_type": chest_type.value},
        )
        or 0
    )

from __future__ import annotations

from datetime import datetime
from enum import Enum
from enum import IntEnum
from enum import IntFlag
from typing import Any
from typing import TypedDict
from typing import NotRequired
from typing import Unpack
from typing import Literal
from typing import NamedTuple
from typing import AsyncGenerator

from ognisko.adapters import AbstractMySQLService
from ognisko.adapters import MeiliSearchClient
from ognisko.resources._common import DatabaseModel
from ognisko.common import modelling
from ognisko.common import data_utils
from ognisko.utilities import time as time_utils


class LevelSearchFlag(IntFlag):
    NONE = 0
    EPIC = 1 << 0
    AWARDED = 1 << 1
    MAGIC = 1 << 2
    LEGENDARY = 1 << 3
    MYTHICAL = 1 << 4

    def as_feature(self) -> LevelFeature:
        if self & LevelSearchFlag.MYTHICAL:
            return LevelFeature.MYTHICAL

        if self & LevelSearchFlag.LEGENDARY:
            return LevelFeature.LEGENDARY

        if self & LevelSearchFlag.EPIC:
            return LevelFeature.EPIC

        return LevelFeature.NONE


class LevelFeature(IntEnum):
    NONE = 0
    FEATURE = 1
    EPIC = 2
    LEGENDARY = 3
    MYTHICAL = 4

    def as_search_flag(self) -> LevelSearchFlag:
        return _LEVEL_FEATURE_MAP[self]


_LEVEL_FEATURE_MAP = {
    LevelFeature.NONE: LevelSearchFlag.NONE,
    LevelFeature.FEATURE: LevelSearchFlag.NONE,
    LevelFeature.EPIC: LevelSearchFlag.EPIC,
    LevelFeature.LEGENDARY: LevelSearchFlag.EPIC | LevelSearchFlag.LEGENDARY,
    LevelFeature.MYTHICAL: LevelSearchFlag.EPIC
    | LevelSearchFlag.LEGENDARY
    | LevelSearchFlag.MYTHICAL,
}


class LevelDifficulty(IntEnum):
    NA = 0
    EASY = 10
    NORMAL = 20
    HARD = 30
    HARDER = 40
    INSANE = 50

    @staticmethod
    def from_stars(stars: int) -> LevelDifficulty:
        return _DIFFICULTY_STAR_MAP.get(
            stars,
            LevelDifficulty.NA,
        )


_DIFFICULTY_STAR_MAP = {
    2: LevelDifficulty.EASY,
    3: LevelDifficulty.NORMAL,
    4: LevelDifficulty.HARD,
    5: LevelDifficulty.HARD,
    6: LevelDifficulty.HARDER,
    7: LevelDifficulty.HARDER,
    8: LevelDifficulty.INSANE,
    9: LevelDifficulty.INSANE,
}


class LevelDifficultyName(Enum):
    """A string equivalent of `LevelDifficulty` enum used for validation."""

    NA = "na"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    HARDER = "harder"
    INSANE = "insane"

    def as_difficulty(self) -> LevelDifficulty:
        return _NAME_DIFFICULTY_MAP[self]


_NAME_DIFFICULTY_MAP = {
    LevelDifficultyName.NA: LevelDifficulty.NA,
    LevelDifficultyName.EASY: LevelDifficulty.EASY,
    LevelDifficultyName.NORMAL: LevelDifficulty.NORMAL,
    LevelDifficultyName.HARD: LevelDifficulty.HARD,
    LevelDifficultyName.HARDER: LevelDifficulty.HARDER,
    LevelDifficultyName.INSANE: LevelDifficulty.INSANE,
}


class LevelLength(IntEnum):
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4
    PLATFORMER = 5


class LevelDemonDifficulty(IntEnum):
    HARD = 0
    EASY = 3
    MEDIUM = 4
    INSANE = 5
    EXTREME = 6


class LevelDemonRating(IntEnum):
    """Demon difficulty rating used by the client to send demon ratings
    (but not receive)."""

    EASY = 1
    MEDIUM = 2
    HARD = 3
    INSANE = 4
    EXTREME = 5

    def as_difficulty(self) -> LevelDemonDifficulty:
        return _RATING_DIFFICULTY_MAP[self]


_RATING_DIFFICULTY_MAP = {
    LevelDemonRating.EASY: LevelDemonDifficulty.EASY,
    LevelDemonRating.MEDIUM: LevelDemonDifficulty.MEDIUM,
    LevelDemonRating.HARD: LevelDemonDifficulty.HARD,
    LevelDemonRating.INSANE: LevelDemonDifficulty.INSANE,
    LevelDemonRating.EXTREME: LevelDemonDifficulty.EXTREME,
}


# Ideas:
# Listed only for friends
class LevelPublicity(IntEnum):
    PUBLIC = 0
    # Levels only accessible through direct ID.
    GLOBAL_UNLISTED = 1
    FRIENDS_UNLISTED = 2


class LevelSearchType(IntEnum):
    SEARCH_QUERY = 0
    MOST_DOWNLOADED = 1
    MOST_LIKED = 2
    TRENDING = 3
    RECENT = 4
    USER_LEVELS = 5
    FEATURED = 6
    MAGIC = 7
    MODERATOR_SENT = 8
    LEVEL_LIST = 9
    AWARDED = 11
    FOLLOWED = 12
    FRIENDS = 13
    EPIC = 16
    DAILY = 21
    WEEKLY = 22

class Level(DatabaseModel):
    id: int
    name: str
    user_id: int
    description: str
    custom_song_id: int | None
    official_song_id: int | None
    version: int
    length: LevelLength
    two_player: bool
    publicity: LevelPublicity
    render_str: str  # Officially called extra string
    game_version: int
    binary_version: int
    upload_ts: datetime
    update_ts: datetime
    original_id: int | None

    # Statistics
    downloads: int
    likes: int
    stars: int
    difficulty: LevelDifficulty
    demon_difficulty: LevelDemonDifficulty | None
    coins: int
    coins_verified: bool
    requested_stars: int
    feature_order: int
    search_flags: LevelSearchFlag
    low_detail_mode: bool
    object_count: int
    building_time: int
    update_locked: bool
    song_ids: list[int]
    sfx_ids: list[int]
    deleted: bool

class _LevelUpdatePartial(TypedDict):
    name: NotRequired[str]
    user_id: NotRequired[int]
    description: NotRequired[str]
    custom_song_id: NotRequired[int | None]
    official_song_id: NotRequired[int | None]
    version: NotRequired[int]
    length: NotRequired[LevelLength]
    two_player: NotRequired[bool]
    publicity: NotRequired[LevelPublicity]
    render_str: NotRequired[str]
    game_version: NotRequired[int]
    binary_version: NotRequired[int]
    upload_ts: NotRequired[datetime]
    update_ts: NotRequired[datetime]
    original_id: NotRequired[int | None]
    downloads: NotRequired[int]
    likes: NotRequired[int]
    stars: NotRequired[int]
    difficulty: NotRequired[LevelDifficulty]
    demon_difficulty: NotRequired[LevelDemonDifficulty | None]
    coins: NotRequired[int]
    coins_verified: NotRequired[bool]
    requested_stars: NotRequired[int]
    feature_order: NotRequired[int]
    search_flags: NotRequired[LevelSearchFlag]
    low_detail_mode: NotRequired[bool]
    object_count: NotRequired[int]
    building_time: NotRequired[int]
    update_locked: NotRequired[bool]
    song_ids: NotRequired[list[int]]
    sfx_ids: NotRequired[list[int]]
    deleted: NotRequired[bool]


ALL_FIELDS = modelling.get_model_fields(Level)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)

def _make_meili_dict(level_dict: dict[str, Any]) -> dict[str, Any]:
    level_dict = level_dict.copy()
    if "upload_ts" in level_dict:
        level_dict["upload_ts"] = time_utils.into_unix_ts(level_dict["upload_ts"])

    if "update_ts" in level_dict:
        level_dict["update_ts"] = time_utils.into_unix_ts(level_dict["update_ts"])

    # Split up bitwise enums as meili does not support bitwise operations.
    if "search_flags" in level_dict:
        level_dict["epic"] = bool(level_dict["search_flags"] & LevelSearchFlag.EPIC)
        level_dict["magic"] = bool(level_dict["search_flags"] & LevelSearchFlag.MAGIC)
        level_dict["awarded"] = bool(
            level_dict["search_flags"] & LevelSearchFlag.AWARDED,
        )
        level_dict["legendary"] = bool(
            level_dict["search_flags"] & LevelSearchFlag.LEGENDARY,
        )
        level_dict["mythical"] = bool(
            level_dict["search_flags"] & LevelSearchFlag.MYTHICAL,
        )

    return level_dict


def _from_meili_dict(level_dict: dict[str, Any]) -> dict[str, Any]:
    level_dict = level_dict.copy()
    # Meili returns unix timestamps, so we need to convert them back to datetime.
    level_dict["upload_ts"] = time_utils.from_unix_ts(level_dict["upload_ts"])
    level_dict["update_ts"] = time_utils.from_unix_ts(level_dict["update_ts"])

    search_flags = LevelSearchFlag.NONE

    if level_dict["epic"]:
        search_flags |= LevelSearchFlag.EPIC

    if level_dict["magic"]:
        search_flags |= LevelSearchFlag.MAGIC

    if level_dict["awarded"]:
        search_flags |= LevelSearchFlag.AWARDED

    if level_dict["legendary"]:
        search_flags |= LevelSearchFlag.LEGENDARY

    if level_dict["mythical"]:
        search_flags |= LevelSearchFlag.MYTHICAL

    level_dict["search_flags"] = search_flags

    del level_dict["epic"]
    del level_dict["magic"]
    del level_dict["awarded"]
    del level_dict["legendary"]
    del level_dict["mythical"]

    # FIXME: Temporary migration measure.
    if "song_ids" not in level_dict:
        level_dict["song_ids"] = [level_dict["custom_song_id"]]
        level_dict["sfx_ids"] = []

    return level_dict


class LevelSearchResults(NamedTuple):
    results: list[Level]
    total: int

class LevelRepository:
    __slots__ = (
        "_mysql",
        "_meili",
    )

    def __init__(self, mysql: AbstractMySQLService, meili: MeiliSearchClient) -> None:
        self._mysql = mysql
        self._meili = meili.index("levels")
    
    async def create(
            self,
            name: str,
            user_id: int,
            description: str = "",
            custom_song_id: int | None = None,
            official_song_id: int | None = 1,
            version: int = 1,
            length: LevelLength = LevelLength.TINY,
            two_player: bool = False,
            publicity: LevelPublicity = LevelPublicity.PUBLIC,
            render_str: str = "",
            game_version: int = 22,
            binary_version: int = 34,
            upload_ts: datetime | None = None,
            update_ts: datetime | None = None,
            original_id: int | None = None,
            downloads: int = 0,
            likes: int = 0,
            stars: int = 0,
            difficulty: LevelDifficulty = LevelDifficulty.NA,
            demon_difficulty: LevelDemonDifficulty | None = None,
            coins: int = 0,
            coins_verified: bool = False,
            requested_stars: int = 0,
            feature_order: int = 0,
            search_flags: LevelSearchFlag = LevelSearchFlag.NONE,
            low_detail_mode: bool = False,
            object_count: int = 0,
            building_time: int = 0,
            update_locked: bool = False,
            song_ids: list[int] | None = None,
            sfx_ids: list[int] | None = None,
            deleted: bool = False,
            level_id: int | None = None,
    ) -> Level:
        if upload_ts is None:
            upload_ts = datetime.now()
        if update_ts is None:
            update_ts = datetime.now()

        if sfx_ids is None:
            sfx_ids = []
        if song_ids is None:
            song_ids = []

        level = Level(
            id=0,
            name=name,
            user_id=user_id,
            description=description,
            custom_song_id=custom_song_id,
            official_song_id=official_song_id,
            version=version,
            length=length,
            two_player=two_player,
            publicity=publicity,
            render_str=render_str,
            game_version=game_version,
            binary_version=binary_version,
            upload_ts=upload_ts,
            update_ts=update_ts,
            original_id=original_id,
            downloads=downloads,
            likes=likes,
            stars=stars,
            difficulty=difficulty,
            demon_difficulty=demon_difficulty,
            coins=coins,
            coins_verified=coins_verified,
            requested_stars=requested_stars,
            feature_order=feature_order,
            search_flags=search_flags,
            low_detail_mode=low_detail_mode,
            object_count=object_count,
            building_time=building_time,
            update_locked=update_locked,
            deleted=deleted,
            song_ids=song_ids,
            sfx_ids=sfx_ids,
        )
        level_dump = level.model_dump()
        level_dump["id"] = level_id

        level.id = await self._mysql.execute(
            f"INSERT INTO levels ({_ALL_FIELDS_COMMA}) VALUES ({_ALL_FIELDS_COLON})",
            level_dump,
        )

        meili_dict = _make_meili_dict(level.model_dump())
        await self._meili.add_documents([meili_dict])
        return level
    

    async def from_id(self, level_id: int) -> Level | None:
        level_dict = await self._mysql.fetch_one(
            f"SELECT {_ALL_FIELDS_COMMA} FROM levels WHERE id = :level_id",
            {"level_id": level_id},
        )

        if not level_dict:
            return None

        return Level(**level_dict)
    

    async def multiple_from_id(self, level_ids: list[int]) -> list[Level]:
        if not level_ids:
            return []

        levels = await self._mysql.fetch_all(
            f"SELECT {_ALL_FIELDS_COMMA} FROM levels WHERE id IN :level_ids",
            {"level_ids": tuple(level_ids)},
        )
        levels = sorted(levels, key=lambda level: level_ids.index(level["id"]))

        return [Level(**level) for level in levels]
    
    async def update_partial(
            self,
            level_id: int,
            **kwargs: Unpack[_LevelUpdatePartial],
    ) -> Level | None:
        changed_fields = modelling.unpack_enum_types(kwargs)
        changed_rows = await self._mysql.execute(
            modelling.update_from_partial_dict("levels", level_id, changed_fields),
            changed_fields,
        )

        if not changed_rows:
            return None
        
        changed_fields["id"] = level_id
        changed_fields = _make_meili_dict(changed_fields)
        await self._meili.update_documents([changed_fields])

        return await self.from_id(level_id)
    

    async def search(
            self,
            query: str | None = None,
            *,
            page: int = 0,
            page_size: int = 10,
            required_lengths: list[LevelLength] | None = None,
            required_difficulties: list[LevelDifficulty] | None = None,
            required_demon_difficulties: list[LevelDemonDifficulty] | None = None,
            song_id: int | None = None,
            custom_song_id: int | None = None,
            rated_only: bool | None = None,
            two_player_only: bool | None = None,
            excluded_user_ids: list[int] | None = None,
            required_user_ids: list[int] | None = None,
            required_level_ids: list[int] | None = None,
            excluded_level_ids: list[int] | None = None,
            order_by: Literal["downloads", "likes", "stars"] = "downloads",
    )-> LevelSearchResults:
        sort = []
        filters = [
            "deleted = 0",
            # TODO: More unlisted logic, such as friends only.
            f"publicity = {LevelPublicity.PUBLIC.value}"
        ]

        if required_lengths is not None:
            required_lengths = data_utils.enum_int_list(required_lengths) # type: ignore
            filters.append(f"length IN {required_lengths}")

        if required_difficulties is not None:
            required_difficulties = data_utils.enum_int_list(required_difficulties) # type: ignore
            filters.append(f"difficulty IN {required_difficulties}")

        if required_demon_difficulties is not None:
            required_demon_difficulties = data_utils.enum_int_list(required_demon_difficulties) # type: ignore
            filters.append(f"demon_difficulty IN {required_demon_difficulties}")

        # FIXME: THIS IS OBV SO WRONG IHREGIUEHRGIUERH
        if song_id is not None:
            filters.append(f"{song_id} = ANY(song_ids)")

        if custom_song_id is not None:
            filters.append(f"{custom_song_id} = ANY(song_ids)")

        if rated_only is not None:
            if rated_only:
                filters.append("stars > 0")
            else:
                filters.append("stars = 0")

        if two_player_only is not None:
            filters.append(f"two_player = {int(two_player_only)}")
        
        if excluded_user_ids is not None:
            filters.append(f"user_id NOT IN {excluded_user_ids}")

        elif required_user_ids is not None:
            filters.append(f"user_id IN {required_user_ids}")

        if required_level_ids is not None:
            filters.append(f"id IN {required_level_ids}")

        elif excluded_level_ids is not None:
            filters.append(f"id NOT IN {excluded_level_ids}")

        sort.append(f"{order_by} DESC")

        levels_res = await self._meili.search(
            query,
            offset=page * page_size,
            limit=page_size,
            filter=" AND ".join(filters), # ???
            sort=sort,
        )

        levels = [Level(**_from_meili_dict(level)) for level in levels_res.hits]
        return LevelSearchResults(results=levels, total=levels_res.estimated_total_hits or 0)
    
    async def iterate_all(
            self,
            *,
            include_deleted: bool = False,
    ) -> AsyncGenerator[Level, None]:
        condition = ""
        if not include_deleted:
            condition = "WHERE deleted = 0"

        async for level_dict in self._mysql.iterate(
            f"SELECT * FROM levels {condition}",
        ):
            yield Level(**level_dict)


    async def count_all(self) -> int:
        return await self._mysql.fetch_val("SELECT COUNT(*) FROM levels")
    
    async def from_name_and_user_id(
            self,
            name: str,
            user_id: int,
            *,
            include_deleted: bool = False,
        ) -> Level | None:
        level_dict = await self._mysql.fetch_one(
            "SELECT * FROM levels WHERE name = :name AND user_id = :user_id"
            " AND deleted = 0" if not include_deleted else "",
            {"name": name, "user_id": user_id},
        )

        if not level_dict:
            return None

        return Level(**level_dict)
    

    async def from_name(
            self,
            name: str,
            *,
            include_deleted: bool = False,
        ) -> Level | None:
        levels = await self._mysql.fetch_one(
            "SELECT * FROM levels WHERE name = :name"
            " AND deleted = 0" if not include_deleted else ""
            " LIMIT 1",
            {"name": name},
        )

        if not levels:
            return None
        
        return Level(**levels)
    

    # TODO: Move LOL
    # A function primarily used for some recommendation algorithms that returns a list of levels
    # ordered by how well received they are, assessed using a formula..
    async def get_well_received(
        self,
        minimum_stars: int,
        minimum_length: LevelLength,
        maximum_stars: int = 0,
        maximum_demon_rating: LevelDemonDifficulty = LevelDemonDifficulty.EXTREME,
        excluded_level_ids: list[
            int
        ] = [],  # The list isnt mutable, so we can set it to an empty list.
        limit: int = 100,
    ) -> list[int]:
        # BOTCH! Avoiding a sql syntax error.
        if not excluded_level_ids:
            excluded_level_ids = [0]

        # The formula in the order clause is made to emphasis lower downloads, but still have a
        # significant impact on likes.
        values = await self._mysql.fetch_all(
            "SELECT id FROM levels WHERE stars >= :minimum_stars AND stars <= :maximum_stars "
            "AND demon_difficulty <= :maximum_demon_rating AND length >= :minimum_length "
            "AND id NOT IN :excluded_level_ids AND deleted = 0 ORDER BY (SQRT(downloads) / likes) DESC "
            "LIMIT :limit",
            {
                "minimum_stars": minimum_stars,
                "maximum_stars": maximum_stars,
                "maximum_demon_rating": maximum_demon_rating.value,
                "minimum_length": minimum_length.value,
                "excluded_level_ids": tuple(excluded_level_ids),
                "limit": limit,
            },
        )

        return [x["id"] for x in values]
        
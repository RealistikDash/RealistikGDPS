from __future__ import annotations

from typing import NamedTuple
from typing import TypedDict

from sqlalchemy import Base
from sqlalchemy import Column
from sqlalchemy import Integer


class DatabaseModel(Base):
    """The base model for all SQLAlchemy models in Ognisko."""

    id = Column(Integer, primary_key=True, autoincrement=True)


"""
class BaseRepository[
    Model: DatabaseModel,
    PartialUpdate: PartialUpdateBase,
    CreateModel: DatabaseModel = Model,
    UpdateModel: DatabaseModel = Model,
]:
    __slots__ = (
        "_session",
    )

    def __init__(self, session: ImplementsMySQL) -> None:
        self._session = session


    @property
    @cached(cache={})
    def __innter_type(self) -> type[Model]:

        annotated = get_args(self)
        return annotated[0]


    async def from_id(self, id: int) -> Model | None:
        return await self._session.get(self.__innter_type, id)


    async def create(self, model: CreateModel) -> Model:
        new_model = self.__innter_type(**model.model_dump())
        self._session.add(new_model)

        return await self.from_id(new_model.id) # type: ignore


    async def update(self, id: int, **kwargs: Unpack[PartialUpdate]) -> Model:
        model = await self.from_id(id)

        for key, value in kwargs.items():
            setattr(model, key, value)


        await self._session.

        return model

"""


class SearchResults[T](NamedTuple):
    results: list[T]
    total: int
    page_size: int

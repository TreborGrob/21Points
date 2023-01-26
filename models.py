import logging
from sqlalchemy import Column, ForeignKey, Integer, Boolean, BIGINT, VARCHAR, create_engine
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)
Base = declarative_base()
engine = create_engine("sqlite:///points.db")


class Games(Base):
    __tablename__ = 'games'
    __tableargs__ = {
        'comment': 'Игры'
    }

    id_game = Column(
        BIGINT,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    id_tg_player_one = Column(BIGINT, ForeignKey('players.id_telegram'), comment='Игрок 1')
    id_tg_player_two = Column(BIGINT, ForeignKey('players.id_telegram'), comment='Игрок 2')
    status = Column(Boolean, comment='Статус игры')
    result = Column(VARCHAR(10), comment='Результат игры')
    score_one = Column(Integer, comment='Счёт 1 игрока')
    score_two = Column(Integer, comment='Счёт 2 игрока')
    move_one = Column(Boolean, comment='Ход 1 игрока')
    move_two = Column(Boolean, comment='Ход 2 игрока')

    def __repr__(self):
        return f'{self.id_game} {self.id_tg_player_one} {self.id_tg_player_two} {self.status} {self.result} ' \
               f'{self.score_one} {self.score_two} {self.move_one} {self.move_two}'


class Players(Base):
    __tablename__ = 'players'
    __tableargs__ = {
        'comment': 'Игроки'
    }
    id_telegram = Column(
        BIGINT,
        primary_key=True,
        unique=True)
    nickname = Column(VARCHAR(100))
    games = Column(BIGINT)
    wins = Column(BIGINT)
    loses = Column(BIGINT)
    draws = Column(BIGINT)

    def __repr__(self):
        return f'{self.id_telegram} {self.nickname} {self.games} {self.wins} {self.loses} {self.draws}'


class Rating(Base):
    __tablename__ = 'rating'
    __tableargs__ = {
        'comment': 'Рейтинги'
    }

    id_telegram = Column(
        BIGINT,
        ForeignKey('players.id_telegram'),
        primary_key=True,
        unique=True)
    games_rating = Column(BIGINT)
    wins_rating = Column(BIGINT)
    loses_rating = Column(BIGINT)
    draws_rating = Column(BIGINT)
    rate = Column(BIGINT)
    desire = Column(Boolean)
    nickname = Column(VARCHAR(50))

    def __repr__(self):
        return f'{self.id_telegram} {self.games_rating} {self.wins_rating} {self.loses_rating} {self.rate}'


if __name__ == '__main__':
    Base.metadata.create_all(engine)

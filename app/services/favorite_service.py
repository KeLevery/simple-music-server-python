from datetime import datetime
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import MessageConstant
from app.core.response import Result, PageResult
from app.db.models.user_favorite import UserFavorite
from app.db.models.song import Song
from app.db.models.artist import Artist
from app.db.models.playlist import Playlist
from app.schemas.playlist import PlaylistVO, FavoriteSearchDTO
from app.schemas.music import SongVO

class FavoriteService:

    @staticmethod
    async def get_favorite_playlists(
        db: AsyncSession,
        user_id: int,
        dto: FavoriteSearchDTO
    ) -> Result[PageResult[PlaylistVO]]:
        """
        获取用户收藏的歌单列表，对齐 Java FavoriteController.getFavoritePlaylists
        """
        # 查询用户收藏的歌单 ID 列表
        fav_stmt = select(UserFavorite.playlist_id).where(
            UserFavorite.user_id == user_id,
            UserFavorite.type == 1
        ).order_by(UserFavorite.create_time.desc())

        fav_result = await db.execute(fav_stmt)
        playlist_ids = [pid for pid in fav_result.scalars().all() if pid is not None]

        if not playlist_ids:
            return Result.success(data=PageResult(total=0, items=[]))

        stmt = select(Playlist).where(Playlist.id.in_(playlist_ids))

        # 总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.scalar(count_stmt)) or 0

        # 切片
        paged_stmt = stmt.offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        res = await db.execute(paged_stmt)
        playlists = res.scalars().all()

        vo_list = [
            PlaylistVO(
                playlistId=p.id,
                title=p.title,
                coverUrl=p.cover_url,
                introduction=p.introduction,
                style=p.style,
            )
            for p in playlists
        ]

        return Result.success(data=PageResult(total=total, items=vo_list))

    @staticmethod
    async def get_favorite_songs(
        db: AsyncSession,
        user_id: int,
        dto: FavoriteSearchDTO
    ) -> Result[PageResult[SongVO]]:
        """
        获取用户收藏的歌曲列表，对齐 Java FavoriteController.getFavoriteSongs
        """
        fav_stmt = select(UserFavorite.song_id).where(
            UserFavorite.user_id == user_id,
            UserFavorite.type == 0
        ).order_by(UserFavorite.create_time.desc())

        fav_result = await db.execute(fav_stmt)
        song_ids = [sid for sid in fav_result.scalars().all() if sid is not None]

        if not song_ids:
            return Result.success(data=PageResult(total=0, items=[]))

        stmt = (
            select(Song, Artist.name.label("artist_name"))
            .outerjoin(Artist, Song.artist_id == Artist.id)
            .where(Song.id.in_(song_ids))
        )

        if dto.songName:
            stmt = stmt.where(Song.name.like(f"%{dto.songName.strip()}%"))

        # 计算总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.scalar(count_stmt)) or 0

        # 切片
        paged_stmt = stmt.offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        res = await db.execute(paged_stmt)
        rows = res.all()

        vo_list = [
            SongVO(
                songId=s.id,
                songName=s.name,
                artistName=artist_name or "群星",
                album=s.album,
                duration=s.duration,
                coverUrl=s.cover_url,
                audioUrl=s.audio_url,
                likeStatus=1,  # 收藏列表中的歌曲都是已喜欢状态
                releaseTime=s.release_time,
            )
            for s, artist_name in rows
        ]

        return Result.success(data=PageResult(total=total, items=vo_list))

    @staticmethod
    async def collect_song(db: AsyncSession, user_id: int, song_id: int) -> Result[None]:
        """
        收藏单曲
        """
        # 校验目标歌曲是否存在
        song_exists = await db.scalar(select(Song.id).where(Song.id == song_id))
        if not song_exists:
            return Result.fail(MessageConstant.SONG + MessageConstant.NOT_EXIST)

        stmt = select(func.count()).select_from(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.type == 0,
            UserFavorite.song_id == song_id
        )
        count = (await db.scalar(stmt)) or 0
        if count == 0:
            fav = UserFavorite(
                user_id=user_id,
                type=0,
                song_id=song_id,
                create_time=datetime.now()
            )
            db.add(fav)
            await db.commit()

        return Result.success(message="收藏成功", data=None)

    @staticmethod
    async def cancel_collect_song(db: AsyncSession, user_id: int, song_id: int) -> Result[None]:
        """
        取消收藏单曲
        """
        stmt = delete(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.type == 0,
            UserFavorite.song_id == song_id
        )
        await db.execute(stmt)
        await db.commit()
        return Result.success(message="已取消收藏", data=None)

    @staticmethod
    async def collect_playlist(db: AsyncSession, user_id: int, playlist_id: int) -> Result[None]:
        """
        收藏歌单
        """
        # 校验目标歌单是否存在
        playlist_exists = await db.scalar(select(Playlist.id).where(Playlist.id == playlist_id))
        if not playlist_exists:
            return Result.fail(MessageConstant.PLAYLIST + MessageConstant.NOT_EXIST)

        stmt = select(func.count()).select_from(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.type == 1,
            UserFavorite.playlist_id == playlist_id
        )
        count = (await db.scalar(stmt)) or 0
        if count == 0:
            fav = UserFavorite(
                user_id=user_id,
                type=1,
                playlist_id=playlist_id,
                create_time=datetime.now()
            )
            db.add(fav)
            await db.commit()

        return Result.success(message="收藏成功", data=None)

    @staticmethod
    async def cancel_collect_playlist(db: AsyncSession, user_id: int, playlist_id: int) -> Result[None]:
        """
        取消收藏歌单
        """
        stmt = delete(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.type == 1,
            UserFavorite.playlist_id == playlist_id
        )
        await db.execute(stmt)
        await db.commit()
        return Result.success(message="已取消收藏", data=None)

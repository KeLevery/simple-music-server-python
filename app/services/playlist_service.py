from typing import Any
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import MessageConstant
from app.core.response import Result, PageResult
from app.db.models.playlist import Playlist
from app.db.models.song import Song
from app.db.models.artist import Artist
from app.db.models.user_favorite import UserFavorite
from app.infrastructure.minio import delete_file
from app.schemas.playlist import PlaylistDTO, PlaylistVO
from app.schemas.admin import PlaylistAddDTO, PlaylistUpdateDTO

class PlaylistService:

    @staticmethod
    async def get_all_playlists_count(db: AsyncSession, style: str | None = None) -> Result[int]:
        """获取所有歌单数量，对齐 Java PlaylistServiceImpl.getAllPlaylistsCount"""
        stmt = select(func.count(Playlist.id))
        if style:
            stmt = stmt.where(Playlist.style.like(f"%{style}%"))
        count = (await db.scalar(stmt)) or 0
        return Result.success(data=count)

    @staticmethod
    async def get_all_playlists(db: AsyncSession, dto: PlaylistDTO) -> Result[PageResult[PlaylistVO]]:
        """分页获取歌单列表，对齐 Java PlaylistServiceImpl.getAllPlaylists"""
        stmt = select(Playlist)
        count_stmt = select(func.count(Playlist.id))

        conditions = []
        if dto.title:
            conditions.append(Playlist.title.like(f"%{dto.title.strip()}%"))
        if dto.style:
            conditions.append(Playlist.style.like(f"%{dto.style.strip()}%"))

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        total = (await db.scalar(count_stmt)) or 0
        if total == 0:
            return Result.success(data=PageResult(total=0, items=[]), message=MessageConstant.DATA_NOT_FOUND)

        stmt = stmt.order_by(Playlist.id.desc()).offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        result = await db.execute(stmt)
        playlists = result.scalars().all()

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
    async def add_playlist(db: AsyncSession, dto: PlaylistAddDTO) -> Result[str]:
        """新增歌单，对齐 Java PlaylistServiceImpl.addPlaylist"""
        check_stmt = select(Playlist).where(Playlist.title == dto.title)
        if (await db.execute(check_stmt)).scalar_one_or_none():
            return Result.fail(MessageConstant.PLAYLIST + MessageConstant.ALREADY_EXISTS)

        playlist = Playlist(
            title=dto.title,
            introduction=dto.introduction,
            style=dto.style,
        )
        db.add(playlist)
        await db.commit()
        return Result.success(message=MessageConstant.ADD + MessageConstant.SUCCESS)

    @staticmethod
    async def update_playlist(db: AsyncSession, dto: PlaylistUpdateDTO) -> Result[str]:
        """修改歌单，对齐 Java PlaylistServiceImpl.updatePlaylist"""
        if dto.title:
            check_stmt = select(Playlist).where(Playlist.title == dto.title, Playlist.id != dto.playlistId)
            if (await db.execute(check_stmt)).scalar_one_or_none():
                return Result.fail(MessageConstant.PLAYLIST + MessageConstant.ALREADY_EXISTS)

        stmt = select(Playlist).where(Playlist.id == dto.playlistId)
        playlist = (await db.execute(stmt)).scalar_one_or_none()
        if playlist is None:
            return Result.fail(MessageConstant.UPDATE + MessageConstant.FAILED)

        if dto.title is not None:
            playlist.title = dto.title
        if dto.introduction is not None:
            playlist.introduction = dto.introduction
        if dto.style is not None:
            playlist.style = dto.style

        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def update_playlist_cover(db: AsyncSession, playlist_id: int, cover_url: str) -> Result[str]:
        """更新歌单封面，对齐 Java PlaylistServiceImpl.updatePlaylistCover"""
        stmt = select(Playlist).where(Playlist.id == playlist_id)
        playlist = (await db.execute(stmt)).scalar_one_or_none()
        if playlist is None:
            return Result.fail(MessageConstant.UPDATE + MessageConstant.FAILED)

        if playlist.cover_url:
            delete_file(playlist.cover_url)

        playlist.cover_url = cover_url
        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_playlist(db: AsyncSession, playlist_id: int) -> Result[str]:
        """删除歌单，对齐 Java PlaylistServiceImpl.deletePlaylist"""
        stmt = select(Playlist).where(Playlist.id == playlist_id)
        playlist = (await db.execute(stmt)).scalar_one_or_none()
        if playlist is None:
            return Result.fail(MessageConstant.PLAYLIST + MessageConstant.NOT_FOUND)

        if playlist.cover_url:
            delete_file(playlist.cover_url)

        await db.delete(playlist)
        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_playlists(db: AsyncSession, playlist_ids: list[int]) -> Result[str]:
        """批量删除歌单，对齐 Java PlaylistServiceImpl.deletePlaylists"""
        if not playlist_ids:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        stmt = select(Playlist).where(Playlist.id.in_(playlist_ids))
        playlists = (await db.execute(stmt)).scalars().all()
        for p in playlists:
            if p.cover_url:
                delete_file(p.cover_url)

        del_stmt = delete(Playlist).where(Playlist.id.in_(playlist_ids))
        res = await db.execute(del_stmt)
        if res.rowcount == 0:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def get_recommended_playlists(db: AsyncSession, user_id: int | None = None) -> Result[list[PlaylistVO]]:
        """获取推荐歌单（默认获取前 10 个）"""
        stmt = select(Playlist).order_by(Playlist.id.desc()).limit(10)
        result = await db.execute(stmt)
        playlists = result.scalars().all()

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

        return Result.success(data=vo_list)

    @staticmethod
    async def get_playlist_detail(db: AsyncSession, playlist_id: int, user_id: int | None = None) -> Result[dict[str, Any]]:
        """获取歌单详情，对齐 Java PlaylistController.getPlaylistDetail"""
        stmt = select(Playlist).where(Playlist.id == playlist_id)
        result = await db.execute(stmt)
        playlist = result.scalar_one_or_none()

        if playlist is None:
            return Result.fail("歌单不存在")

        # 查询前 50 首歌曲用于填充歌单展示
        song_stmt = (
            select(Song, Artist.name.label("artist_name"))
            .outerjoin(Artist, Song.artist_id == Artist.id)
            .order_by(Song.id.desc())
            .limit(50)
        )
        song_result = await db.execute(song_stmt)
        song_rows = song_result.all()

        song_list = [
            {
                "songId": s.id,
                "artistId": s.artist_id,
                "songName": s.name,
                "artistName": artist_name or "群星",
                "album": s.album,
                "duration": s.duration,
                "coverUrl": s.cover_url,
                "audioUrl": s.audio_url,
                "releaseTime": s.release_time.strftime("%Y-%m-%d") if s.release_time else None,
            }
            for s, artist_name in song_rows
        ]

        # 检查是否已收藏该歌单
        is_collected = False
        if user_id:
            fav_stmt = select(func.count()).select_from(UserFavorite).where(
                UserFavorite.user_id == user_id,
                UserFavorite.type == 1,
                UserFavorite.playlist_id == playlist_id
            )
            count = (await db.scalar(fav_stmt)) or 0
            is_collected = count > 0

        detail = {
            "playlistId": playlist.id,
            "title": playlist.title,
            "coverUrl": playlist.cover_url,
            "introduction": playlist.introduction if playlist.introduction is not None else "暂无歌单简介",
            "style": playlist.style,
            "songs": song_list,
            "comments": [],
            "likeStatus": 0,
            "isCollected": is_collected,
        }

        return Result.success(data=detail)

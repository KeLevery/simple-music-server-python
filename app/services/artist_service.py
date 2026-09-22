from datetime import datetime, date
from typing import Any
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import MessageConstant
from app.core.response import Result, PageResult
from app.db.models.artist import Artist
from app.db.models.song import Song
from app.infrastructure.minio import delete_file
from app.schemas.music import ArtistDTO, ArtistVO
from app.schemas.admin import ArtistAddDTO, ArtistUpdateDTO

class ArtistService:

    @staticmethod
    async def get_all_artists_count(db: AsyncSession, gender: int | None = None, area: str | None = None) -> Result[int]:
        """获取所有歌手数量，对齐 Java ArtistServiceImpl.getAllArtistsCount"""
        stmt = select(func.count(Artist.id))
        if gender is not None:
            stmt = stmt.where(Artist.gender == gender)
        if area:
            stmt = stmt.where(Artist.area == area)
        count = (await db.scalar(stmt)) or 0
        return Result.success(data=count)

    @staticmethod
    async def get_all_artists(db: AsyncSession, dto: ArtistDTO) -> Result[PageResult[ArtistVO]]:
        """分页获取歌手列表，复刻 Java ArtistServiceImpl.getAllArtists"""
        stmt = select(Artist)
        count_stmt = select(func.count(Artist.id))

        conditions = []
        if dto.artistName:
            conditions.append(Artist.name.like(f"%{dto.artistName.strip()}%"))
        if dto.gender is not None:
            conditions.append(Artist.gender == dto.gender)
        if dto.area:
            conditions.append(Artist.area.like(f"%{dto.area.strip()}%"))

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        total = (await db.scalar(count_stmt)) or 0
        if total == 0:
            return Result.success(data=PageResult(total=0, items=[]), message=MessageConstant.DATA_NOT_FOUND)

        stmt = stmt.order_by(Artist.id.desc()).offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        result = await db.execute(stmt)
        artists = result.scalars().all()

        vo_list = [
            ArtistVO(
                artistId=artist.id,
                artistName=artist.name,
                gender=artist.gender,
                birth=artist.birth,
                area=artist.area,
                introduction=artist.introduction,
                avatar=artist.avatar,
            )
            for artist in artists
        ]

        return Result.success(data=PageResult(total=total, items=vo_list))

    @staticmethod
    async def get_all_artists_and_detail(db: AsyncSession, dto: ArtistDTO) -> Result[PageResult[ArtistVO]]:
        """管理端获取歌手列表，对齐 Java ArtistServiceImpl.getAllArtistsAndDetail"""
        return await ArtistService.get_all_artists(db, dto)

    @staticmethod
    async def get_artist_detail(db: AsyncSession, artist_id: int) -> Result[dict[str, Any]]:
        """获取歌手详情与名下歌曲，复刻 Java ArtistController.getArtistDetail"""
        stmt = select(Artist).where(Artist.id == artist_id)
        result = await db.execute(stmt)
        artist = result.scalar_one_or_none()

        if artist is None:
            return Result.fail("歌手不存在")

        song_stmt = select(Song).where(Song.artist_id == artist_id).order_by(Song.id.desc())
        song_result = await db.execute(song_stmt)
        songs = song_result.scalars().all()

        song_list = [
            {
                "songId": s.id,
                "artistId": s.artist_id,
                "songName": s.name,
                "album": s.album,
                "lyric": s.lyric,
                "duration": s.duration,
                "style": s.style,
                "coverUrl": s.cover_url,
                "audioUrl": s.audio_url,
                "releaseTime": s.release_time.strftime("%Y-%m-%d") if s.release_time else None,
            }
            for s in songs
        ]

        detail = {
            "artistId": artist.id,
            "artistName": artist.name,
            "avatar": artist.avatar,
            "birth": artist.birth.strftime("%Y-%m-%d") if artist.birth else None,
            "area": artist.area,
            "introduction": artist.introduction if artist.introduction is not None else "暂无简介",
            "songs": song_list,
        }

        return Result.success(data=detail)

    @staticmethod
    async def add_artist(db: AsyncSession, dto: ArtistAddDTO) -> Result[str]:
        """新增歌手，对齐 Java ArtistServiceImpl.addArtist"""
        check_stmt = select(Artist).where(Artist.name == dto.artistName)
        if (await db.execute(check_stmt)).scalar_one_or_none():
            return Result.fail(MessageConstant.ARTIST + MessageConstant.ALREADY_EXISTS)

        birth_val = None
        if dto.birth:
            try:
                birth_val = datetime.strptime(dto.birth, "%Y-%m-%d").date()
            except Exception:
                pass

        artist = Artist(
            name=dto.artistName,
            gender=dto.gender,
            birth=birth_val,
            area=dto.area,
            introduction=dto.introduction,
        )
        db.add(artist)
        await db.commit()
        return Result.success(message=MessageConstant.ARTIST + MessageConstant.ADD + MessageConstant.SUCCESS)

    @staticmethod
    async def update_artist(db: AsyncSession, dto: ArtistUpdateDTO) -> Result[str]:
        """修改歌手，对齐 Java ArtistServiceImpl.updateArtist"""
        if dto.artistName:
            check_stmt = select(Artist).where(Artist.name == dto.artistName, Artist.id != dto.artistId)
            if (await db.execute(check_stmt)).scalar_one_or_none():
                return Result.fail(MessageConstant.ARTIST + MessageConstant.ALREADY_EXISTS)

        stmt = select(Artist).where(Artist.id == dto.artistId)
        artist = (await db.execute(stmt)).scalar_one_or_none()
        if artist is None:
            return Result.fail(MessageConstant.UPDATE + MessageConstant.FAILED)

        if dto.artistName is not None:
            artist.name = dto.artistName
        if dto.gender is not None:
            artist.gender = dto.gender
        if dto.birth is not None:
            try:
                artist.birth = datetime.strptime(dto.birth, "%Y-%m-%d").date()
            except Exception:
                pass
        if dto.area is not None:
            artist.area = dto.area
        if dto.introduction is not None:
            artist.introduction = dto.introduction

        await db.commit()
        return Result.success(message=MessageConstant.ARTIST + MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def update_artist_avatar(db: AsyncSession, artist_id: int, avatar_url: str) -> Result[str]:
        """更新歌手头像，对齐 Java ArtistServiceImpl.updateArtistAvatar"""
        stmt = select(Artist).where(Artist.id == artist_id)
        artist = (await db.execute(stmt)).scalar_one_or_none()
        if artist is None:
            return Result.fail(MessageConstant.UPDATE + MessageConstant.FAILED)

        if artist.avatar:
            delete_file(artist.avatar)

        artist.avatar = avatar_url
        await db.commit()
        return Result.success(message=MessageConstant.ARTIST + MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_artist(db: AsyncSession, artist_id: int) -> Result[str]:
        """删除歌手，对齐 Java ArtistServiceImpl.deleteArtist"""
        stmt = select(Artist).where(Artist.id == artist_id)
        artist = (await db.execute(stmt)).scalar_one_or_none()
        if artist is None:
            return Result.fail(MessageConstant.ARTIST + MessageConstant.NOT_FOUND)

        if artist.avatar:
            delete_file(artist.avatar)

        await db.delete(artist)
        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_artists(db: AsyncSession, artist_ids: list[int]) -> Result[str]:
        """批量删除歌手，对齐 Java ArtistServiceImpl.deleteArtists"""
        if not artist_ids:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        stmt = select(Artist).where(Artist.id.in_(artist_ids))
        artists = (await db.execute(stmt)).scalars().all()
        for a in artists:
            if a.avatar:
                delete_file(a.avatar)

        del_stmt = delete(Artist).where(Artist.id.in_(artist_ids))
        res = await db.execute(del_stmt)
        if res.rowcount == 0:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

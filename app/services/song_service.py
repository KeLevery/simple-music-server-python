from datetime import datetime, date
from typing import Any
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import MessageConstant
from app.core.response import Result, PageResult
from app.db.models.song import Song
from app.db.models.artist import Artist
from app.db.models.style import Style
from app.db.models.genre import Genre
from app.db.models.user_favorite import UserFavorite
from app.infrastructure.minio import delete_file
from app.schemas.music import SongDTO, SongVO, SongDetailVO
from app.schemas.admin import SongAndArtistDTO, SongAddDTO, SongUpdateDTO, SongAdminVO, ArtistNameVO

class SongService:

    @staticmethod
    async def get_all_songs_count(db: AsyncSession, style: str | None = None) -> Result[int]:
        """获取所有歌曲数量，对齐 Java SongServiceImpl.getAllSongsCount"""
        stmt = select(func.count(Song.id))
        if style:
            stmt = stmt.where(Song.style.like(f"%{style}%"))
        count = (await db.scalar(stmt)) or 0
        return Result.success(data=count)

    @staticmethod
    async def get_all_artist_names(db: AsyncSession) -> Result[list[ArtistNameVO]]:
        """获取所有歌手名称列表，对齐 Java SongServiceImpl.getAllArtistNames"""
        stmt = select(Artist).order_by(Artist.id.desc())
        result = await db.execute(stmt)
        artists = result.scalars().all()
        if not artists:
            return Result.success(message=MessageConstant.DATA_NOT_FOUND, data=[])

        vo_list = [ArtistNameVO(artistId=a.id, artistName=a.name) for a in artists]
        return Result.success(data=vo_list)

    @staticmethod
    async def get_all_songs_by_artist(db: AsyncSession, dto: SongAndArtistDTO) -> Result[PageResult[SongAdminVO]]:
        """管理端获取歌曲列表，对齐 Java SongServiceImpl.getAllSongsByArtist"""
        stmt = (
            select(Song, Artist.name.label("artist_name"))
            .outerjoin(Artist, Song.artist_id == Artist.id)
        )
        count_stmt = (
            select(func.count(Song.id))
            .select_from(Song)
            .outerjoin(Artist, Song.artist_id == Artist.id)
        )

        conditions = []
        if dto.artistId is not None:
            conditions.append(Song.artist_id == dto.artistId)
        if dto.songName:
            conditions.append(Song.name.like(f"%{dto.songName.strip()}%"))
        if dto.album:
            conditions.append(Song.album.like(f"%{dto.album.strip()}%"))

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        total = (await db.scalar(count_stmt)) or 0
        if total == 0:
            return Result.success(message=MessageConstant.DATA_NOT_FOUND, data=PageResult(total=0, items=[]))

        stmt = stmt.order_by(Song.release_time.desc(), Song.id.desc()).offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        result = await db.execute(stmt)
        rows = result.all()

        records = [
            SongAdminVO(
                songId=song.id,
                artistName=artist_name or "群星",
                songName=song.name,
                album=song.album,
                lyric=song.lyric,
                duration=song.duration,
                style=song.style,
                coverUrl=song.cover_url,
                audioUrl=song.audio_url,
                releaseTime=song.release_time,
            )
            for song, artist_name in rows
        ]

        return Result.success(data=PageResult(total=total, items=records))

    @staticmethod
    async def add_song(db: AsyncSession, dto: SongAddDTO) -> Result[str]:
        """新增歌曲，对齐 Java SongServiceImpl.addSong"""
        release_date = None
        if dto.releaseTime:
            if isinstance(dto.releaseTime, date):
                release_date = dto.releaseTime
            else:
                try:
                    release_date = datetime.strptime(str(dto.releaseTime), "%Y-%m-%d").date()
                except Exception:
                    pass

        song = Song(
            artist_id=dto.artistId,
            name=dto.songName,
            album=dto.album,
            style=dto.style,
            release_time=release_date,
        )
        db.add(song)
        await db.flush()  # 生成 song.id

        # 处理歌曲风格关联 tb_genre
        if dto.style:
            styles = [s.strip() for s in dto.style.split(",") if s.strip()]
            if styles:
                style_stmt = select(Style).where(Style.name.in_(styles))
                style_res = await db.execute(style_stmt)
                style_entities = style_res.scalars().all()
                for st in style_entities:
                    genre = Genre(song_id=song.id, style_id=st.id)
                    db.add(genre)

        await db.commit()
        return Result.success(message=MessageConstant.ADD + MessageConstant.SUCCESS)

    @staticmethod
    async def update_song(db: AsyncSession, dto: SongUpdateDTO) -> Result[str]:
        """修改歌曲，对齐 Java SongServiceImpl.updateSong"""
        stmt = select(Song).where(Song.id == dto.songId)
        song = (await db.execute(stmt)).scalar_one_or_none()
        if song is None:
            return Result.fail(MessageConstant.SONG + MessageConstant.NOT_FOUND)

        if dto.artistId is not None:
            song.artist_id = dto.artistId
        if dto.songName is not None:
            song.name = dto.songName
        if dto.album is not None:
            song.album = dto.album
        if dto.style is not None:
            song.style = dto.style
        if dto.releaseTime is not None:
            if isinstance(dto.releaseTime, date):
                song.release_time = dto.releaseTime
            else:
                try:
                    song.release_time = datetime.strptime(str(dto.releaseTime), "%Y-%m-%d").date()
                except Exception:
                    pass

        # 更新风格关联
        if dto.style is not None:
            del_genre_stmt = delete(Genre).where(Genre.song_id == dto.songId)
            await db.execute(del_genre_stmt)

            styles = [s.strip() for s in dto.style.split(",") if s.strip()]
            if styles:
                style_stmt = select(Style).where(Style.name.in_(styles))
                style_res = await db.execute(style_stmt)
                style_entities = style_res.scalars().all()
                for st in style_entities:
                    genre = Genre(song_id=song.id, style_id=st.id)
                    db.add(genre)

        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def update_song_cover(db: AsyncSession, song_id: int, cover_url: str) -> Result[str]:
        """更新歌曲封面，对齐 Java SongServiceImpl.updateSongCover"""
        stmt = select(Song).where(Song.id == song_id)
        song = (await db.execute(stmt)).scalar_one_or_none()
        if song is None:
            return Result.fail(MessageConstant.UPDATE + MessageConstant.FAILED)

        if song.cover_url:
            delete_file(song.cover_url)

        song.cover_url = cover_url
        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def update_song_audio(db: AsyncSession, song_id: int, audio_url: str) -> Result[str]:
        """更新歌曲音频，对齐 Java SongServiceImpl.updateSongAudio"""
        stmt = select(Song).where(Song.id == song_id)
        song = (await db.execute(stmt)).scalar_one_or_none()
        if song is None:
            return Result.fail(MessageConstant.UPDATE + MessageConstant.FAILED)

        if song.audio_url:
            delete_file(song.audio_url)

        song.audio_url = audio_url
        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_song(db: AsyncSession, song_id: int) -> Result[str]:
        """删除歌曲，对齐 Java SongServiceImpl.deleteSong"""
        stmt = select(Song).where(Song.id == song_id)
        song = (await db.execute(stmt)).scalar_one_or_none()
        if song is None:
            return Result.fail(MessageConstant.SONG + MessageConstant.NOT_FOUND)

        if song.cover_url:
            delete_file(song.cover_url)
        if song.audio_url:
            delete_file(song.audio_url)

        # 删除 genre 关联
        del_genre = delete(Genre).where(Genre.song_id == song_id)
        await db.execute(del_genre)

        # 级联删除收藏记录
        del_fav = delete(UserFavorite).where(
            UserFavorite.type == 0,
            UserFavorite.song_id == song_id
        )
        await db.execute(del_fav)

        await db.delete(song)
        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_songs(db: AsyncSession, song_ids: list[int]) -> Result[str]:
        """批量删除歌曲，对齐 Java SongServiceImpl.deleteSongs"""
        if not song_ids:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        stmt = select(Song).where(Song.id.in_(song_ids))
        songs = (await db.execute(stmt)).scalars().all()
        for s in songs:
            if s.cover_url:
                delete_file(s.cover_url)
            if s.audio_url:
                delete_file(s.audio_url)

        # 删除 genre 关联
        del_genre = delete(Genre).where(Genre.song_id.in_(song_ids))
        await db.execute(del_genre)

        # 级联删除收藏记录
        del_fav = delete(UserFavorite).where(
            UserFavorite.type == 0,
            UserFavorite.song_id.in_(song_ids)
        )
        await db.execute(del_fav)

        del_songs = delete(Song).where(Song.id.in_(song_ids))
        res = await db.execute(del_songs)
        if res.rowcount == 0:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def get_all_songs(
        db: AsyncSession,
        dto: SongDTO,
        user_id: int | None = None
    ) -> Result[PageResult[SongVO]]:
        """分页获取歌曲列表（前台）"""
        stmt = (
            select(Song, Artist.name.label("artist_name"))
            .outerjoin(Artist, Song.artist_id == Artist.id)
        )
        count_stmt = (
            select(func.count(Song.id))
            .select_from(Song)
            .outerjoin(Artist, Song.artist_id == Artist.id)
        )

        conditions = []
        if dto.songName:
            conditions.append(Song.name.like(f"%{dto.songName.strip()}%"))
        if dto.artistName:
            conditions.append(Artist.name.like(f"%{dto.artistName.strip()}%"))
        if dto.album:
            conditions.append(Song.album.like(f"%{dto.album.strip()}%"))

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        total = (await db.scalar(count_stmt)) or 0
        if total == 0:
            return Result.success(data=PageResult(total=0, items=[]), message=MessageConstant.DATA_NOT_FOUND)

        stmt = stmt.order_by(Song.id.desc()).offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        result = await db.execute(stmt)
        rows = result.all()

        fav_song_ids: set[int] = set()
        if user_id:
            fav_stmt = select(UserFavorite.song_id).where(
                UserFavorite.user_id == user_id,
                UserFavorite.type == 0
            )
            fav_res = await db.execute(fav_stmt)
            fav_song_ids = set(fav_res.scalars().all())

        vo_list = [
            SongVO(
                songId=song.id,
                songName=song.name,
                artistName=artist_name or "群星",
                album=song.album,
                duration=song.duration,
                coverUrl=song.cover_url,
                audioUrl=song.audio_url,
                likeStatus=1 if song.id in fav_song_ids else 0,
                releaseTime=song.release_time,
            )
            for song, artist_name in rows
        ]

        return Result.success(data=PageResult(total=total, items=vo_list))

    @staticmethod
    async def get_recommended_songs(
        db: AsyncSession,
        user_id: int | None = None
    ) -> Result[list[SongVO]]:
        """获取推荐歌曲列表（前台）"""
        stmt = (
            select(Song, Artist.name.label("artist_name"))
            .outerjoin(Artist, Song.artist_id == Artist.id)
            .order_by(Song.id.desc())
            .limit(20)
        )
        result = await db.execute(stmt)
        rows = result.all()

        fav_song_ids: set[int] = set()
        if user_id:
            fav_stmt = select(UserFavorite.song_id).where(
                UserFavorite.user_id == user_id,
                UserFavorite.type == 0
            )
            fav_res = await db.execute(fav_stmt)
            fav_song_ids = set(fav_res.scalars().all())

        vo_list = [
            SongVO(
                songId=song.id,
                songName=song.name,
                artistName=artist_name or "群星",
                album=song.album,
                duration=song.duration,
                coverUrl=song.cover_url,
                audioUrl=song.audio_url,
                likeStatus=1 if song.id in fav_song_ids else 0,
                releaseTime=song.release_time,
            )
            for song, artist_name in rows
        ]

        return Result.success(data=vo_list)

    @staticmethod
    async def get_song_detail(
        db: AsyncSession,
        song_id: int,
        user_id: int | None = None
    ) -> Result[SongDetailVO]:
        """获取单曲详情（前台）"""
        stmt = (
            select(Song, Artist.name.label("artist_name"))
            .outerjoin(Artist, Song.artist_id == Artist.id)
            .where(Song.id == song_id)
        )
        result = await db.execute(stmt)
        row = result.first()

        if row is None:
            return Result.fail(MessageConstant.SONG + MessageConstant.NOT_FOUND)

        song, artist_name = row

        like_status = 0
        if user_id:
            fav_stmt = select(func.count()).select_from(UserFavorite).where(
                UserFavorite.user_id == user_id,
                UserFavorite.type == 0,
                UserFavorite.song_id == song_id
            )
            count = (await db.scalar(fav_stmt)) or 0
            if count > 0:
                like_status = 1

        detail = SongDetailVO(
            songId=song.id,
            songName=song.name,
            artistName=artist_name or "群星",
            album=song.album,
            lyric=song.lyric,
            duration=song.duration,
            coverUrl=song.cover_url,
            audioUrl=song.audio_url,
            releaseTime=song.release_time,
            likeStatus=like_status,
            comments=[],
        )

        return Result.success(data=detail)

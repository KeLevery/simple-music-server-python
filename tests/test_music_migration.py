import pytest
from httpx import AsyncClient

# ==================== Song 接口测试 ====================

@pytest.mark.asyncio
async def test_get_recommended_songs(async_client: AsyncClient):
    """测试获取推荐歌曲列表契约"""
    response = await async_client.get("/song/getRecommendedSongs")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["message"] == "操作成功"
    assert isinstance(res["data"], list)
    if len(res["data"]) > 0:
        song = res["data"][0]
        assert "songId" in song
        assert "songName" in song
        assert "artistName" in song
        assert "likeStatus" in song
        assert "coverUrl" in song
        assert "audioUrl" in song

@pytest.mark.asyncio
async def test_get_all_songs_pagination(async_client: AsyncClient):
    """测试分页获取所有歌曲"""
    payload = {
        "pageNum": 1,
        "pageSize": 10
    }
    response = await async_client.post("/song/getAllSongs", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert "total" in res["data"]
    assert "items" in res["data"]
    assert res["data"]["total"] > 0
    assert len(res["data"]["items"]) <= 10

@pytest.mark.asyncio
async def test_get_all_songs_with_filter(async_client: AsyncClient):
    """测试按关键词搜索歌曲"""
    payload = {
        "pageNum": 1,
        "pageSize": 10,
        "songName": "非真实存在的极其罕见的歌曲名称_9999"
    }
    response = await async_client.post("/song/getAllSongs", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["data"]["total"] == 0
    assert res["data"]["items"] == []

@pytest.mark.asyncio
async def test_get_song_detail_success(async_client: AsyncClient):
    """测试获取真实存在的单曲详情"""
    # 先获取第一首歌曲的 ID
    list_resp = await async_client.post("/song/getAllSongs", json={"pageNum": 1, "pageSize": 1})
    first_song = list_resp.json()["data"]["items"][0]
    song_id = first_song["songId"]

    response = await async_client.get(f"/song/getSongDetail/{song_id}")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["data"]["songId"] == song_id
    assert res["data"]["songName"] == first_song["songName"]
    assert "artistName" in res["data"]
    assert "lyric" in res["data"]
    assert "likeStatus" in res["data"]

@pytest.mark.asyncio
async def test_get_song_detail_not_found(async_client: AsyncClient):
    """测试获取不存在的歌曲详情返回 code: 1"""
    response = await async_client.get("/song/getSongDetail/99999999")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 1
    assert "NOT_FOUND" in res["message"]


# ==================== Artist 接口测试 ====================

@pytest.mark.asyncio
async def test_get_all_artists_pagination(async_client: AsyncClient):
    """测试分页获取歌手列表"""
    payload = {
        "pageNum": 1,
        "pageSize": 10
    }
    response = await async_client.post("/artist/getAllArtists", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["data"]["total"] > 0
    assert len(res["data"]["items"]) <= 10
    artist = res["data"]["items"][0]
    assert "artistId" in artist
    assert "artistName" in artist

@pytest.mark.asyncio
async def test_get_artist_detail_success(async_client: AsyncClient):
    """测试获取真实存在的歌手详情及名下歌曲"""
    list_resp = await async_client.post("/artist/getAllArtists", json={"pageNum": 1, "pageSize": 1})
    first_artist = list_resp.json()["data"]["items"][0]
    artist_id = first_artist["artistId"]

    response = await async_client.get(f"/artist/getArtistDetail/{artist_id}")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    data = res["data"]
    assert data["artistId"] == artist_id
    assert data["artistName"] == first_artist["artistName"]
    assert "songs" in data
    assert isinstance(data["songs"], list)

@pytest.mark.asyncio
async def test_get_artist_detail_not_found(async_client: AsyncClient):
    """测试获取不存在的歌手详情"""
    response = await async_client.get("/artist/getArtistDetail/99999999")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 1
    assert res["message"] == "歌手不存在"

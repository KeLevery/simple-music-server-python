import pytest
from httpx import AsyncClient

EXISTING_USER_EMAIL = "user651@example.com"
EXISTING_USER_PASSWORD_RAW = "123456abc"

# ==================== Playlist 测试 ====================

@pytest.mark.asyncio
async def test_get_recommended_playlists(async_client: AsyncClient):
    """测试获取推荐歌单列表"""
    response = await async_client.get("/playlist/getRecommendedPlaylists")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["message"] == "操作成功"
    assert isinstance(res["data"], list)
    if len(res["data"]) > 0:
        p = res["data"][0]
        assert "playlistId" in p
        assert "title" in p
        assert "coverUrl" in p

@pytest.mark.asyncio
async def test_get_all_playlists_pagination(async_client: AsyncClient):
    """测试分页获取所有歌单（歌单广场）"""
    payload = {
        "pageNum": 1,
        "pageSize": 5
    }
    response = await async_client.post("/playlist/getAllPlaylists", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["data"]["total"] > 0
    assert len(res["data"]["items"]) <= 5

@pytest.mark.asyncio
async def test_get_playlist_detail_success(async_client: AsyncClient):
    """测试获取真实存在的歌单详情"""
    list_resp = await async_client.post("/playlist/getAllPlaylists", json={"pageNum": 1, "pageSize": 1})
    first_playlist = list_resp.json()["data"]["items"][0]
    playlist_id = first_playlist["playlistId"]

    response = await async_client.get(f"/playlist/getPlaylistDetail/{playlist_id}")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    data = res["data"]
    assert data["playlistId"] == playlist_id
    assert data["title"] == first_playlist["title"]
    assert "songs" in data
    assert isinstance(data["songs"], list)
    assert "isCollected" in data

@pytest.mark.asyncio
async def test_get_playlist_detail_not_found(async_client: AsyncClient):
    """测试不存在歌单详情返回 code: 1"""
    response = await async_client.get("/playlist/getPlaylistDetail/99999999")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 1
    assert res["message"] == "歌单不存在"


# ==================== Banner 测试 ====================

@pytest.mark.asyncio
async def test_get_banner_list(async_client: AsyncClient):
    """测试获取前台轮播图列表"""
    response = await async_client.get("/banner/getBannerList")
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert isinstance(res["data"], list)
    if len(res["data"]) > 0:
        b = res["data"][0]
        assert "bannerId" in b
        assert "bannerUrl" in b


# ==================== Favorite 测试 ====================

@pytest.mark.asyncio
async def test_favorite_operations_lifecycle(async_client: AsyncClient):
    """测试完整的收藏/取消收藏生命周期与查询契约"""
    # 1. 登录用户
    login_resp = await async_client.post("/user/login", json={
        "email": EXISTING_USER_EMAIL,
        "password": EXISTING_USER_PASSWORD_RAW
    })
    token = login_resp.json()["data"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 查询一首歌曲与一个歌单
    song_resp = await async_client.post("/song/getAllSongs", json={"pageNum": 1, "pageSize": 1})
    song_id = song_resp.json()["data"]["items"][0]["songId"]

    playlist_resp = await async_client.post("/playlist/getAllPlaylists", json={"pageNum": 1, "pageSize": 1})
    playlist_id = playlist_resp.json()["data"]["items"][0]["playlistId"]

    # 3. 收藏歌曲
    collect_song_res = await async_client.post(f"/favorite/collectSong?songId={song_id}", headers=headers)
    assert collect_song_res.status_code == 200
    assert collect_song_res.json()["code"] == 0
    assert collect_song_res.json()["message"] == "收藏成功"

    # 4. 获取用户收藏歌曲列表
    fav_songs_res = await async_client.post("/favorite/getFavoriteSongs", json={"pageNum": 1, "pageSize": 20}, headers=headers)
    assert fav_songs_res.status_code == 200
    assert fav_songs_res.json()["code"] == 0
    fav_song_ids = [s["songId"] for s in fav_songs_res.json()["data"]["items"]]
    assert song_id in fav_song_ids

    # 5. 取消收藏歌曲
    cancel_song_res = await async_client.delete(f"/favorite/cancelCollectSong?songId={song_id}", headers=headers)
    assert cancel_song_res.status_code == 200
    assert cancel_song_res.json()["code"] == 0
    assert cancel_song_res.json()["message"] == "已取消收藏"

    # 6. 收藏歌单
    collect_pl_res = await async_client.post(f"/favorite/collectPlaylist?playlistId={playlist_id}", headers=headers)
    assert collect_pl_res.status_code == 200
    assert collect_pl_res.json()["code"] == 0
    assert collect_pl_res.json()["message"] == "收藏成功"

    # 7. 获取用户收藏歌单列表
    fav_pl_res = await async_client.post("/favorite/getFavoritePlaylists", json={"pageNum": 1, "pageSize": 20}, headers=headers)
    assert fav_pl_res.status_code == 200
    assert fav_pl_res.json()["code"] == 0
    fav_pl_ids = [p["playlistId"] for p in fav_pl_res.json()["data"]["items"]]
    assert playlist_id in fav_pl_ids

    # 8. 取消收藏歌单
    cancel_pl_res = await async_client.delete(f"/favorite/cancelCollectPlaylist?playlistId={playlist_id}", headers=headers)
    assert cancel_pl_res.status_code == 200
    assert cancel_pl_res.json()["code"] == 0
    assert cancel_pl_res.json()["message"] == "已取消收藏"

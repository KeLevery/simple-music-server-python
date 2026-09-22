import uuid
import pytest
from httpx import AsyncClient

ADMIN_USERNAME = "admin_172"
ADMIN_PASSWORD_RAW = "123456abc"

@pytest.fixture
async def admin_auth_headers(async_client: AsyncClient) -> dict[str, str]:
    """登录管理员并获取带有 Token 的 Headers"""
    res = await async_client.post("/admin/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD_RAW,
    })
    assert res.status_code == 200
    token = res.json()["data"]
    return {"Authorization": f"Bearer {token}"}

# ==================== 1. 仪表盘统计测试 ====================

@pytest.mark.asyncio
async def test_admin_dashboard_counts(async_client: AsyncClient, admin_auth_headers: dict[str, str]):
    """测试获取各模块统计总数"""
    # 用户总数
    user_cnt = await async_client.get("/admin/getAllUsersCount", headers=admin_auth_headers)
    assert user_cnt.status_code == 200
    assert user_cnt.json()["code"] == 0
    assert isinstance(user_cnt.json()["data"], int)
    assert user_cnt.json()["data"] >= 0

    # 歌手总数
    artist_cnt = await async_client.get("/admin/getAllArtistsCount", headers=admin_auth_headers)
    assert artist_cnt.status_code == 200
    assert artist_cnt.json()["code"] == 0
    assert isinstance(artist_cnt.json()["data"], int)

    # 歌曲总数
    song_cnt = await async_client.get("/admin/getAllSongsCount", headers=admin_auth_headers)
    assert song_cnt.status_code == 200
    assert song_cnt.json()["code"] == 0
    assert isinstance(song_cnt.json()["data"], int)

    # 歌单总数
    playlist_cnt = await async_client.get("/admin/getAllPlaylistsCount", headers=admin_auth_headers)
    assert playlist_cnt.status_code == 200
    assert playlist_cnt.json()["code"] == 0
    assert isinstance(playlist_cnt.json()["data"], int)

    # 歌手名称列表
    artist_names = await async_client.get("/admin/getAllArtistNames", headers=admin_auth_headers)
    assert artist_names.status_code == 200
    assert artist_names.json()["code"] == 0
    assert isinstance(artist_names.json()["data"], list)

# ==================== 2. 用户管理测试 ====================

@pytest.mark.asyncio
async def test_admin_user_crud(async_client: AsyncClient, admin_auth_headers: dict[str, str]):
    """测试用户增删改查生命周期"""
    uid = uuid.uuid4().hex[:8]
    temp_uname = f"u_{uid}"
    temp_email = f"u_{uid}@test.com"
    phone_suffix = f"{int(uuid.uuid4().int % 100000000):08d}"
    temp_phone = f"138{phone_suffix}"

    # 1. 查询用户列表
    search_res = await async_client.post("/admin/getAllUsers", json={"pageNum": 1, "pageSize": 10}, headers=admin_auth_headers)
    assert search_res.status_code == 200
    assert search_res.json()["code"] == 0
    assert search_res.json()["data"]["total"] > 0

    # 2. 新增临时用户
    add_res = await async_client.post("/admin/addUser", json={
        "username": temp_uname,
        "password": "Password123!",
        "phone": temp_phone,
        "email": temp_email,
        "introduction": "自动化测试创建",
        "userStatus": 1,
    }, headers=admin_auth_headers)
    assert add_res.status_code == 200
    assert add_res.json()["code"] == 0
    assert add_res.json()["message"] == "添加成功"

    # 3. 查出刚创建的用户获取 ID
    find_res = await async_client.post("/admin/getAllUsers", json={"pageNum": 1, "pageSize": 1, "username": temp_uname}, headers=admin_auth_headers)
    created_user = find_res.json()["data"]["items"][0]
    user_id = created_user["userId"]
    assert created_user["username"] == temp_uname

    # 4. 修改用户信息
    upd_res = await async_client.put("/admin/updateUser", json={
        "userId": user_id,
        "username": f"up_{uid}",
        "phone": f"139{phone_suffix}",
        "email": f"up_{uid}@test.com",
        "introduction": "更新后的简介",
    }, headers=admin_auth_headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["code"] == 0
    assert upd_res.json()["message"] == "更新成功"

    # 5. 更新用户状态
    status_res = await async_client.patch(f"/admin/updateUserStatus/{user_id}/1", headers=admin_auth_headers)
    assert status_res.status_code == 200
    assert status_res.json()["code"] == 0
    assert status_res.json()["message"] == "更新成功"

    # 6. 删除用户
    del_res = await async_client.delete(f"/admin/deleteUser/{user_id}", headers=admin_auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["code"] == 0
    assert del_res.json()["message"] == "删除成功"

# ==================== 3. 歌手管理测试 ====================

@pytest.mark.asyncio
async def test_admin_artist_crud(async_client: AsyncClient, admin_auth_headers: dict[str, str]):
    """测试歌手增删改查生命周期"""
    uid = uuid.uuid4().hex[:8]
    temp_artist_name = f"歌手_{uid}"

    # 1. 新增歌手
    add_res = await async_client.post("/admin/addArtist", json={
        "artistName": temp_artist_name,
        "gender": 0,
        "birth": "1990-01-01",
        "area": "中国大陆",
        "introduction": "测试歌手简介",
    }, headers=admin_auth_headers)
    assert add_res.status_code == 200
    assert add_res.json()["code"] == 0

    # 重复新增应报错
    dup_res = await async_client.post("/admin/addArtist", json={
        "artistName": temp_artist_name,
        "gender": 0,
    }, headers=admin_auth_headers)
    assert dup_res.status_code == 200
    assert dup_res.json()["code"] == 1
    assert "已存在" in dup_res.json()["message"]

    # 2. 查询列表拿到 ID
    query_res = await async_client.post("/admin/getAllArtists", json={
        "pageNum": 1,
        "pageSize": 1,
        "artistName": temp_artist_name,
    }, headers=admin_auth_headers)
    artist_id = query_res.json()["data"]["items"][0]["artistId"]

    # 3. 编辑歌手
    upd_res = await async_client.put("/admin/updateArtist", json={
        "artistId": artist_id,
        "artistName": temp_artist_name + "_已更新",
        "gender": 1,
        "area": "中国香港",
    }, headers=admin_auth_headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["code"] == 0

    # 4. 删除歌手
    del_res = await async_client.delete(f"/admin/deleteArtist/{artist_id}", headers=admin_auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["code"] == 0
    assert del_res.json()["message"] == "删除成功"

# ==================== 4. 歌曲管理测试 ====================

@pytest.mark.asyncio
async def test_admin_song_crud(async_client: AsyncClient, admin_auth_headers: dict[str, str]):
    """测试歌曲增删改查生命周期"""
    uid = uuid.uuid4().hex[:8]
    temp_song_name = f"歌曲_{uid}"

    # 动态获取一个真实存在的歌手 ID
    artist_names_res = await async_client.get("/admin/getAllArtistNames", headers=admin_auth_headers)
    assert artist_names_res.status_code == 200
    first_artist = artist_names_res.json()["data"][0]
    valid_artist_id = first_artist["artistId"]

    # 1. 新增歌曲
    add_res = await async_client.post("/admin/addSong", json={
        "artistId": valid_artist_id,
        "songName": temp_song_name,
        "album": "测试专辑",
        "style": "流行",
        "releaseTime": "2024-01-01",
    }, headers=admin_auth_headers)
    assert add_res.status_code == 200
    assert add_res.json()["code"] == 0

    # 2. 查出刚新增的歌曲
    query_res = await async_client.post("/admin/getAllSongsByArtist", json={
        "pageNum": 1,
        "pageSize": 1,
        "songName": temp_song_name,
    }, headers=admin_auth_headers)
    song_id = query_res.json()["data"]["items"][0]["songId"]

    # 3. 修改歌曲
    upd_res = await async_client.put("/admin/updateSong", json={
        "songId": song_id,
        "songName": temp_song_name + "_已更新",
        "album": "新专辑",
    }, headers=admin_auth_headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["code"] == 0

    # 4. 删除歌曲
    del_res = await async_client.delete(f"/admin/deleteSong/{song_id}", headers=admin_auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["code"] == 0
    assert del_res.json()["message"] == "删除成功"

# ==================== 5. 歌单管理测试 ====================

@pytest.mark.asyncio
async def test_admin_playlist_crud(async_client: AsyncClient, admin_auth_headers: dict[str, str]):
    """测试歌单增删改查生命周期"""
    uid = uuid.uuid4().hex[:8]
    temp_title = f"歌单_{uid}"

    # 1. 新增歌单
    add_res = await async_client.post("/admin/addPlaylist", json={
        "title": temp_title,
        "introduction": "测试歌单描述",
        "style": "民谣",
    }, headers=admin_auth_headers)
    assert add_res.status_code == 200
    assert add_res.json()["code"] == 0

    # 2. 查出刚新增的歌单
    query_res = await async_client.post("/admin/getAllPlaylists", json={
        "pageNum": 1,
        "pageSize": 1,
        "title": temp_title,
    }, headers=admin_auth_headers)
    playlist_id = query_res.json()["data"]["items"][0]["playlistId"]

    # 3. 修改歌单
    upd_res = await async_client.put("/admin/updatePlaylist", json={
        "playlistId": playlist_id,
        "title": temp_title + "_MOD",
        "introduction": "更新描述",
    }, headers=admin_auth_headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["code"] == 0

    # 4. 删除歌单
    del_res = await async_client.delete(f"/admin/deletePlaylist/{playlist_id}", headers=admin_auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["code"] == 0
    assert del_res.json()["message"] == "删除成功"

# ==================== 6. 轮播图与反馈管理测试 ====================

@pytest.mark.asyncio
async def test_admin_banners_and_feedbacks(async_client: AsyncClient, admin_auth_headers: dict[str, str]):
    """测试轮播图和反馈管理接口"""
    # 轮播图列表
    banner_res = await async_client.post("/admin/getAllBanners", json={"pageNum": 1, "pageSize": 5}, headers=admin_auth_headers)
    assert banner_res.status_code == 200
    assert banner_res.json()["code"] == 0

    # 反馈列表
    feedback_res = await async_client.post("/admin/getAllFeedbacks", json={"pageNum": 1, "pageSize": 5}, headers=admin_auth_headers)
    assert feedback_res.status_code == 200
    assert feedback_res.json()["code"] == 0

    # 管理端测试接口
    test_res = await async_client.get("/admin/get", headers=admin_auth_headers)
    assert test_res.status_code == 200
    assert test_res.json()["code"] == 0

# ==================== 7. 批量删除与文件上传测试 ====================

@pytest.mark.asyncio
async def test_admin_batch_operations_and_uploads(async_client: AsyncClient, admin_auth_headers: dict[str, str], monkeypatch):
    """测试批量删除与文件上传接口 (使用 Mock 隔离外部 MinIO 网络 IO)"""
    # Mock upload_file and delete_file to ensure deterministic test without requiring live S3 server
    monkeypatch.setattr("app.api.admin.upload_file", lambda file, folder: f"http://127.0.0.1:9000/vibe-music-data/{folder}/mocked-file.png")
    monkeypatch.setattr("app.services.artist_service.delete_file", lambda url: None)
    monkeypatch.setattr("app.services.song_service.delete_file", lambda url: None)
    monkeypatch.setattr("app.services.playlist_service.delete_file", lambda url: None)
    monkeypatch.setattr("app.services.banner_service.delete_file", lambda url: None)

    # 1. 上传轮播图
    files = {"banner": ("test_banner.png", b"fake image bytes", "image/png")}
    add_banner_res = await async_client.post("/admin/addBanner", files=files, headers=admin_auth_headers)
    assert add_banner_res.status_code == 200
    assert add_banner_res.json()["code"] == 0
    assert add_banner_res.json()["message"] == "添加成功"

    # 查出刚新增的轮播图
    banners_res = await async_client.post("/admin/getAllBanners", json={"pageNum": 1, "pageSize": 1}, headers=admin_auth_headers)
    banner_id = banners_res.json()["data"]["items"][0]["bannerId"]

    # 2. 更新轮播图图片
    update_banner_res = await async_client.post(f"/admin/updateBanner/{banner_id}", files={"banner": ("upd.png", b"new bytes", "image/png")}, headers=admin_auth_headers)
    assert update_banner_res.status_code == 200
    assert update_banner_res.json()["code"] == 0

    # 3. 批量删除轮播图
    del_banners_res = await async_client.request("DELETE", "/admin/deleteBanners", json=[banner_id], headers=admin_auth_headers)
    assert del_banners_res.status_code == 200
    assert del_banners_res.json()["code"] == 0
    assert del_banners_res.json()["message"] == "删除成功"

    # 4. 新增两个临时歌手并批量删除
    uid = uuid.uuid4().hex[:6]
    await async_client.post("/admin/addArtist", json={"artistName": f"批量A_{uid}", "gender": 0}, headers=admin_auth_headers)
    await async_client.post("/admin/addArtist", json={"artistName": f"批量B_{uid}", "gender": 1}, headers=admin_auth_headers)
    q1 = await async_client.post("/admin/getAllArtists", json={"pageNum": 1, "pageSize": 1, "artistName": f"批量A_{uid}"}, headers=admin_auth_headers)
    q2 = await async_client.post("/admin/getAllArtists", json={"pageNum": 1, "pageSize": 1, "artistName": f"批量B_{uid}"}, headers=admin_auth_headers)
    aid1 = q1.json()["data"]["items"][0]["artistId"]
    aid2 = q2.json()["data"]["items"][0]["artistId"]

    # 测试修改歌手头像
    upd_avatar_res = await async_client.patch(f"/admin/updateArtistAvatar/{aid1}", files={"avatar": ("avatar.png", b"avatar bytes", "image/png")}, headers=admin_auth_headers)
    assert upd_avatar_res.status_code == 200
    assert upd_avatar_res.json()["code"] == 0

    del_artists_res = await async_client.request("DELETE", "/admin/deleteArtists", json=[aid1, aid2], headers=admin_auth_headers)
    assert del_artists_res.status_code == 200
    assert del_artists_res.json()["code"] == 0
    assert del_artists_res.json()["message"] == "删除成功"

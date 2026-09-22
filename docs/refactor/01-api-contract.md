# 01 - API 完整契约清单 (API Contract)

> ⚠️ **铁律**：所有 HTTP 响应状态码除非鉴权失败（401/403），其余业务逻辑统一返回 `HTTP 200`，业务状态由响应体中的 `code` 区分（`0`=成功，`1`=失败）。

---

## 1. 统一响应与分页包装

### 1.1 通用响应包结构 `Result<T>`
```json
{
  "code": 0,          // 0 为成功，1 为业务异常/失败
  "message": "操作成功", // 提示信息
  "data": {}          // 具体业务数据，成功时可为 Object/Array/String/null；失败时为 null
}
```

### 1.2 通用分页结构 `PageResult<T>`
```json
{
  "total": 120,       // 总条数 (Long / int)
  "items": []         // 当前页数据列表 (List<T>)，无数据时为空列表 []，不要传 null
}
```

---

## 2. 用户端认证与信息模块 (User & Auth)

### 2.1 用户登录
- **URL**: `POST /user/login`
- **权限**: 公开 (Public)
- **Content-Type**: `application/json`
- **请求 Body**:
  ```json
  {
    "email": "user@example.com",     // 必填，邮箱格式
    "password": "Password123"        // 必填，8-18位数字/字母/符号组合
  }
  ```
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "登录成功",
    "data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." // String Token
  }
  ```
- **失败响应**:
  ```json
  { "code": 1, "message": "邮箱错误" / "密码错误" / "账号已被锁定", "data": null }
  ```

### 2.2 获取当前登录用户信息
- **URL**: `GET /user/getUserInfo`
- **权限**: 需要登录 (ROLE_USER)，请求头带 `Authorization: Bearer <token>`
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "操作成功",
    "data": {
      "userId": 1,
      "username": "kevin",
      "phone": "13800000000",
      "email": "user@example.com",
      "userAvatar": "http://localhost:9000/vibe-music-data/avatar.jpg",
      "introduction": "热爱音乐",
      "createTime": "2025-01-01 12:00:00",
      "updateTime": "2025-01-01 12:00:00",
      "userStatus": 0
    }
  }
  ```

---

## 3. 歌曲模块 (Song)

### 3.1 获取推荐歌曲
- **URL**: `GET /song/getRecommendedSongs`
- **权限**: 公开 (Public)，若携带 Token 会在返回中计算 `likeStatus` (0-未喜欢，1-已喜欢)
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "操作成功",
    "data": [
      {
        "songId": 1,
        "songName": "晴天",
        "artistName": "周杰伦",
        "album": "叶惠美",
        "duration": "04:29",
        "coverUrl": "http://...",
        "audioUrl": "http://...",
        "likeStatus": 0,
        "releaseTime": "2003-07-31"
      }
    ]
  }
  ```

### 3.2 分页获取歌曲列表（歌曲库/搜索）
- **URL**: `POST /song/getAllSongs`
- **权限**: 公开 (Public)
- **请求 Body**:
  ```json
  {
    "pageNum": 1,
    "pageSize": 20,
    "songName": "关键词", // 可选
    "style": "流行"       // 可选
  }
  ```
- **成功响应**: `Result<PageResult<SongVO>>`

### 3.3 获取歌曲详情
- **URL**: `GET /song/getSongDetail/{id}`
- **权限**: 公开 (Public)
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "操作成功",
    "data": {
      "songId": 1,
      "songName": "晴天",
      "artistName": "周杰伦",
      "album": "叶惠美",
      "lyric": "[00:00.00] 晴天 - 周杰伦...",
      "duration": "04:29",
      "coverUrl": "http://...",
      "audioUrl": "http://...",
      "likeStatus": 0,
      "releaseTime": "2003-07-31"
    }
  }
  ```

---

## 4. 歌手模块 (Artist)

### 4.1 分页获取歌手列表
- **URL**: `POST /artist/getAllArtists`
- **权限**: 公开 (Public)
- **请求 Body**:
  ```json
  {
    "pageNum": 1,
    "pageSize": 20,
    "artistName": "周杰伦", // 可选
    "gender": 0,          // 可选：0-男，1-女，2-组合
    "area": "中国台湾"     // 可选
  }
  ```
- **成功响应**: `Result<PageResult<ArtistVO>>`

### 4.2 获取歌手详情及作品
- **URL**: `GET /artist/getArtistDetail/{id}`
- **权限**: 公开 (Public)
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "操作成功",
    "data": {
      "artistId": 1,
      "artistName": "周杰伦",
      "avatar": "http://...",
      "birth": "1979-01-18",
      "area": "中国台湾",
      "introduction": "华语流行男歌手...",
      "songs": [ /* Song 实体列表 */ ]
    }
  }
  ```

---

## 5. 歌单模块 (Playlist)

### 5.1 获取推荐歌单
- **URL**: `GET /playlist/getRecommendedPlaylists`
- **权限**: 公开 (Public)
- **成功响应**: `Result<List<PlaylistVO>>`

### 5.2 获取所有歌单（歌单广场）
- **URL**: `POST /playlist/getAllPlaylists`
- **权限**: 公开 (Public)
- **请求 Body**:
  ```json
  {
    "pageNum": 1,
    "pageSize": 20,
    "title": "流行", // 可选
    "style": "华语"  // 可选
  }
  ```
- **成功响应**: `Result<PageResult<Playlist>>`

### 5.3 获取歌单详情
- **URL**: `GET /playlist/getPlaylistDetail/{id}`
- **权限**: 公开 (Public)
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "操作成功",
    "data": {
      "playlistId": 1,
      "title": "经典华语流行",
      "coverUrl": "http://...",
      "introduction": "收录经典...",
      "songs": [ /* 歌曲列表 */ ],
      "comments": [],
      "likeStatus": 0,
      "isCollected": false
    }
  }
  ```

---

## 6. 收藏模块 (Favorite)

- **权限**: 需要登录 (ROLE_USER)

| 接口说明 | Method | Path | 参数形式 | 参数字段 | 成功返回 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 获取收藏歌单 | `POST` | `/favorite/getFavoritePlaylists` | JSON Body | `{ pageNum, pageSize }` | `PageResult<Playlist>` |
| 获取收藏歌曲 | `POST` | `/favorite/getFavoriteSongs` | JSON Body | `{ pageNum, pageSize, songName }` | `PageResult<SongVO>` |
| 收藏歌曲 | `POST` | `/favorite/collectSong` | Query Param | `songId=123` | `data: null, message: "收藏成功"` |
| 取消收藏歌曲 | `DELETE` | `/favorite/cancelCollectSong` | Query Param | `songId=123` | `data: null, message: "已取消收藏"` |
| 收藏歌单 | `POST` | `/favorite/collectPlaylist` | Query Param | `playlistId=123` | `data: null, message: "收藏成功"` |
| 取消收藏歌单 | `DELETE` | `/favorite/cancelCollectPlaylist` | Query Param | `playlistId=123` | `data: null, message: "已取消收藏"` |

---

## 7. 轮播图模块 (Banner)

- `GET /banner/getBannerList` (Public) -> 获取前台轮播图列表 `Result<List<BannerVO>>`

---

## 8. 管理后台模块 (Admin Endpoints)

> 必须携带拥有 `ROLE_ADMIN` 的 JWT Token。

### 8.1 管理员鉴权
- `POST /admin/login` -> Body: `{ username, password }` -> 返回 `Result<String>` (Token)
- `POST /admin/logout` -> Header `Authorization` -> 返回 `Result.success()`

### 8.2 仪表盘统计
- `GET /admin/getAllUsersCount` -> `Result<Long>`
- `GET /admin/getAllArtistsCount?gender=&area=` -> `Result<Long>`
- `GET /admin/getAllSongsCount?style=` -> `Result<Long>`
- `GET /admin/getAllPlaylistsCount?style=` -> `Result<Long>`

### 8.3 用户管理
- `POST /admin/getAllUsers` -> Body: `{ pageNum, pageSize, username, phone, userStatus }` -> `PageResult<UserManagementVO>`
- `POST /admin/addUser` -> Body: `{ username, password, phone, email, introduction }`
- `PUT /admin/updateUser` -> Body: `{ userId, username, phone, email, introduction, userStatus }`
- `PATCH /admin/updateUserStatus/{id}/{status}` -> Path params
- `DELETE /admin/deleteUser/{id}` -> Path param
- `DELETE /admin/deleteUsers` -> Body: `[1, 2, 3]`

### 8.4 歌手管理
- `POST /admin/getAllArtists` -> Body: `ArtistDTO` -> `PageResult<Artist>`
- `POST /admin/addArtist` -> Body: `ArtistDTO`
- `PUT /admin/updateArtist` -> Body: `ArtistUpdateDTO`
- `PATCH /admin/updateArtistAvatar/{id}` -> Multipart file `avatar`
- `DELETE /admin/deleteArtist/{id}`
- `DELETE /admin/deleteArtists` -> Body: `[1, 2, 3]`

### 8.5 歌曲管理
- `GET /admin/getAllArtistNames` -> `Result<List<ArtistNameVO>>`
- `POST /admin/getAllSongsByArtist` -> Body: `{ pageNum, pageSize, artistId, songName }` -> `PageResult<SongAdminVO>`
- `POST /admin/addSong` -> Body: `SongAddDTO`
- `PUT /admin/updateSong` -> Body: `SongUpdateDTO`
- `PATCH /admin/updateSongCover/{id}` -> Multipart file `cover`
- `PATCH /admin/updateSongAudio/{id}` -> Multipart file `audio`
- `DELETE /admin/deleteSong/{id}`
- `DELETE /admin/deleteSongs` -> Body: `[1, 2, 3]`

### 8.6 歌单管理
- `POST /admin/getAllPlaylists` -> Body: `PlaylistDTO` -> `PageResult<Playlist>`
- `POST /admin/addPlaylist` -> Body: `PlaylistAddDTO`
- `PUT /admin/updatePlaylist` -> Body: `PlaylistUpdateDTO`
- `PATCH /admin/updatePlaylistCover/{id}` -> Multipart file `cover`
- `DELETE /admin/deletePlaylist/{id}`
- `DELETE /admin/deletePlaylists` -> Body: `[1, 2, 3]`

### 8.7 轮播图管理
- `POST /admin/getAllBanners` -> Body: `BannerDTO` -> `PageResult<Banner>`
- `POST /admin/addBanner` -> Multipart file `banner`
- `POST /admin/updateBanner/{id}` -> Multipart file `banner`
- `PATCH /admin/updateBannerStatus/{id}?status=0` -> Param status
- `DELETE /admin/deleteBanner/{id}`
- `DELETE /admin/deleteBanners` -> Body: `[1, 2, 3]`

### 8.8 反馈管理
- `POST /admin/getAllFeedbacks` -> Body: `FeedbackDTO` -> `PageResult<Feedback>`
- `DELETE /admin/deleteFeedback/{id}`
- `DELETE /admin/deleteFeedbacks` -> Body: `[1, 2, 3]`

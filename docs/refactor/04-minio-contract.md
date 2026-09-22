# 04 - MinIO 对象存储与媒体流契约 (MinIO Contract)

> ⚠️ **存储路径与 URL 规范**：
> 保持与 Java 服务完全一致的 Bucket、文件目录分类和 Object Key 命名规则，保证历史音频与图片无缝访问。

---

## 1. MinIO 基础配置

- **Bucket 名称**：`vibe-music-data`
- **默认访问 Endpoint**：`http://localhost:9000`（或由环境变量 `MINIO_ENDPOINT` 覆盖）
- **公开策略**：Bucket 设置为公开只读（Public Read），前端直接通过 HTTP GET 请求静态资源。

---

## 2. 目录规范与 Object Key 生成规则

所有上传资源统一使用：
$$\text{ObjectKey} = \text{folder} + \text{"/"} + \text{UUID} + \text{"-"} + \text{original\_filename}$$

### 2.1 目录划分
| 业务类型 | 存储目录 (folder) | 示例 Object Key | 说明 |
| :--- | :--- | :--- | :--- |
| 轮播图 | `banners` | `banners/9b1deb4d-...-banner1.jpg` | 首页运营 Banner 图 |
| 歌手头像 | `artists` | `artists/98b29849-...-artist.png` | 歌手头像写真 |
| 歌曲封面 | `songCovers` | `songCovers/a1b2c3d4-...-cover.jpg` | 单曲封面 |
| 歌曲音频 | `songs` | `songs/e5f6g7h8-...-song.mp3` | MP3/FLAC 音频流媒体文件 |
| 歌单封面 | `playlists` | `playlists/f1e2d3c4-...-playlist.jpg` | 歌单展示封面 |

---

## 3. URL 构造与删除提取规则

### 3.1 上传返回 URL
```python
file_url = f"{endpoint}/{bucket_name}/{object_key}"
```
**示例**：
`http://localhost:9000/vibe-music-data/songs/e5f6g7h8-9a0b-1c2d-3e4f-5a6b7c8d9e0f-晴天.mp3`

### 3.2 删除文件提取 Object Key
```python
object_key = file_url.replace(f"{endpoint}/{bucket_name}/", "")
minio_client.remove_object(bucket_name, object_key)
```

---

## 4. 音频播放与 HTTP 206 Range 支持

- **播放方式**：前端 `Audio` 标签通过 `audioUrl` 直接向 MinIO / Nginx 发起请求。
- **拖动进度条**：浏览器通过 `Range: bytes=start-end` 请求音频分片，MinIO 原生支持 `206 Partial Content`，无需经过 FastAPI 代理。

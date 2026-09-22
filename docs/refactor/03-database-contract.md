# 03 - 数据库表结构与 ORM 映射契约 (Database Contract)

> ⚠️ **数据零破坏原则**：
> 1. 完全沿用现有 MySQL 数据库 `vibe_music` 和已有的 `tb_*` 物理表结构。
> 2. 第一阶段**严禁任何 DDL 变更**，严禁使用 Alembic 执行 drop / alter 等破坏性迁移。
> 3. SQLAlchemy 2.0 中的 Model 严格映射物理字段名。

---

## 1. 核心表结构映射字典

### 1.1 `tb_admin`（管理员表）
| MySQL 字段 | 类型 | 约束 | Java 实体属性 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK, AUTO_INCREMENT | `adminId` | 管理员 ID |
| `username` | `VARCHAR(20)` | UNIQUE, NOT NULL | `username` | 管理员用户名 |
| `password` | `VARCHAR(64)` | NOT NULL | `password` | MD5 密码 (32位 hex) |

### 1.2 `tb_user`（用户表）
| MySQL 字段 | 类型 | 约束 | Java 实体属性 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK, AUTO_INCREMENT | `userId` | 用户 ID |
| `username` | `VARCHAR(20)` | NOT NULL | `username` | 用户名 |
| `password` | `VARCHAR(64)` | NOT NULL | `password` | MD5 密码 (32位 hex) |
| `phone` | `VARCHAR(20)` | NULL | `phone` | 手机号 |
| `email` | `VARCHAR(50)` | UNIQUE, NOT NULL | `email` | 邮箱 |
| `user_avatar` | `VARCHAR(255)` | NULL | `userAvatar` | 用户头像 MinIO URL |
| `introduction`| `VARCHAR(255)` | NULL | `introduction` | 个人简介 |
| `create_time` | `DATETIME` | NULL | `createTime` | 注册时间 |
| `update_time` | `DATETIME` | NULL | `updateTime` | 更新时间 |
| `status` | `INT` | DEFAULT 0 | `userStatus` | 0-启用, 1-禁用 |

### 1.3 `tb_artist`（歌手表）
| MySQL 字段 | 类型 | 约束 | Java 实体属性 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK, AUTO_INCREMENT | `artistId` | 歌手 ID |
| `name` | `VARCHAR(100)` | NOT NULL | `artistName` | 歌手姓名 |
| `gender` | `INT` | NULL | `gender` | 0-男, 1-女, 2-组合 |
| `avatar` | `VARCHAR(255)` | NULL | `avatar` | 头像 MinIO URL |
| `birth` | `DATE` | NULL | `birth` | 出生日期 (`YYYY-MM-DD`) |
| `area` | `VARCHAR(30)` | NULL | `area` | 所属地区/国籍 |
| `introduction`| `VARCHAR(255)` | NULL | `introduction` | 歌手简介 |

### 1.4 `tb_song`（歌曲表）
| MySQL 字段 | 类型 | 约束 | Java 实体属性 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK, AUTO_INCREMENT | `songId` | 歌曲 ID |
| `artist_id` | `BIGINT` | NULL | `artistId` | 关联歌手 ID |
| `name` | `VARCHAR(255)` | NOT NULL | `songName` | 歌曲名 |
| `album` | `VARCHAR(255)` | NULL | `album` | 专辑名 |
| `lyric` | `TEXT` | NULL | `lyric` | LRC 歌词文本 |
| `duration` | `VARCHAR(20)` | NULL | `duration` | 时长 (如 `03:45`) |
| `style` | `VARCHAR(50)` | NULL | `style` | 曲风风格 |
| `cover_url` | `VARCHAR(255)` | NULL | `coverUrl` | 封面图 MinIO URL |
| `audio_url` | `VARCHAR(255)` | NULL | `audioUrl` | 音频流 MinIO URL |
| `release_time`| `DATE` | NULL | `releaseTime` | 发行日期 (`YYYY-MM-DD`) |

### 1.5 `tb_playlist`（歌单表）
| MySQL 字段 | 类型 | 约束 | Java 实体属性 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK, AUTO_INCREMENT | `playlistId` | 歌单 ID |
| `title` | `VARCHAR(100)` | NOT NULL | `title` | 歌单标题 |
| `cover_url` | `VARCHAR(255)` | NULL | `coverUrl` | 歌单封面 MinIO URL |
| `introduction`| `VARCHAR(255)` | NULL | `introduction` | 歌单简介 |
| `style` | `VARCHAR(50)` | NULL | `style` | 歌单分类风格 |

### 1.6 `tb_banner`（轮播图表）
| MySQL 字段 | 类型 | 约束 | Java 实体属性 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK, AUTO_INCREMENT | `bannerId` | 轮播图 ID |
| `banner_url` | `VARCHAR(255)` | NOT NULL | `bannerUrl` | 图片 MinIO URL |
| `status` | `INT` | DEFAULT 0 | `bannerStatus` | 0-启用, 1-禁用 |

### 1.7 `tb_user_favorite`（用户收藏关联表）
| MySQL 字段 | 类型 | 约束 | Java 实体属性 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK, AUTO_INCREMENT | `userFavoriteId` | 主键 ID |
| `user_id` | `BIGINT` | NOT NULL | `userId` | 用户 ID |
| `type` | `INT` | NOT NULL | `type` | 0-歌曲收藏, 1-歌单收藏 |
| `song_id` | `BIGINT` | NULL | `songId` | 收藏歌曲 ID (type=0) |
| `playlist_id`| `BIGINT` | NULL | `playlistId` | 收藏歌单 ID (type=1) |
| `create_time` | `DATETIME` | NULL | `createTime` | 收藏时间 |

### 1.8 `tb_feedback`（用户反馈表）
| MySQL 字段 | 类型 | 约束 | Java 实体属性 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK, AUTO_INCREMENT | `feedbackId` | 反馈 ID |
| `user_id` | `BIGINT` | NOT NULL | `userId` | 用户 ID |
| `feedback` | `TEXT` | NOT NULL | `feedback` | 反馈内容 |
| `create_time` | `DATETIME` | NULL | `createTime` | 提交时间 |

### 1.9 `tb_genre` & `tb_style`（风格标签表）
- `tb_style`: `id` (PK), `name` (VARCHAR)
- `tb_genre`: `song_id` (PK/FK), `style_id` (FK)

---

## 2. SQLAlchemy 2.0 异步 Model 示例定义

```python
from datetime import date, datetime
from sqlalchemy import BigInteger, String, Integer, Text, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "tb_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    introduction: Mapped[str | None] = mapped_column(String(255), nullable=True)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=0)
```

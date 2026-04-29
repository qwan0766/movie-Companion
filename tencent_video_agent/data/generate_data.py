"""
腾讯视频模拟数据生成脚本
=======================
生成 ~100 条视频数据及关联的演员、导演、分类数据，输出为多文件关联式 JSON。

用法: python data/generate_data.py
输出: data/videos.json, data/actors.json, data/directors.json, data/categories.json
"""

import json
import os
import random
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# ── 常量配置 ──────────────────────────────────────────────────────────

SEED = 42
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 枚举定义 ──────────────────────────────────────────────────────────


class VideoType(str, Enum):
    MOVIE = "movie"
    TV = "tv"
    VARIETY = "variety"
    ANIMATION = "animation"
    DOCUMENTARY = "documentary"


class VideoStatus(str, Enum):
    COMPLETED = "completed"
    ONGOING = "ongoing"
    UPCOMING = "upcoming"


# ── Pydantic 模型 ────────────────────────────────────────────────────


class Category(BaseModel):
    category_id: str
    name: str
    description: str


class Actor(BaseModel):
    actor_id: str
    name: str
    gender: str
    birth_year: int
    nationality: str
    bio: str
    avatar_url: str
    popularity: int = Field(ge=1, le=100)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        assert v in ("male", "female"), "gender must be male or female"
        return v


class Director(BaseModel):
    director_id: str
    name: str
    birth_year: int
    nationality: str
    bio: str
    avatar_url: str
    popularity: int = Field(ge=1, le=100)


class Video(BaseModel):
    video_id: str
    title: str
    original_title: Optional[str] = None
    description: str
    year: int = Field(ge=2000, le=2026)
    region: str
    language: str
    type: VideoType
    genres: list[str]
    rating: float = Field(ge=1.0, le=10.0)
    vote_count: int = Field(ge=1000)
    episode_count: Optional[int] = None
    duration: Optional[int] = None
    status: VideoStatus
    poster_url: str = ""
    director_ids: list[str] = Field(default_factory=list)
    actor_ids: list[str] = Field(default_factory=list)


# ── 数据池 ────────────────────────────────────────────────────────────

CATEGORIES_POOL = [
    Category(category_id="c_01", name="喜剧", description="轻松搞笑类"),
    Category(category_id="c_02", name="动作", description="激烈打斗/动作场面"),
    Category(category_id="c_03", name="科幻", description="科幻幻想类"),
    Category(category_id="c_04", name="爱情", description="浪漫爱情类"),
    Category(category_id="c_05", name="悬疑", description="悬疑推理类"),
    Category(category_id="c_06", name="剧情", description="剧情片"),
    Category(category_id="c_07", name="古装", description="古装历史类"),
    Category(category_id="c_08", name="奇幻", description="奇幻魔法类"),
    Category(category_id="c_09", name="犯罪", description="犯罪警匪类"),
    Category(category_id="c_10", name="恐怖", description="恐怖惊悚类"),
    Category(category_id="c_11", name="战争", description="战争题材"),
    Category(category_id="c_12", name="动画", description="动画类"),
    Category(category_id="c_13", name="纪录片", description="纪实类"),
    Category(category_id="c_14", name="真人秀", description="真人秀综艺"),
    Category(category_id="c_15", name="脱口秀", description="脱口秀节目"),
]

# 演员池（姓名, 性别, 出生年, 国籍）
ACTOR_POOL = [
    ("张毅", "male", 1978, "中国大陆"),
    ("武京", "male", 1974, "中国大陆"),
    ("沈东", "male", 1979, "中国大陆"),
    ("黄波", "male", 1974, "中国大陆"),
    ("刘浩", "male", 1961, "中国香港"),
    ("梁威", "male", 1962, "中国香港"),
    ("陈龙", "male", 1954, "中国香港"),
    ("葛兰", "male", 1957, "中国大陆"),
    ("陈明", "male", 1955, "中国大陆"),
    ("王强", "male", 1984, "中国大陆"),
    ("徐峥", "male", 1972, "中国大陆"),
    ("黄宣", "male", 1985, "中国大陆"),
    ("朱峰", "male", 1988, "中国大陆"),
    ("易洋", "male", 2000, "中国大陆"),
    ("王一", "male", 1997, "中国大陆"),
    ("肖展", "male", 1991, "中国大陆"),
    ("邓超", "male", 1979, "中国大陆"),
    ("陈昆", "male", 1976, "中国大陆"),
    ("刘华", "male", 1978, "中国大陆"),
    ("段宏", "male", 1973, "中国大陆"),
    ("张云", "male", 1988, "中国大陆"),
    ("白羽", "male", 1990, "中国大陆"),
    ("雷音", "male", 1979, "中国大陆"),
    ("于伟", "male", 1971, "中国大陆"),
    ("张文", "male", 1976, "中国大陆"),
    ("王春", "male", 1973, "中国大陆"),
    ("廖帆", "male", 1974, "中国大陆"),
    ("黄宇", "male", 1992, "中国大陆"),
    ("李贤", "male", 1991, "中国大陆"),
    ("周讯", "female", 1974, "中国大陆"),
    ("章怡", "female", 1979, "中国大陆"),
    ("杨蜜", "female", 1986, "中国大陆"),
    ("赵颖", "female", 1987, "中国大陆"),
    ("刘菲", "female", 1987, "中国大陆"),
    ("孙丽", "female", 1982, "中国大陆"),
    ("汤薇", "female", 1979, "中国大陆"),
    ("姚晨", "female", 1979, "中国大陆"),
    ("白荷", "female", 1984, "中国大陆"),
    ("马纯", "female", 1988, "中国大陆"),
    ("周雨", "female", 1992, "中国大陆"),
    ("杨紫", "female", 1992, "中国大陆"),
    ("迪巴", "female", 1992, "中国大陆"),
    ("古扎", "female", 1992, "中国大陆"),
    ("关彤", "female", 1997, "中国大陆"),
    ("张枫", "female", 2001, "中国大陆"),
    ("刘存", "female", 2000, "中国大陆"),
    ("倪妮", "female", 1988, "中国大陆"),
    ("宋佳", "female", 1980, "中国大陆"),
    ("袁泉", "female", 1977, "中国大陆"),
    ("谭卓", "female", 1987, "中国大陆"),
    ("海清", "female", 1977, "中国大陆"),
    ("殷桃", "female", 1979, "中国大陆"),
    ("刘桃", "female", 1978, "中国大陆"),
    ("全智", "female", 1981, "韩国"),
    ("金秀", "male", 1988, "韩国"),
    ("宋康", "male", 1967, "韩国"),
    ("小李", "male", 1974, "美国"),
    ("汤姆", "male", 1962, "美国"),
    ("凯特", "female", 1975, "美国"),
    ("渡边", "male", 1959, "日本"),
]

# 导演池（姓名, 出生年, 国籍）
DIRECTOR_POOL = [
    ("郭凡", 1980, "中国大陆"),
    ("陈歌", 1970, "中国大陆"),
    ("宁昊", 1977, "中国大陆"),
    ("徐克", 1950, "中国香港"),
    ("王家", 1958, "中国香港"),
    ("张谋", 1950, "中国大陆"),
    ("冯刚", 1958, "中国大陆"),
    ("姜文", 1963, "中国大陆"),
    ("陈凯", 1952, "中国大陆"),
    ("吴晶", 1974, "中国大陆"),
    ("贾玲", 1982, "中国大陆"),
    ("韩延", 1983, "中国大陆"),
    ("路扬", 1986, "中国大陆"),
    ("文牧", 1985, "中国大陆"),
    ("大鹏", 1982, "中国大陆"),
    ("饺饵", 1980, "中国大陆"),
    ("刘循", 1986, "中国大陆"),
    ("五百", 1980, "中国大陆"),
    ("费振", 1983, "中国大陆"),
    ("孙皓", 1980, "中国大陆"),
    ("克里斯", 1970, "美国"),
    ("诺兰", 1970, "英国"),
    ("奉昊", 1969, "韩国"),
    ("宫崎", 1941, "日本"),
    ("斯皮", 1946, "美国"),
    ("詹姆斯", 1954, "美国"),
    ("丹尼", 1971, "英国"),
    ("是枝", 1962, "日本"),
    ("新海", 1973, "日本"),
    ("温仁", 1977, "马来西亚"),
]

# ── 视频标题池 ────────────────────────────────────────────────────────

MOVIE_TITLES = [
    ("星际探索", "Interstellar Quest"),
    ("龙虎风云", "Dragon Storm"),
    ("笑傲江湖之剑气冲霄", "Swordsman: Rising Sword"),
    ("暗夜追踪", "Night Chase"),
    ("流浪星辰", "Wandering Star"),
    ("长津湖之水门桥", "Battle at Frozen Lake"),
    ("你好夏洛", "Hello, Xia Luo"),
    ("唐人街谜案", "Chinatown Mystery"),
    ("我不是药神", "I Am Not the Medicine God"),
    ("哪吒之魔童降世", "Nezha: Birth of the Demon Child"),
    ("满江红", "Full River Red"),
    ("消失的她", "The Vanished Her"),
    ("孤注一掷", "All or Nothing"),
    ("封神第一部", "Creation of the Gods I"),
    ("人生大事", "Life Events"),
    ("独行月球", "The Lone Moon"),
    ("奇迹笨小孩", "Miracle: The Fool Kid"),
    ("飞驰人生", "Pegasus"),
    ("这个杀手不太冷静", "Too Cool to Kill"),
    ("狙击手", "Sniper"),
    ("怒火重案", "Raging Fire"),
    ("悬崖之上", "Cliff Walkers"),
    ("拆弹专家", "Shock Wave"),
    ("明日战记", "Warriors of Future"),
    ("反贪风暴", "G Storm"),
    ("扫黑行动", "The Black Storm"),
    ("万里归途", "Home Coming"),
    ("平凡英雄", "Ordinary Hero"),
    ("妈妈", "Song of Spring"),
    ("海的尽头是草原", "The Sea Beyond"),
    ("隐入尘烟", "Return to Dust"),
    ("爱情神话", "B for Busy"),
    ("穿过寒冬拥抱你", "Embrace Winter"),
    ("检察风云", "The Procurator"),
    ("热带往事", "Are You Lonesome Tonight"),
    ("刺杀小说家", "A Writer's Odyssey"),
    ("我在时间尽头等你", "Love in Time"),
    ("温暖的抱抱", "Warm Hug"),
    ("紧急救援", "The Rescue"),
    ("夺冠", "Leap"),
]

TV_TITLES = [
    ("庆余年", "Joy of Life"),
    ("三体", "The Three-Body Problem"),
    ("狂飙", "The Knockout"),
    ("漫长的季节", "The Long Season"),
    ("繁花", "Blossoms Shanghai"),
    ("山海情", "Minning Town"),
    ("觉醒年代", "The Awakening Age"),
    ("人世间", "A Lifelong Journey"),
    ("琅琊榜", "Nirvana in Fire"),
    ("甄嬛传", "Empresses in the Palace"),
    ("都挺好", "All Is Well"),
    ("小舍得", "A Little Dilemma"),
    ("三十而已", "Nothing But Thirty"),
    ("欢乐颂", "Ode to Joy"),
    ("扶摇", "Legend of Fuyao"),
    ("苍兰诀", "Love Between Fairy and Devil"),
    ("星汉灿烂", "Love Like the Galaxy"),
    ("梦华录", "A Dream of Splendor"),
    ("开端", "Reset"),
    ("隐秘的角落", "The Bad Kids"),
    ("沉默的真相", "The Long Night"),
    ("白夜追凶", "Day and Night"),
    ("长安十二时辰", "The Longest Day in Chang'an"),
    ("陈情令", "The Untamed"),
    ("赘婿", "My Heroic Husband"),
]

VARIETY_TITLES = [
    ("奔跑吧青春", "Keep Running Youth"),
    ("向往的生活", "Back to Field"),
    ("明星大侦探", "Who's the Murderer"),
    ("乘风破浪", "Sisters Who Make Waves"),
    ("歌手2025", "Singer 2025"),
    ("舌尖上的旅行", "Flavors on the Road"),
    ("喜剧之王", "Comedy King"),
    ("演员请就位", "Actors Please Take Your Place"),
    ("我们的歌", "Our Song"),
    ("最强大脑", "The Brain"),
    ("密室大逃脱", "Great Escape"),
    ("哈哈哈哈哈", "Ha-ha-ha"),
    ("五十公里桃花坞", "50km to Paradise"),
    ("萌探探探案", "Super Detective"),
    ("了不起的挑战", "Great Challenge"),
]

ANIMATION_TITLES = [
    ("斗罗大陆", "Douluo Dalu"),
    ("凡人修仙传", "A Mortal's Journey to Immortality"),
    ("完美世界", "The Perfect World"),
    ("一念永恒", "A Will Eternal"),
    ("吞噬星空", "Swallowed Star"),
    ("仙逆", "Rebirth of the Immortal"),
    ("斗破苍穹", "Battle Through the Heavens"),
    ("武动乾坤", "Martial Universe"),
    ("狐妖小红娘", "Fox Spirit Matchmaker"),
    ("一人之下", "The Outcast"),
    ("时光代理人", "Link Click"),
    ("灵笼", "The Incantation"),
]

DOCUMENTARY_TITLES = [
    ("舌尖上的中国", "A Bite of China"),
    ("我在故宫修文物", "Masters in the Forbidden City"),
    ("大国崛起", "The Rise of Great Powers"),
    ("河西走廊", "The Hexi Corridor"),
    ("美丽中国", "Wild China"),
    ("航拍中国", "Aerial China"),
    ("人间世", "Life Matters"),
    ("二十二", "Twenty Two"),
]

# 视频简介模板片段
DESCRIPTION_TEMPLATES = [
    "讲述了一段跨越时空的感人故事，在命运的交织中，主人公们不断追寻着属于自己的答案。",
    "一场惊心动魄的正邪较量，正义与邪恶的边界在人性考验中逐渐模糊。",
    "改编自真实事件，展现普通人在极端困境下迸发出的非凡勇气与力量。",
    "以独特的视角切入当代都市生活，细腻描绘了年轻人的成长与蜕变。",
    "在宏大的历史背景下，小人物的命运与时代浪潮交织，谱写出一曲命运交响。",
    "一段跨越地域与文化的奇妙旅程，在欢笑与泪水中重新发现生活的意义。",
    "科幻与现实的交织，当人类面临前所未有的危机，希望是最后的武器。",
    "悬疑层层递进，每一个线索都指向一个令人震惊的真相。",
    "温暖治愈系作品，用最朴实的日常打动人心，让观众在平凡中看到不平凡。",
    "高燃动作场面与深刻人物刻画并重，为观众呈现一场视听盛宴。",
]

# ── 辅助函数 ──────────────────────────────────────────────────────────


def _make_avatar_url(entity_type: str, entity_id: str) -> str:
    """生成占位头像/海报 URL"""
    return f"https://placeholder.example/{entity_type}/{entity_id}.jpg"


def _make_bio(name: str, nationality: str, works_count: int) -> str:
    """生成人物简介"""
    templates = [
        f"{name}，出生于{nationality}，知名{works_count}部影视作品的主创人员，深受观众喜爱。",
        f"{name}，{nationality}著名影视人，参与创作{works_count}余部作品，演技备受好评。",
        f"{name}，实力派演员/导演，来自{nationality}，代表作累计{works_count}部，曾获多项大奖提名。",
    ]
    return random.choice(templates)


# ── 生成器函数 ────────────────────────────────────────────────────────


def generate_actors(rng: random.Random) -> list[Actor]:
    """生成演员数据"""
    actors: list[Actor] = []
    for i, (name, gender, birth_year, nationality) in enumerate(ACTOR_POOL, 1):
        actor = Actor(
            actor_id=f"a_{i:03d}",
            name=name,
            gender=gender,
            birth_year=birth_year,
            nationality=nationality,
            bio=_make_bio(name, nationality, rng.randint(5, 30)),
            avatar_url=_make_avatar_url("actor", f"a_{i:03d}"),
            popularity=rng.randint(30, 100),
        )
        actors.append(actor)
    return actors


def generate_directors(rng: random.Random) -> list[Director]:
    """生成导演数据"""
    directors: list[Director] = []
    for i, (name, birth_year, nationality) in enumerate(DIRECTOR_POOL, 1):
        director = Director(
            director_id=f"d_{i:03d}",
            name=name,
            birth_year=birth_year,
            nationality=nationality,
            bio=_make_bio(name, nationality, rng.randint(5, 25)),
            avatar_url=_make_avatar_url("director", f"d_{i:03d}"),
            popularity=rng.randint(30, 100),
        )
        directors.append(director)
    return directors


def _build_video(
    video_id: str,
    title: str,
    original_title: Optional[str],
    year: int,
    type_: VideoType,
    region: str,
    rng: random.Random,
    actors: list[Actor],
    directors: list[Director],
    categories: list[Category],
) -> Video:
    """构建单条视频数据"""

    # 根据类型确定字段
    is_movie = type_ == VideoType.MOVIE
    is_variety = type_ == VideoType.VARIETY
    is_doc = type_ == VideoType.DOCUMENTARY

    episode_count = None
    duration = None
    if is_movie:
        duration = rng.randint(90, 180)
    elif not is_variety:
        episode_count = rng.choice([12, 16, 24, 30, 36, 40, 48])
    else:
        episode_count = rng.choice([10, 12, 15, 20])

    # 语言
    region_language = {
        "中国大陆": "国语",
        "中国香港": "粤语",
        "美国": "英语",
        "英国": "英语",
        "韩国": "韩语",
        "日本": "日语",
    }
    language = region_language.get(region, "国语")

    # 评分
    base_rating = rng.uniform(6.0, 9.5)
    rating = round(base_rating, 1)

    # 评分人数
    vote_count = rng.randint(5000, 500000)

    # 选导演（1-2位）
    selected_directors = rng.sample(directors, rng.randint(1, 2))
    director_ids = [d.director_id for d in selected_directors]

    # 选演员（2-5位），优先同地区，不足时从其他地区补齐
    region_actors = [a for a in actors if a.nationality == region]
    other_actors = [a for a in actors if a.nationality != region]

    selected = []
    target_count = rng.randint(2, 4)

    if region_actors:
        take = min(target_count, len(region_actors))
        selected = list(rng.sample(region_actors, take))

    remaining = target_count - len(selected)
    if remaining > 0 and other_actors:
        extra = rng.sample(other_actors, min(remaining, len(other_actors)))
        selected.extend(extra)

    if not selected:
        # 极端 fallback：从所有演员中选
        selected = rng.sample(actors, min(target_count, len(actors)))

    rng.shuffle(selected)
    actor_ids = [a.actor_id for a in selected]

    # 选分类（1-3个）
    selected_cats = rng.sample(categories, rng.randint(1, 3))
    category_ids = [c.category_id for c in selected_cats]

    # genres（从分类名称映射）
    cat_map = {c.category_id: c.name for c in categories}
    genres = [cat_map[cid] for cid in category_ids]

    # 状态
    if year >= 2025:
        status = VideoStatus.UPCOMING if rng.random() < 0.3 else VideoStatus.ONGOING
    else:
        status = VideoStatus.COMPLETED

    description = rng.choice(DESCRIPTION_TEMPLATES)

    return Video(
        video_id=video_id,
        title=title,
        original_title=original_title,
        description=description,
        year=year,
        region=region,
        language=language,
        type=type_,
        genres=genres,
        rating=rating,
        vote_count=vote_count,
        episode_count=episode_count,
        duration=duration,
        status=status,
        poster_url=_make_avatar_url("video", video_id),
        director_ids=director_ids,
        actor_ids=actor_ids,
    )


def generate_videos(
    rng: random.Random,
    actors: list[Actor],
    directors: list[Director],
    categories: list[Category],
) -> list[Video]:
    """生成视频数据，按类型分布"""
    videos: list[Video] = []

    # 类型分布配置：(类型, 数量, 年份范围, 地区分布偏好)
    configs = [
        (VideoType.MOVIE, 40, (2000, 2026), ["中国大陆", "中国大陆", "中国大陆", "美国", "韩国"]),
        (VideoType.TV, 25, (2005, 2026), ["中国大陆", "中国大陆", "中国大陆", "韩国"]),
        (VideoType.VARIETY, 15, (2010, 2026), ["中国大陆"]),
        (VideoType.ANIMATION, 12, (2000, 2026), ["中国大陆", "中国大陆", "日本"]),
        (VideoType.DOCUMENTARY, 8, (2005, 2026), ["中国大陆", "中国大陆", "英国"]),
    ]

    title_counter = 0
    for type_, count, year_range, regions in configs:
        # 选定该类型的标题池
        if type_ == VideoType.MOVIE:
            titles = MOVIE_TITLES
        elif type_ == VideoType.TV:
            titles = TV_TITLES
        elif type_ == VideoType.VARIETY:
            titles = VARIETY_TITLES
        elif type_ == VideoType.ANIMATION:
            titles = ANIMATION_TITLES
        else:
            titles = DOCUMENTARY_TITLES

        # 如果标题不够，循环使用
        for i in range(count):
            title_idx = i % len(titles)
            title, orig = titles[title_idx]
            title_counter += 1
            video_id = f"v_{type_.value}_{title_counter:03d}"
            year = rng.randint(year_range[0], year_range[1])
            region = rng.choice(regions)

            video = _build_video(
                video_id=video_id,
                title=title,
                original_title=orig if rng.random() < 0.6 else None,
                year=year,
                type_=type_,
                region=region,
                rng=rng,
                actors=actors,
                directors=directors,
                categories=categories,
            )
            videos.append(video)

    return videos


def generate_all() -> tuple[list[Category], list[Actor], list[Director], list[Video]]:
    """生成全部数据"""
    rng = random.Random(SEED)

    categories = CATEGORIES_POOL
    actors = generate_actors(rng)
    directors = generate_directors(rng)
    videos = generate_videos(rng, actors, directors, categories)

    return categories, actors, directors, videos


# ── JSON 导出 ─────────────────────────────────────────────────────────


def export_to_json(data: list[BaseModel], filepath: str) -> str:
    """将 Pydantic 模型列表导出为 JSON 文件"""
    full_path = os.path.join(OUTPUT_DIR, filepath)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(
            [item.model_dump() for item in data],
            f,
            ensure_ascii=False,
            indent=2,
        )
    return full_path


def main() -> None:
    """一键生成全部 JSON 数据文件"""
    print("正在生成腾讯视频模拟数据...")
    categories, actors, directors, videos = generate_all()

    files = [
        ("categories.json", categories),
        ("actors.json", actors),
        ("directors.json", directors),
        ("videos.json", videos),
    ]

    for filename, data in files:
        path = export_to_json(data, filename)
        print(f"  [OK] 已生成: {path} ({len(data)} 条)")

    # 打印统计信息
    print("\n--- 数据统计 ---")
    print(f"  分类: {len(categories)} 个")
    print(f"  演员: {len(actors)} 位")
    print(f"  导演: {len(directors)} 位")
    print(f"  视频: {len(videos)} 条")
    type_counts = {}
    for v in videos:
        type_counts[v.type] = type_counts.get(v.type, 0) + 1
    for t, c in sorted(type_counts.items()):
        print(f"    {t.value}: {c} 条")
    print("数据生成完成！")


if __name__ == "__main__":
    main()

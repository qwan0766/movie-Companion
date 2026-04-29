# DESIGN.md - 腾讯视频智能观影助手（基于 awesome-design 大厂简约风格）

## 设计哲学（来自 awesome-design Concepts）
- 内容优先、极致简约、留白充足（参考 Brand Style Guide Examples）
- 参考标杆：腾讯视频 PC 端 + Material Design + 大厂简洁风格
- 关键词：干净、专业、沉浸式、卡片驱动、无多余装饰

## 颜色系统（来自 Color 章节）
- **主色**：#00A1D6（腾讯视频蓝，可从 Coolors / Brand Colors 调色板扩展）
- **辅助色**：#FF4B4B（活力红）、#00C853（成功绿）
- **中性色**：
    - 背景：#0F1117（深色大厂黑）
    - 表面/卡片：#1A1C23
    - 文字主色：#F0F2F5
    - 文字次色：#A0A3A8
- **工具推荐**（awesome-design）：
    - Coolors.co（快速生成配色）
    - Color Hunt（潮流调色板）
    - Brand Colors（官方品牌色参考）

## 排版规范（来自 Typography 章节）
- **字体栈**：PingFang SC / HarmonyOS Sans / system-ui / -apple-system / "Segoe UI"
- **推荐资源**（awesome-design）：
    - Google Fonts
    - Adobe Fonts
    - Butterick's Practical Typography（排版原则）
    - Typewolf（潮流字体搭配）
- **层级**：
    - 标题（H1）：28px / 600
    - 子标题（H2）：20px / 600
    - 正文：15-16px / 400
    - 辅助文字：13-14px / 400

## 图标与 Logo（来自 Icon and Logo 章节）
- **推荐资源**：
    - Material Design Icons（Google）
    - Font Awesome
    - Simple Icons（品牌图标）
    - Iconfont.cn（阿里矢量图标）
    - The Noun Project
- 使用原则：简洁线条图标，统一 24px 尺寸，与文字对齐

## 组件与布局规范（大厂简约风格）
**Movie Card**
- 圆角 12px
- 悬浮阴影（参考 Material Design）
- 海报 16:9 比例置顶
- Hover 效果：轻微上浮 + 阴影增强

**整体布局**
- 左侧 Sidebar（260px，深色 surface）
- 主内容区：聊天 + 推荐网格（st.columns 响应式）
- 大量留白（8px 倍数间距）

**按钮与交互**
- Primary 按钮使用腾讯蓝 #00A1D6
- Ghost 按钮透明边框
- 微交互：hover 亮度/位移变化

## Stock 图片资源（来自 Stock 章节）
- Unsplash、Pexels、Pixabay（高质量影视海报）
- 优先使用横版电影封面

## 实现提示（给 Agent / Streamlit 使用）
> 严格遵循 awesome-design 资源：使用 Coolors 配色、Material Icons、Google Fonts 排版，保持大厂深色简约风格，卡片悬浮、留白充足、内容（海报）优先。

---
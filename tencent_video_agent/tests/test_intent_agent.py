"""意图识别 Agent 单元测试"""

from agents.intent_agent import IntentAgent, _classify_intent


class TestClassifyIntent:
    """意图分类核心逻辑测试"""

    def test_find_movie_by_recommend(self):
        """推荐找片"""
        intent, conf, _ = _classify_intent("推荐几部好看的科幻电影")
        assert intent == "find_movie"
        assert conf >= 0.70

    def test_find_movie_what_to_watch(self):
        """有什么好看的"""
        intent, conf, _ = _classify_intent("最近有什么好看的电视剧吗")
        assert intent == "find_movie"
        assert conf >= 0.70

    def test_find_movie_by_genre(self):
        """按类型找片"""
        intent, conf, _ = _classify_intent("有没有动作片推荐")
        assert intent == "find_movie"
        assert conf >= 0.70

    def test_find_movie_want_to_watch(self):
        """想看"""
        intent, conf, _ = _classify_intent("我想看一部悬疑剧")
        assert intent == "find_movie"
        assert conf >= 0.70

    def test_ask_info_about_actor(self):
        """咨询演员信息"""
        intent, conf, _ = _classify_intent("介绍一下这个演员")
        assert intent == "ask_info"
        assert conf >= 0.70

    def test_ask_info_about_director(self):
        """咨询导演信息"""
        intent, conf, _ = _classify_intent("这个导演还拍过什么电影")
        assert intent == "ask_info"
        assert conf >= 0.70

    def test_ask_info_award(self):
        """咨询获奖信息"""
        intent, conf, _ = _classify_intent("这部电影获过什么奖")
        assert intent == "ask_info"
        assert conf >= 0.70

    def test_make_plan_weekend(self):
        """制定周末计划"""
        intent, conf, _ = _classify_intent("帮我规划周末看什么电影")
        assert intent == "make_plan"
        assert conf >= 0.70

    def test_make_plan_list(self):
        """制定清单"""
        intent, conf, _ = _classify_intent("帮我列个观影清单")
        assert intent == "make_plan"
        assert conf >= 0.70

    def test_chat_greeting(self):
        """问候"""
        intent, conf, _ = _classify_intent("你好")
        assert intent == "chat"
        assert conf >= 0.70

    def test_chat_thanks(self):
        """感谢"""
        intent, conf, _ = _classify_intent("谢谢")
        assert intent == "chat"
        assert conf >= 0.70

    def test_unknown_intent(self):
        """无法识别的意图"""
        intent, conf, _ = _classify_intent("今天天气真好")
        assert intent in ("chat", "unknown")  # chat or unknown

    def test_empty_text(self):
        """空文本"""
        intent, conf, _ = _classify_intent("")
        assert intent == "unknown"
        assert conf == 0.0

    def test_find_movie_new_releases(self):
        """最新影片"""
        intent, conf, _ = _classify_intent("最近新上映的电影有哪些")
        assert intent == "find_movie"
        assert conf >= 0.70

    def test_make_plan_tonight(self):
        """今晚计划"""
        intent, conf, _ = _classify_intent("今晚想看点什么好")
        assert intent == "make_plan"
        assert conf >= 0.70


class TestIntentAgent:
    """IntentAgent 整体测试"""

    def setup_method(self):
        self.agent = IntentAgent()

    def test_agent_name(self):
        assert self.agent.name == "intent_agent"

    def test_process_with_find_movie(self):
        result = self.agent.process({
            "messages": [{"role": "user", "content": "推荐一部科幻电影"}],
            "user_intent": "",
            "intent_confidence": 0.0,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert result["user_intent"] == "find_movie"
        assert result["intent_confidence"] >= 0.70
        assert result["next"] == "find_movie"

    def test_process_empty_messages(self):
        result = self.agent.process({
            "messages": [],
            "user_intent": "",
            "intent_confidence": 0.0,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert result["user_intent"] == "unknown"
        assert result["intent_confidence"] == 0.0

    def test_get_system_prompt(self):
        prompt = self.agent.get_system_prompt()
        assert "find_movie" in prompt
        assert "周星驰" in prompt

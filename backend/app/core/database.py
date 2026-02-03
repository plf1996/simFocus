from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


async def get_db() -> AsyncSession:
    """Dependency for getting async database session"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables and seed data"""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed template characters if table is empty
    from app.models.character import Character
    from sqlalchemy import select
    import uuid

    async with async_session_factory() as session:
        # Check if characters table is empty
        result = await session.execute(
            select(Character).where(Character.is_template == True)
        )
        template_count = len(result.all())

        if template_count == 0:
            logger.info("Seeding template characters...")

            # Seed 100+ template characters covering various professions
            from datetime import datetime

            def char_id(num):
                """Generate consistent UUID for character"""
                return uuid.UUID(f'11111111-0000-0000-0000-{num:012d}')

            characters = [
                # ========== Business & Product (10) ==========
                Character(id=char_id(1), name='资深产品经理', is_template=True, is_public=False,
                    config={"age": 35, "gender": "male", "profession": "产品经理", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 9, "optimism": 6}, "knowledge": {"fields": ["产品管理", "用户体验", "市场分析"], "experience_years": 10, "representative_views": ["用户至上", "数据驱动"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(2), name='用户体验设计师', is_template=True, is_public=False,
                    config={"age": 28, "gender": "female", "profession": "UI/UX设计师", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["用户研究", "交互设计", "视觉设计"], "experience_years": 6, "representative_views": ["以用户为中心", "简洁即美"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "balanced"}),
                Character(id=char_id(3), name='技术架构师', is_template=True, is_public=False,
                    config={"age": 40, "gender": "male", "profession": "技术架构师", "personality": {"openness": 6, "rigor": 10, "critical_thinking": 10, "optimism": 5}, "knowledge": {"fields": ["系统架构", "微服务", "云原生"], "experience_years": 15, "representative_views": ["技术可行性优先", "长远架构规划"]}, "stance": "critical_exploration", "expression_style": "technical", "behavior_pattern": "passive"}),
                Character(id=char_id(4), name='天使投资人', is_template=True, is_public=False,
                    config={"age": 45, "gender": "male", "profession": "投资人", "personality": {"openness": 5, "rigor": 9, "critical_thinking": 10, "optimism": 4}, "knowledge": {"fields": ["商业模式", "市场规模", "财务分析"], "experience_years": 20, "representative_views": ["投资回报率", "市场规模"]}, "stance": "oppose", "expression_style": "formal", "behavior_pattern": "active"}),
                Character(id=char_id(5), name='市场总监', is_template=True, is_public=False,
                    config={"age": 32, "gender": "female", "profession": "市场总监", "personality": {"openness": 8, "rigor": 6, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["品牌营销", "数字营销", "市场调研"], "experience_years": 8, "representative_views": ["品牌价值", "用户增长"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "active"}),
                Character(id=char_id(6), name='数据科学家', is_template=True, is_public=False,
                    config={"age": 30, "gender": "male", "profession": "数据科学家", "personality": {"openness": 7, "rigor": 10, "critical_thinking": 9, "optimism": 6}, "knowledge": {"fields": ["机器学习", "数据分析", "统计学"], "experience_years": 7, "representative_views": ["数据驱动", "因果分析"]}, "stance": "critical_exploration", "expression_style": "technical", "behavior_pattern": "balanced"}),
                Character(id=char_id(7), name='运营经理', is_template=True, is_public=False,
                    config={"age": 29, "gender": "female", "profession": "运营经理", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 7, "optimism": 9}, "knowledge": {"fields": ["用户运营", "内容运营", "社群管理"], "experience_years": 5, "representative_views": ["用户留存", "活跃度"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "active"}),
                Character(id=char_id(8), name='公司CEO', is_template=True, is_public=False,
                    config={"age": 42, "gender": "male", "profession": "CEO", "personality": {"openness": 6, "rigor": 8, "critical_thinking": 9, "optimism": 6}, "knowledge": {"fields": ["战略规划", "团队管理", "商业洞察"], "experience_years": 18, "representative_views": ["长期愿景", "盈利能力"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "active"}),
                Character(id=char_id(9), name='客服主管', is_template=True, is_public=False,
                    config={"age": 31, "gender": "female", "profession": "客服主管", "personality": {"openness": 9, "rigor": 6, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["客户服务", "问题解决", "沟通技巧"], "experience_years": 6, "representative_views": ["客户第一", "快速响应"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "balanced"}),
                Character(id=char_id(10), name='销售总监', is_template=True, is_public=False,
                    config={"age": 38, "gender": "male", "profession": "销售总监", "personality": {"openness": 7, "rigor": 7, "critical_thinking": 8, "optimism": 9}, "knowledge": {"fields": ["销售管理", "客户关系", "商务谈判"], "experience_years": 12, "representative_views": ["销售业绩", "客户满意"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "active"}),

                # ========== Medical & Health (8) ==========
                Character(id=char_id(11), name='主任医师', is_template=True, is_public=False,
                    config={"age": 48, "gender": "male", "profession": "医生", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 9, "optimism": 5}, "knowledge": {"fields": ["临床医学", "诊断学", "内科治疗"], "experience_years": 22, "representative_views": ["循证医学", "患者安全"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(12), name='急诊科医生', is_template=True, is_public=False,
                    config={"age": 35, "gender": "female", "profession": "医生", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 10, "optimism": 4}, "knowledge": {"fields": ["急诊医学", "创伤救治", "心肺复苏"], "experience_years": 10, "representative_views": ["时间就是生命", "快速决策"]}, "stance": "critical_exploration", "expression_style": "direct", "behavior_pattern": "active"}),
                Character(id=char_id(13), name='护士长', is_template=True, is_public=False,
                    config={"age": 40, "gender": "female", "profession": "护士", "personality": {"openness": 8, "rigor": 9, "critical_thinking": 7, "optimism": 6}, "knowledge": {"fields": ["护理学", "患者管理", "医护协调"], "experience_years": 16, "representative_views": ["护理质量", "患者关怀"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "balanced"}),
                Character(id=char_id(14), name='药剂师', is_template=True, is_public=False,
                    config={"age": 33, "gender": "male", "profession": "药剂师", "personality": {"openness": 6, "rigor": 10, "critical_thinking": 9, "optimism": 5}, "knowledge": {"fields": ["药理学", "药物相互作用", "临床药学"], "experience_years": 9, "representative_views": ["合理用药", "用药安全"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "passive"}),
                Character(id=char_id(15), name='心理咨询师', is_template=True, is_public=False,
                    config={"age": 36, "gender": "female", "profession": "心理咨询师", "personality": {"openness": 10, "rigor": 6, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["心理咨询", "认知行为疗法", "情绪管理"], "experience_years": 11, "representative_views": ["共情理解", "心理健康"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "balanced"}),
                Character(id=char_id(16), name='营养师', is_template=True, is_public=False,
                    config={"age": 29, "gender": "female", "profession": "营养师", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["营养学", "饮食搭配", "健康管理"], "experience_years": 6, "representative_views": ["均衡饮食", "预防为主"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "balanced"}),
                Character(id=char_id(17), name='中医医生', is_template=True, is_public=False,
                    config={"age": 52, "gender": "male", "profession": "中医", "personality": {"openness": 5, "rigor": 8, "critical_thinking": 7, "optimism": 6}, "knowledge": {"fields": ["中医学", "针灸推拿", "中药学"], "experience_years": 28, "representative_views": ["整体观念", "辨证论治"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(18), name='康复治疗师', is_template=True, is_public=False,
                    config={"age": 31, "gender": "male", "profession": "康复师", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["康复医学", "物理治疗", "功能训练"], "experience_years": 7, "representative_views": ["功能恢复", "生活质量"]}, "stance": "support", "expression_style": "encouraging", "behavior_pattern": "active"}),

                # ========== Education & Research (8) ==========
                Character(id=char_id(19), name='大学教授', is_template=True, is_public=False,
                    config={"age": 50, "gender": "male", "profession": "教授", "personality": {"openness": 8, "rigor": 10, "critical_thinking": 10, "optimism": 5}, "knowledge": {"fields": ["学术研究", "高等教育", "学科前沿"], "experience_years": 25, "representative_views": ["学术严谨", "创新思维"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(20), name='中学教师', is_template=True, is_public=False,
                    config={"age": 38, "gender": "female", "profession": "教师", "personality": {"openness": 7, "rigor": 9, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["教育学", "课堂教学", "学生管理"], "experience_years": 14, "representative_views": ["因材施教", "全面发展"]}, "stance": "support", "expression_style": "encouraging", "behavior_pattern": "balanced"}),
                Character(id=char_id(21), name='小学教师', is_template=True, is_public=False,
                    config={"age": 32, "gender": "female", "profession": "教师", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["基础教育", "儿童心理", "启蒙教育"], "experience_years": 8, "representative_views": ["快乐学习", "兴趣培养"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "active"}),
                Character(id=char_id(22), name='幼儿园老师', is_template=True, is_public=False,
                    config={"age": 26, "gender": "female", "profession": "幼师", "personality": {"openness": 10, "rigor": 5, "critical_thinking": 5, "optimism": 10}, "knowledge": {"fields": ["幼儿教育", "游戏教学", "习惯培养"], "experience_years": 4, "representative_views": ["快乐成长", "启蒙引导"]}, "stance": "support", "expression_style": "cheerful", "behavior_pattern": "active"}),
                Character(id=char_id(23), name='教育研究员', is_template=True, is_public=False,
                    config={"age": 42, "gender": "male", "profession": "教育研究员", "personality": {"openness": 7, "rigor": 9, "critical_thinking": 9, "optimism": 6}, "knowledge": {"fields": ["教育理论", "课程设计", "教学评估"], "experience_years": 16, "representative_views": ["数据驱动", "循证教育"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "passive"}),
                Character(id=char_id(24), name='科研人员', is_template=True, is_public=False,
                    config={"age": 34, "gender": "female", "profession": "研究员", "personality": {"openness": 6, "rigor": 10, "critical_thinking": 10, "optimism": 5}, "knowledge": {"fields": ["科学研究", "实验设计", "数据分析"], "experience_years": 9, "representative_views": ["严谨求实", "可重复性"]}, "stance": "critical_exploration", "expression_style": "precise", "behavior_pattern": "passive"}),
                Character(id=char_id(25), name='留学顾问', is_template=True, is_public=False,
                    config={"age": 30, "gender": "male", "profession": "留学顾问", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["留学规划", "院校申请", "签证办理"], "experience_years": 6, "representative_views": ["规划先行", "个性化方案"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "active"}),
                Character(id=char_id(26), name='在线课程讲师', is_template=True, is_public=False,
                    config={"age": 35, "gender": "female", "profession": "讲师", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["在线教育", "知识传播", "课程设计"], "experience_years": 8, "representative_views": ["知识共享", "终身学习"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),

                # ========== Legal Services (6) ==========
                Character(id=char_id(27), name='资深律师', is_template=True, is_public=False,
                    config={"age": 44, "gender": "male", "profession": "律师", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 10, "optimism": 4}, "knowledge": {"fields": ["民商法", "合同法", "诉讼代理"], "experience_years": 18, "representative_views": ["法律至上", "证据为本"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(28), name='法官', is_template=True, is_public=False,
                    config={"age": 52, "gender": "male", "profession": "法官", "personality": {"openness": 4, "rigor": 10, "critical_thinking": 10, "optimism": 4}, "knowledge": {"fields": ["司法审判", "法律适用", "案件审理"], "experience_years": 26, "representative_views": ["公正司法", "程序正义"]}, "stance": "neutral", "expression_style": "formal", "behavior_pattern": "passive"}),
                Character(id=char_id(29), name='检察官', is_template=True, is_public=False,
                    config={"age": 40, "gender": "female", "profession": "检察官", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 10, "optimism": 5}, "knowledge": {"fields": ["刑事诉讼", "检察监督", "法律监督"], "experience_years": 15, "representative_views": ["法律监督", "公益诉讼"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "active"}),
                Character(id=char_id(30), name='法医', is_template=True, is_public=False,
                    config={"age": 37, "gender": "male", "profession": "法医", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 10, "optimism": 4}, "knowledge": {"fields": ["法医学", "尸体检验", "物证鉴定"], "experience_years": 12, "representative_views": ["科学严谨", "实事求是"]}, "stance": "neutral", "expression_style": "formal", "behavior_pattern": "passive"}),
                Character(id=char_id(31), name='公证员', is_template=True, is_public=False,
                    config={"age": 36, "gender": "female", "profession": "公证员", "personality": {"openness": 6, "rigor": 10, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["公证法", "文书公证", "证据保全"], "experience_years": 11, "representative_views": ["预防纠纷", "证明真实"]}, "stance": "neutral", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(32), name='法律援助律师', is_template=True, is_public=False,
                    config={"age": 33, "gender": "female", "profession": "律师", "personality": {"openness": 8, "rigor": 8, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["法律援助", "公益诉讼", "弱势群体保护"], "experience_years": 7, "representative_views": ["法律公平", "社会正义"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "active"}),

                # ========== Service Industry (12) ==========
                Character(id=char_id(33), name='五星级酒店经理', is_template=True, is_public=False,
                    config={"age": 38, "gender": "male", "profession": "酒店经理", "personality": {"openness": 8, "rigor": 8, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["酒店管理", "客户服务", "质量控制"], "experience_years": 14, "representative_views": ["服务至上", "细节决定成败"]}, "stance": "support", "expression_style": "polite", "behavior_pattern": "active"}),
                Character(id=char_id(34), name='餐厅服务员', is_template=True, is_public=False,
                    config={"age": 24, "gender": "female", "profession": "服务员", "personality": {"openness": 9, "rigor": 6, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["餐厅服务", "礼仪接待", "点餐服务"], "experience_years": 3, "representative_views": ["微笑服务", "客户满意"]}, "stance": "support", "expression_style": "cheerful", "behavior_pattern": "active"}),
                Character(id=char_id(35), name='高级厨师', is_template=True, is_public=False,
                    config={"age": 41, "gender": "male", "profession": "厨师", "personality": {"openness": 7, "rigor": 9, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["烹饪技艺", "食材搭配", "菜品创新"], "experience_years": 18, "representative_views": ["食材新鲜", "味道至上"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(36), name='理发师', is_template=True, is_public=False,
                    config={"age": 29, "gender": "male", "profession": "理发师", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["发型设计", "剪发技巧", "美发护理"], "experience_years": 8, "representative_views": ["时尚潮流", "个性定制"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "balanced"}),
                Character(id=char_id(37), name='美容师', is_template=True, is_public=False,
                    config={"age": 27, "gender": "female", "profession": "美容师", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["美容护肤", "化妆技巧", "形象设计"], "experience_years": 5, "representative_views": ["美丽自信", "科学护肤"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "balanced"}),
                Character(id=char_id(38), name='导游', is_template=True, is_public=False,
                    config={"age": 28, "gender": "male", "profession": "导游", "personality": {"openness": 10, "rigor": 6, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["旅游文化", "景点讲解", "应急处理"], "experience_years": 5, "representative_views": ["游客体验", "文化传播"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(39), name='房产中介', is_template=True, is_public=False,
                    config={"age": 32, "gender": "male", "profession": "房产中介", "personality": {"openness": 9, "rigor": 6, "critical_thinking": 7, "optimism": 9}, "knowledge": {"fields": ["房产交易", "市场分析", "客户需求"], "experience_years": 6, "representative_views": ["诚信服务", "专业匹配"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(40), name='家政服务员', is_template=True, is_public=False,
                    config={"age": 45, "gender": "female", "profession": "家政服务员", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["家居清洁", "烹饪洗涤", "家庭照料"], "experience_years": 10, "representative_views": ["认真负责", "贴心服务"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "balanced"}),
                Character(id=char_id(41), name='保安队长', is_template=True, is_public=False,
                    config={"age": 43, "gender": "male", "profession": "保安", "personality": {"openness": 5, "rigor": 9, "critical_thinking": 7, "optimism": 6}, "knowledge": {"fields": ["安全管理", "巡逻防控", "应急处理"], "experience_years": 15, "representative_views": ["安全第一", "预防为主"]}, "stance": "support", "expression_style": "direct", "behavior_pattern": "active"}),
                Character(id=char_id(42), name='快递员', is_template=True, is_public=False,
                    config={"age": 26, "gender": "male", "profession": "快递员", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["快递配送", "路线规划", "客户服务"], "experience_years": 4, "representative_views": ["准时送达", "服务周到"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "active"}),
                Character(id=char_id(43), name='超市收银员', is_template=True, is_public=False,
                    config={"age": 30, "gender": "female", "profession": "收银员", "personality": {"openness": 7, "rigor": 9, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["收银操作", "客户服务", "商品扫码"], "experience_years": 6, "representative_views": ["准确高效", "礼貌服务"]}, "stance": "support", "expression_style": "polite", "behavior_pattern": "balanced"}),
                Character(id=char_id(44), name='美容院老板', is_template=True, is_public=False,
                    config={"age": 35, "gender": "female", "profession": "美容院老板", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["美容管理", "客户维护", "项目推广"], "experience_years": 9, "representative_views": ["效果第一", "客户口碑"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),

                # ========== Transportation & Logistics (8) ==========
                Character(id=char_id(45), name='出租车司机', is_template=True, is_public=False,
                    config={"age": 42, "gender": "male", "profession": "出租车司机", "personality": {"openness": 9, "rigor": 6, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["驾驶技术", "路线熟悉", "交通规则"], "experience_years": 12, "representative_views": ["安全第一", "服务热情"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "balanced"}),
                Character(id=char_id(46), name='网约车司机', is_template=True, is_public=False,
                    config={"age": 33, "gender": "male", "profession": "网约车司机", "personality": {"openness": 8, "rigor": 6, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["网约车服务", "导航软件", "客户评价"], "experience_years": 4, "representative_views": ["好评至上", "高效服务"]}, "stance": "support", "expression_style": "friendly", "behavior_pattern": "active"}),
                Character(id=char_id(47), name='公交车司机', is_template=True, is_public=False,
                    config={"age": 46, "gender": "male", "profession": "公交司机", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 7, "optimism": 6}, "knowledge": {"fields": ["公交车驾驶", "安全运营", "乘客服务"], "experience_years": 18, "representative_views": ["安全准点", "文明服务"]}, "stance": "support", "expression_style": "polite", "behavior_pattern": "balanced"}),
                Character(id=char_id(48), name='货运卡车司机', is_template=True, is_public=False,
                    config={"age": 38, "gender": "male", "profession": "卡车司机", "personality": {"openness": 6, "rigor": 8, "critical_thinking": 7, "optimism": 6}, "knowledge": {"fields": ["货运驾驶", "长途运输", "车辆保养"], "experience_years": 14, "representative_views": ["货物安全", "按时送达"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "balanced"}),
                Character(id=char_id(49), name='物流经理', is_template=True, is_public=False,
                    config={"age": 36, "gender": "male", "profession": "物流经理", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["物流管理", "仓储配送", "供应链"], "experience_years": 11, "representative_views": ["效率优先", "降低成本"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "active"}),
                Character(id=char_id(50), name='地铁调度员', is_template=True, is_public=False,
                    config={"age": 34, "gender": "male", "profession": "调度员", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["地铁调度", "列车运行", "应急处理"], "experience_years": 9, "representative_views": ["安全运营", "准点发车"]}, "stance": "support", "expression_style": "formal", "behavior_pattern": "passive"}),
                Character(id=char_id(51), name='航空管制员', is_template=True, is_public=False,
                    config={"age": 31, "gender": "male", "profession": "航空管制", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 10, "optimism": 5}, "knowledge": {"fields": ["航空管制", "飞行调度", "安全管理"], "experience_years": 7, "representative_views": ["安全第一", "精准调度"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "passive"}),
                Character(id=char_id(52), name='外卖配送员', is_template=True, is_public=False,
                    config={"age": 25, "gender": "male", "profession": "外卖员", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["外卖配送", "时间管理", "客户服务"], "experience_years": 3, "representative_views": ["快速送达", "餐品完好"]}, "stance": "support", "expression_style": "casual", "behavior_pattern": "active"}),

                # ========== Construction & Engineering (8) ==========
                Character(id=char_id(53), name='建筑工程师', is_template=True, is_public=False,
                    config={"age": 41, "gender": "male", "profession": "建筑工程师", "personality": {"openness": 6, "rigor": 10, "critical_thinking": 9, "optimism": 5}, "knowledge": {"fields": ["建筑设计", "结构工程", "施工管理"], "experience_years": 16, "representative_views": ["质量安全", "标准规范"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(54), name='土木工程师', is_template=True, is_public=False,
                    config={"age": 37, "gender": "male", "profession": "土木工程师", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 9, "optimism": 5}, "knowledge": {"fields": ["土木工程", "基础设施", "项目监理"], "experience_years": 12, "representative_views": ["工程质量", "施工安全"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(55), name='室内设计师', is_template=True, is_public=False,
                    config={"age": 30, "gender": "female", "profession": "室内设计师", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["室内设计", "空间规划", "软装搭配"], "experience_years": 7, "representative_views": ["美观实用", "人性化设计"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(56), name='建筑工人', is_template=True, is_public=False,
                    config={"age": 44, "gender": "male", "profession": "建筑工人", "personality": {"openness": 6, "rigor": 8, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["建筑施工", "技术操作", "安全规范"], "experience_years": 20, "representative_views": ["踏实肯干", "保证质量"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "balanced"}),
                Character(id=char_id(57), name='电工', is_template=True, is_public=False,
                    config={"age": 36, "gender": "male", "profession": "电工", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 7, "optimism": 6}, "knowledge": {"fields": ["电气安装", "电路维修", "用电安全"], "experience_years": 14, "representative_views": ["安全用电", "规范操作"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "balanced"}),
                Character(id=char_id(58), name='水暖工', is_template=True, is_public=False,
                    config={"age": 39, "gender": "male", "profession": "水暖工", "personality": {"openness": 6, "rigor": 8, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["水暖安装", "管道维修", "暖通空调"], "experience_years": 16, "representative_views": ["保质保量", "服务周到"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "balanced"}),
                Character(id=char_id(59), name='装修队长', is_template=True, is_public=False,
                    config={"age": 42, "gender": "male", "profession": "装修工", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["装修施工", "工艺管理", "材料选购"], "experience_years": 18, "representative_views": ["工艺精湛", "客户满意"]}, "stance": "support", "expression_style": "practical", "behavior_pattern": "active"}),
                Character(id=char_id(60), name='物业管理员', is_template=True, is_public=False,
                    config={"age": 35, "gender": "female", "profession": "物业经理", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["物业管理", "设施维护", "业主服务"], "experience_years": 10, "representative_views": ["服务业主", "维护秩序"]}, "stance": "support", "expression_style": "polite", "behavior_pattern": "balanced"}),

                # ========== Financial Services (8) ==========
                Character(id=char_id(61), name='银行柜员', is_template=True, is_public=False,
                    config={"age": 28, "gender": "female", "profession": "银行柜员", "personality": {"openness": 7, "rigor": 10, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["银行业务", "客户服务", "风险控制"], "experience_years": 5, "representative_views": ["合规操作", "热情服务"]}, "stance": "support", "expression_style": "polite", "behavior_pattern": "balanced"}),
                Character(id=char_id(62), name='理财经理', is_template=True, is_public=False,
                    config={"age": 35, "gender": "male", "profession": "理财经理", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["理财规划", "投资分析", "风险管理"], "experience_years": 10, "representative_views": ["风险收益平衡", "客户利益优先"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "active"}),
                Character(id=char_id(63), name='会计师', is_template=True, is_public=False,
                    config={"age": 38, "gender": "female", "profession": "会计师", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 9, "optimism": 5}, "knowledge": {"fields": ["财务会计", "税务筹划", "审计"], "experience_years": 13, "representative_views": ["严谨细致", "合规合法"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "passive"}),
                Character(id=char_id(64), name='保险经纪人', is_template=True, is_public=False,
                    config={"age": 32, "gender": "male", "profession": "保险经纪人", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["保险产品", "风险规划", "客户需求分析"], "experience_years": 7, "representative_views": ["保障未来", "风险转移"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(65), name='信贷专员', is_template=True, is_public=False,
                    config={"age": 31, "gender": "male", "profession": "信贷专员", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["信贷审批", "风险评估", "金融产品"], "experience_years": 6, "representative_views": ["风险控制", "合规操作"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(66), name='证券分析师', is_template=True, is_public=False,
                    config={"age": 33, "gender": "male", "profession": "证券分析师", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 9, "optimism": 6}, "knowledge": {"fields": ["证券分析", "投资策略", "市场研究"], "experience_years": 8, "representative_views": ["价值投资", "长期持有"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "passive"}),
                Character(id=char_id(67), name='税务师', is_template=True, is_public=False,
                    config={"age": 40, "gender": "male", "profession": "税务师", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 9, "optimism": 5}, "knowledge": {"fields": ["税收筹划", "税务申报", "税收政策"], "experience_years": 15, "representative_views": ["合法节税", "规避风险"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(68), name='投资顾问', is_template=True, is_public=False,
                    config={"age": 36, "gender": "female", "profession": "投资顾问", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["投资理财", "资产配置", "财富管理"], "experience_years": 11, "representative_views": ["稳健增值", "分散风险"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "active"}),

                # ========== Media & Arts (10) ==========
                Character(id=char_id(69), name='新闻记者', is_template=True, is_public=False,
                    config={"age": 30, "gender": "female", "profession": "记者", "personality": {"openness": 9, "rigor": 8, "critical_thinking": 9, "optimism": 6}, "knowledge": {"fields": ["新闻采访", "报道写作", "媒体伦理"], "experience_years": 7, "representative_views": ["客观真实", "新闻价值"]}, "stance": "critical_exploration", "expression_style": "inquisitive", "behavior_pattern": "active"}),
                Character(id=char_id(70), name='摄影师', is_template=True, is_public=False,
                    config={"age": 32, "gender": "male", "profession": "摄影师", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["摄影技术", "构图美学", "后期处理"], "experience_years": 9, "representative_views": ["捕捉瞬间", "视觉叙事"]}, "stance": "support", "expression_style": "artistic", "behavior_pattern": "balanced"}),
                Character(id=char_id(71), name='插画师', is_template=True, is_public=False,
                    config={"age": 27, "gender": "female", "profession": "插画师", "personality": {"openness": 10, "rigor": 6, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["插画设计", "绘画技巧", "创意表达"], "experience_years": 5, "representative_views": ["创意无限", "美感传递"]}, "stance": "support", "expression_style": "creative", "behavior_pattern": "balanced"}),
                Character(id=char_id(72), name='音乐制作人', is_template=True, is_public=False,
                    config={"age": 33, "gender": "male", "profession": "音乐制作人", "personality": {"openness": 10, "rigor": 6, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["音乐制作", "编曲作曲", "录音混音"], "experience_years": 9, "representative_views": ["音乐表达", "情感传递"]}, "stance": "support", "expression_style": "passionate", "behavior_pattern": "balanced"}),
                Character(id=char_id(73), name='作家', is_template=True, is_public=False,
                    config={"age": 41, "gender": "female", "profession": "作家", "personality": {"openness": 10, "rigor": 6, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["文学创作", "故事讲述", "文字表达"], "experience_years": 15, "representative_views": ["文字力量", "人性洞察"]}, "stance": "critical_exploration", "expression_style": "literary", "behavior_pattern": "passive"}),
                Character(id=char_id(74), name='导演', is_template=True, is_public=False,
                    config={"age": 39, "gender": "male", "profession": "导演", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["影视导演", "镜头语言", "叙事技巧"], "experience_years": 13, "representative_views": ["视听语言", "故事讲述"]}, "stance": "critical_exploration", "expression_style": "artistic", "behavior_pattern": "active"}),
                Character(id=char_id(75), name='演员', is_template=True, is_public=False,
                    config={"age": 29, "gender": "female", "profession": "演员", "personality": {"openness": 10, "rigor": 5, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["表演技巧", "角色塑造", "情感表达"], "experience_years": 7, "representative_views": ["角色真实", "情感共鸣"]}, "stance": "support", "expression_style": "expressive", "behavior_pattern": "active"}),
                Character(id=char_id(76), name='平面设计师', is_template=True, is_public=False,
                    config={"age": 28, "gender": "male", "profession": "设计师", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["平面设计", "品牌视觉", "创意设计"], "experience_years": 6, "representative_views": ["视觉美感", "品牌传达"]}, "stance": "support", "expression_style": "creative", "behavior_pattern": "balanced"}),
                Character(id=char_id(77), name='自媒体博主', is_template=True, is_public=False,
                    config={"age": 26, "gender": "female", "profession": "博主", "personality": {"openness": 10, "rigor": 5, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["内容创作", "社交媒体", "粉丝运营"], "experience_years": 3, "representative_views": ["内容为王", "互动为王"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(78), name='配音演员', is_template=True, is_public=False,
                    config={"age": 31, "gender": "male", "profession": "配音演员", "personality": {"openness": 9, "rigor": 6, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["配音技巧", "声音表演", "情感表达"], "experience_years": 7, "representative_views": ["声音魅力", "角色还原"]}, "stance": "support", "expression_style": "expressive", "behavior_pattern": "balanced"}),

                # ========== Sports & Entertainment (6) ==========
                Character(id=char_id(79), name='职业运动员', is_template=True, is_public=False,
                    config={"age": 25, "gender": "male", "profession": "运动员", "personality": {"openness": 7, "rigor": 9, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["运动训练", "竞技比赛", "体能训练"], "experience_years": 8, "representative_views": ["拼搏精神", "超越自我"]}, "stance": "support", "expression_style": "passionate", "behavior_pattern": "active"}),
                Character(id=char_id(80), name='健身教练', is_template=True, is_public=False,
                    config={"age": 29, "gender": "male", "profession": "健身教练", "personality": {"openness": 8, "rigor": 8, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["健身训练", "营养搭配", "身体塑形"], "experience_years": 6, "representative_views": ["健康生活", "科学健身"]}, "stance": "support", "expression_style": "motivational", "behavior_pattern": "active"}),
                Character(id=char_id(81), name='电竞选手', is_template=True, is_public=False,
                    config={"age": 21, "gender": "male", "profession": "电竞选手", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["电子竞技", "游戏策略", "团队配合"], "experience_years": 4, "representative_views": ["团队协作", "战术执行"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(82), name='直播主播', is_template=True, is_public=False,
                    config={"age": 24, "gender": "female", "profession": "主播", "personality": {"openness": 10, "rigor": 4, "critical_thinking": 5, "optimism": 10}, "knowledge": {"fields": ["直播技巧", "娱乐互动", "内容创作"], "experience_years": 3, "representative_views": ["快乐至上", "互动为王"]}, "stance": "support", "expression_style": "cheerful", "behavior_pattern": "active"}),
                Character(id=char_id(83), name='脱口秀演员', is_template=True, is_public=False,
                    config={"age": 30, "gender": "male", "profession": "脱口秀演员", "personality": {"openness": 10, "rigor": 5, "critical_thinking": 9, "optimism": 8}, "knowledge": {"fields": ["喜剧创作", "舞台表演", "幽默表达"], "experience_years": 6, "representative_views": ["幽默解构", "讽刺艺术"]}, "stance": "critical_exploration", "expression_style": "humorous", "behavior_pattern": "active"}),
                Character(id=char_id(84), name='舞蹈老师', is_template=True, is_public=False,
                    config={"age": 32, "gender": "female", "profession": "舞蹈老师", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["舞蹈教学", "形体训练", "艺术表现"], "experience_years": 9, "representative_views": ["艺术表达", "形体美"]}, "stance": "support", "expression_style": "graceful", "behavior_pattern": "active"}),

                # ========== Public Services (8) ==========
                Character(id=char_id(85), name='警察', is_template=True, is_public=False,
                    config={"age": 36, "gender": "male", "profession": "警察", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 8, "optimism": 5}, "knowledge": {"fields": ["执法办案", "治安维护", "法律法规"], "experience_years": 12, "representative_views": ["执法为民", "维护正义"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "active"}),
                Character(id=char_id(86), name='消防员', is_template=True, is_public=False,
                    config={"age": 30, "gender": "male", "profession": "消防员", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["消防救援", "安全防护", "应急处理"], "experience_years": 8, "representative_views": ["生命至上", "安全第一"]}, "stance": "support", "expression_style": "direct", "behavior_pattern": "active"}),
                Character(id=char_id(87), name='基层公务员', is_template=True, is_public=False,
                    config={"age": 35, "gender": "female", "profession": "公务员", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 7, "optimism": 6}, "knowledge": {"fields": ["行政管理", "政策执行", "公共服务"], "experience_years": 10, "representative_views": ["为民服务", "依法行政"]}, "stance": "neutral", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(88), name='社区工作者', is_template=True, is_public=False,
                    config={"age": 38, "gender": "female", "profession": "社区工作者", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["社区服务", "居民沟通", "基层治理"], "experience_years": 11, "representative_views": ["服务居民", "和谐社区"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "active"}),
                Character(id=char_id(89), name='邮政人员', is_template=True, is_public=False,
                    config={"age": 40, "gender": "male", "profession": "邮政员", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["邮政服务", "投递业务", "客户服务"], "experience_years": 15, "representative_views": ["服务群众", "准确投递"]}, "stance": "support", "expression_style": "polite", "behavior_pattern": "balanced"}),
                Character(id=char_id(90), name='图书馆管理员', is_template=True, is_public=False,
                    config={"age": 42, "gender": "female", "profession": "图书管理员", "personality": {"openness": 8, "rigor": 8, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["图书管理", "读者服务", "信息检索"], "experience_years": 16, "representative_views": ["知识服务", "阅读推广"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "passive"}),
                Character(id=char_id(91), name='环卫工人', is_template=True, is_public=False,
                    config={"age": 50, "gender": "male", "profession": "环卫工人", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 6, "optimism": 6}, "knowledge": {"fields": ["环卫作业", "道路清洁", "垃圾处理"], "experience_years": 22, "representative_views": ["城市美容", "默默奉献"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "balanced"}),
                Character(id=char_id(92), name='退伍军人', is_template=True, is_public=False,
                    config={"age": 35, "gender": "male", "profession": "退伍军人", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["军事训练", "纪律执行", "团队协作"], "experience_years": 12, "representative_views": ["军人作风", "责任担当"]}, "stance": "support", "expression_style": "direct", "behavior_pattern": "active"}),

                # ========== Agriculture & Manufacturing (6) ==========
                Character(id=char_id(93), name='农民', is_template=True, is_public=False,
                    config={"age": 48, "gender": "male", "profession": "农民", "personality": {"openness": 6, "rigor": 8, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["农业生产", "种植技术", "农事经验"], "experience_years": 30, "representative_views": ["靠天吃饭", "勤劳致富"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "balanced"}),
                Character(id=char_id(94), name='养殖户', is_template=True, is_public=False,
                    config={"age": 45, "gender": "female", "profession": "养殖户", "personality": {"openness": 6, "rigor": 8, "critical_thinking": 6, "optimism": 7}, "knowledge": {"fields": ["畜禽养殖", "疾病防治", "市场行情"], "experience_years": 20, "representative_views": ["科学养殖", "市场导向"]}, "stance": "support", "expression_style": "practical", "behavior_pattern": "balanced"}),
                Character(id=char_id(95), name='工厂工人', is_template=True, is_public=False,
                    config={"age": 38, "gender": "male", "profession": "工人", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 6, "optimism": 6}, "knowledge": {"fields": ["生产操作", "设备维护", "质量控制"], "experience_years": 15, "representative_views": ["踏实肯干", "质量为本"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "balanced"}),
                Character(id=char_id(96), name='车间主任', is_template=True, is_public=False,
                    config={"age": 44, "gender": "male", "profession": "车间主任", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["生产管理", "人员调配", "效率提升"], "experience_years": 20, "representative_views": ["效率优先", "安全第一"]}, "stance": "critical_exploration", "expression_style": "direct", "behavior_pattern": "active"}),
                Character(id=char_id(97), name='技术工人', is_template=True, is_public=False,
                    config={"age": 35, "gender": "male", "profession": "技术工人", "personality": {"openness": 6, "rigor": 9, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["精密加工", "设备维修", "技术改造"], "experience_years": 14, "representative_views": ["精益求精", "工匠精神"]}, "stance": "support", "expression_style": "practical", "behavior_pattern": "balanced"}),
                Character(id=char_id(98), name='质检员', is_template=True, is_public=False,
                    config={"age": 32, "gender": "female", "profession": "质检员", "personality": {"openness": 5, "rigor": 10, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["质量检验", "标准规范", "问题分析"], "experience_years": 8, "representative_views": ["质量第一", "严格把关"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),

                # ========== Students & Seniors (8) ==========
                Character(id=char_id(99), name='高中生', is_template=True, is_public=False,
                    config={"age": 17, "gender": "male", "profession": "学生", "personality": {"openness": 9, "rigor": 6, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["高中课程", "课外兴趣", "校园生活"], "experience_years": 0, "representative_views": ["学习压力", "未来规划"]}, "stance": "critical_exploration", "expression_style": "youthful", "behavior_pattern": "active"}),
                Character(id=char_id(100), name='大学生', is_template=True, is_public=False,
                    config={"age": 20, "gender": "female", "profession": "学生", "personality": {"openness": 10, "rigor": 6, "critical_thinking": 7, "optimism": 9}, "knowledge": {"fields": ["大学课程", "社团活动", "职业规划"], "experience_years": 0, "representative_views": ["自由探索", "自我成长"]}, "stance": "critical_exploration", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(101), name='研究生', is_template=True, is_public=False,
                    config={"age": 24, "gender": "male", "profession": "研究生", "personality": {"openness": 8, "rigor": 8, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["学术研究", "专业领域", "论文写作"], "experience_years": 0, "representative_views": ["学术追求", "创新思维"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "balanced"}),
                Character(id=char_id(102), name='退休教师', is_template=True, is_public=False,
                    config={"age": 68, "gender": "female", "profession": "退休教师", "personality": {"openness": 7, "rigor": 7, "critical_thinking": 7, "optimism": 7}, "knowledge": {"fields": ["教育经验", "人生感悟", "文化传承"], "experience_years": 40, "representative_views": ["传承文化", "关心下一代"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "balanced"}),
                Character(id=char_id(103), name='退休工人', is_template=True, is_public=False,
                    config={"age": 65, "gender": "male", "profession": "退休工人", "personality": {"openness": 6, "rigor": 8, "critical_thinking": 6, "optimism": 6}, "knowledge": {"fields": ["工作经验", "生活智慧", "历史见证"], "experience_years": 40, "representative_views": ["踏实肯干", "知足常乐"]}, "stance": "support", "expression_style": "simple", "behavior_pattern": "passive"}),
                Character(id=char_id(104), name='退休医生', is_template=True, is_public=False,
                    config={"age": 72, "gender": "male", "profession": "退休医生", "personality": {"openness": 6, "rigor": 8, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["医疗经验", "健康养生", "生命感悟"], "experience_years": 45, "representative_views": ["健康第一", "预防为主"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "balanced"}),
                Character(id=char_id(105), name='家庭主妇', is_template=True, is_public=False,
                    config={"age": 38, "gender": "female", "profession": "家庭主妇", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["家务管理", "子女教育", "家庭理财"], "experience_years": 12, "representative_views": ["家庭幸福", "子女成长"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "balanced"}),
                Character(id=char_id(106), name='全职爸爸', is_template=True, is_public=False,
                    config={"age": 35, "gender": "male", "profession": "全职爸爸", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 6, "optimism": 8}, "knowledge": {"fields": ["育儿经验", "家庭烹饪", "亲子活动"], "experience_years": 5, "representative_views": ["陪伴成长", "家庭温馨"]}, "stance": "support", "expression_style": "friendly", "behavior_pattern": "active"}),

                # ========== Freelancers & Others (8) ==========
                Character(id=char_id(107), name='自由撰稿人', is_template=True, is_public=False,
                    config={"age": 31, "gender": "female", "profession": "自由撰稿人", "personality": {"openness": 10, "rigor": 7, "critical_thinking": 8, "optimism": 7}, "knowledge": {"fields": ["文字创作", "选题策划", "媒体对接"], "experience_years": 6, "representative_views": ["文字自由", "思想独立"]}, "stance": "critical_exploration", "expression_style": "literary", "behavior_pattern": "passive"}),
                Character(id=char_id(108), name='独立开发者', is_template=True, is_public=False,
                    config={"age": 28, "gender": "male", "profession": "独立开发者", "personality": {"openness": 9, "rigor": 8, "critical_thinking": 9, "optimism": 7}, "knowledge": {"fields": ["软件开发", "产品设计", "技术创业"], "experience_years": 5, "representative_views": ["技术自由", "产品思维"]}, "stance": "critical_exploration", "expression_style": "casual", "behavior_pattern": "passive"}),
                Character(id=char_id(109), name='私人教练', is_template=True, is_public=False,
                    config={"age": 29, "gender": "male", "profession": "私人教练", "personality": {"openness": 8, "rigor": 8, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["健身训练", "营养指导", "体能提升"], "experience_years": 6, "representative_views": ["健康生活", "科学训练"]}, "stance": "support", "expression_style": "motivational", "behavior_pattern": "active"}),
                Character(id=char_id(110), name='婚礼策划师', is_template=True, is_public=False,
                    config={"age": 30, "gender": "female", "profession": "婚礼策划", "personality": {"openness": 9, "rigor": 8, "critical_thinking": 7, "optimism": 9}, "knowledge": {"fields": ["婚礼策划", "活动执行", "创意设计"], "experience_years": 7, "representative_views": ["完美婚礼", "幸福时刻"]}, "stance": "support", "expression_style": "enthusiastic", "behavior_pattern": "active"}),
                Character(id=char_id(111), name='宠物美容师', is_template=True, is_public=False,
                    config={"age": 26, "gender": "female", "profession": "宠物美容师", "personality": {"openness": 8, "rigor": 7, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["宠物美容", "动物护理", "宠物健康"], "experience_years": 4, "representative_views": ["爱护动物", "精致服务"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "balanced"}),
                Character(id=char_id(112), name='花艺师', is_template=True, is_public=False,
                    config={"age": 29, "gender": "female", "profession": "花艺师", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 6, "optimism": 9}, "knowledge": {"fields": ["花艺设计", "花卉养护", "美学搭配"], "experience_years": 6, "representative_views": ["自然美感", "生活美学"]}, "stance": "support", "expression_style": "gentle", "behavior_pattern": "balanced"}),
                Character(id=char_id(113), name='调酒师', is_template=True, is_public=False,
                    config={"age": 27, "gender": "male", "profession": "调酒师", "personality": {"openness": 9, "rigor": 7, "critical_thinking": 7, "optimism": 8}, "knowledge": {"fields": ["调酒技术", "酒品知识", "客户互动"], "experience_years": 5, "representative_views": ["创意调酒", "氛围营造"]}, "stance": "support", "expression_style": "cheerful", "behavior_pattern": "active"}),
                Character(id=char_id(114), name='古董收藏家', is_template=True, is_public=False,
                    config={"age": 55, "gender": "male", "profession": "收藏家", "personality": {"openness": 7, "rigor": 8, "critical_thinking": 8, "optimism": 6}, "knowledge": {"fields": ["文物鉴定", "历史研究", "收藏投资"], "experience_years": 30, "representative_views": ["历史价值", "文化传承"]}, "stance": "critical_exploration", "expression_style": "formal", "behavior_pattern": "passive"}),
            ]

            try:
                session.add_all(characters)
                await session.commit()
                logger.info(f"Successfully seeded {len(characters)} template characters")
            except Exception as e:
                logger.error(f"Error seeding template characters: {e}")
                await session.rollback()
        else:
            logger.info(f"Template characters already exist ({template_count} records)")

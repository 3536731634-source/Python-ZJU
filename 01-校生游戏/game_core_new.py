# ==================== game_core.py ====================
import random
import json

class EventManager:
    def __init__(self, difficulty=1.0):
        self.difficulty = difficulty
        self.events = [
            ("✨ 教授赏识：你的论文被推荐发表，GPA+{g}, 获得学术荣誉。", 
             lambda s, d: (int(5*d), 0, 0, 0), True),
            ("🤝 社团成功：组织的活动大获好评，社交+{s}, 领导经验+1。", 
             lambda s, d: (0, int(8*d), 0, 0), True),
            ("🏆 体育竞赛获奖：奖金+{m}，心理健康+{h}。", 
             lambda s, d: (0, 0, int(5*d), int(20*d)), False),
            ("❤️ 邂逅恋人：心理健康+{h}，社交+{s}。", 
             lambda s, d: (0, int(5*d), int(10*d), 0), False),
            ("💡 意外之财：捡到奖学金，金钱+{m}。", 
             lambda s, d: (0, 0, 0, int(30*d)), False),
            ("📖 图书馆偶遇学霸：GPA+{g}，社交+{s}。", 
             lambda s, d: (int(3*d), int(2*d), 0, 0), False),
            ("📉 考试不及格：GPA-{g}，心理健康-{h}。", 
             lambda s, d: (int(-8/d), 0, int(-6/d), 0), False),
            ("💔 舍友矛盾：社交-{s}，心理-{h}。", 
             lambda s, d: (0, int(-6/d), int(-5/d), 0), False),
            ("😰 焦虑袭来：GPA-{g}，心理-{h}。", 
             lambda s, d: (int(-3/d), 0, int(-12/d), 0), False),
            ("💰 财务危机：被骗或被偷，金钱-{m}。", 
             lambda s, d: (0, 0, 0, int(-35/d)), False),
            ("🎮 游戏上瘾：GPA-{g}，社交-{s}。", 
             lambda s, d: (int(-5/d), int(-3/d), 0, 0), False),
            ("⚖️ 社团与考试冲突：GPA-{g}，社交+{s}，心理-{h}。", 
             lambda s, d: (int(-4/d), int(6*d), int(-3/d), 0), False),
            ("🍕 暴饮暴食：心理+{h}，金钱-{m}。", 
             lambda s, d: (0, 0, int(5*d), int(-8*d)), False),
            ("📱 网课划水：GPA-{g}，心理+{h}。", 
             lambda s, d: (int(-2/d), 0, int(4*d), 0), False),
            ("🤧 流感来袭：GPA-{g}，心理-{h}，社交-{s}。", 
             lambda s, d: (int(-3/d), int(-2/d), int(-4/d), 0), False),
        ]
    
    def get_random_event(self):
        desc_template, effect_func, award_flag = random.choice(self.events)
        raw_effect = effect_func(self, self.difficulty)
        desc = desc_template.format(
            g=abs(raw_effect[0]) if raw_effect[0] != 0 else "",
            s=abs(raw_effect[1]) if raw_effect[1] != 0 else "",
            h=abs(raw_effect[2]) if raw_effect[2] != 0 else "",
            m=abs(raw_effect[3]) if raw_effect[3] != 0 else ""
        ).replace("+-", "-").replace("+0", "").replace("-0", "")
        desc = desc.replace("GPA+-", "GPA-").replace("社交+-", "社交-")
        return desc, raw_effect, award_flag


class UniversityGame:
    def __init__(self, difficulty="normal"):
        self.semester = 1
        self.gpa = 60
        self.social = 60
        self.mental = 70
        self.money = 50
        self.game_over = False
        self.final_comment = ""
        self.action_history = []
        
        self.has_academic_award = False
        self.has_leadership_exp = False
        self.has_internship = False
        
        self.difficulty_map = {"easy": 1.2, "normal": 1.0, "hard": 0.8}
        self.difficulty = self.difficulty_map.get(difficulty, 1.0)
        self.event_manager = EventManager(self.difficulty)
        self.perfect_semester_count = 0
    
    def get_state(self):
        return {
            'semester': self.semester,
            'gpa': self.gpa,
            'social': self.social,
            'mental': self.mental,
            'money': self.money,
            'game_over': self.game_over,
            'final_comment': self.final_comment,
            'has_academic_award': self.has_academic_award,
            'has_leadership_exp': self.has_leadership_exp,
            'has_internship': self.has_internship,
            'action_history': self.action_history[-15:],
            'difficulty': self.difficulty,
            'perfect_semester_count': self.perfect_semester_count,
        }
    
    def load_state(self, state):
        self.semester = state['semester']
        self.gpa = state['gpa']
        self.social = state['social']
        self.mental = state['mental']
        self.money = state['money']
        self.game_over = state['game_over']
        self.final_comment = state['final_comment']
        self.has_academic_award = state['has_academic_award']
        self.has_leadership_exp = state['has_leadership_exp']
        self.has_internship = state['has_internship']
        self.action_history = state.get('action_history', [])
        self.difficulty = state.get('difficulty', 1.0)
        self.perfect_semester_count = state.get('perfect_semester_count', 0)
    
    def _clamp(self, value, min_val, max_val):
        return max(min_val, min(value, max_val))
    
    def _check_warning(self):
        warnings = []
        if self.gpa <= 25:
            warnings.append("学业危险")
        if self.mental <= 25:
            warnings.append("心理危机")
        if self.money <= -10:
            warnings.append("财务告急")
        return warnings
    
    def _check_game_over(self):
        if self.gpa <= 20:
            self.game_over = True
            self.final_comment = "【学业崩溃】由于成绩太差，你被学校劝退。"
        elif self.mental <= 15:
            self.game_over = True
            self.final_comment = "【心理危机】长期压力导致休学。"
        elif self.money <= -30:
            self.game_over = True
            self.final_comment = "【财务困境】无法承担学费，被迫中断学业。"
        elif self.semester > 8:
            self.game_over = True
            self._final_evaluation()
    
    def _final_evaluation(self):
        score = (self.gpa * 0.4 + self.social * 0.2 + self.mental * 0.2 + min(self.money, 100) * 0.2)
        if self.has_academic_award:
            score += 5
        if self.has_leadership_exp:
            score += 5
        if self.has_internship:
            score += 5
        if self.has_academic_award and self.has_leadership_exp and self.has_internship and self.perfect_semester_count >= 6:
            self.final_comment = "🏆 全能大神！你不仅学业顶尖、社交达人、还获得了实习与领导经验，人生赢家！"
        elif score >= 80:
            self.final_comment = "🎉 荣耀毕业！前途无量！"
        elif score >= 60:
            self.final_comment = "👍 普通毕业生，找到一份平凡工作。"
        elif score >= 40:
            self.final_comment = "😔 勉强毕业，未来仍需努力。"
        else:
            self.final_comment = "💔 艰难毕业，后悔当初没有规划。"
    
    def get_actions(self):
        return [
            ("📚 专心学习", "GPA +8~18, 心理 -2~6, 小概率获奖学金", (8,18), (-6,-2), (0,0), (0,0)),
            ("🎉 社交活动", "社交+5~15, 心理+3~10, 金钱-5~15", (0,0), (3,10), (5,15), (-15,-5)),
            ("💼 兼职工作", "金钱+15~30, GPA -2~8, 心理 -1~5", (-8,-2), (-5,-1), (0,0), (15,30)),
            ("🏃 体育锻炼", "心理+5~12, GPA +0~3", (0,3), (5,12), (0,0), (0,0)),
            ("🎮 放松娱乐", "心理+6~15, GPA -3~12, 小概率金钱-10", (-12,-3), (6,15), (0,0), (0,0)),
            ("🤝 志愿/领导", "社交+4~12, 心理+2~6, 金钱-5", (0,0), (2,6), (4,12), (-5,-5)),
        ]
    
    def perform_action(self, action_idx):
        action = self.get_actions()[action_idx]
        ranges = action[2:]
        def rnd(r):
            if r[0] == 0 and r[1] == 0:
                return 0
            base = random.randint(r[0], r[1])
            if base < 0:
                return int(base / self.difficulty)
            else:
                return int(base * self.difficulty)
        delta_gpa = rnd(ranges[0])
        delta_mental = rnd(ranges[1])
        delta_social = rnd(ranges[2])
        delta_money = rnd(ranges[3])
        
        self.gpa = self._clamp(self.gpa + delta_gpa, 0, 100)
        self.mental = self._clamp(self.mental + delta_mental, 0, 100)
        self.social = self._clamp(self.social + delta_social, 0, 100)
        self.money = self._clamp(self.money + delta_money, -30, 200)
        
        desc = f"{action[0]}：" + "，".join([f"{n} {v:+d}" for n,v in [("GPA", delta_gpa), ("心理", delta_mental), ("社交", delta_social), ("金钱", delta_money)] if v != 0]) + "。"
        
        if action_idx == 0 and random.random() < 0.2 and self.gpa >= 75:
            self.has_academic_award = True
            self.money += 15
            desc += " 因成绩优异获得奖学金！金钱+15，获得学术奖励成就。"
        elif action_idx == 2 and random.random() < 0.2:
            self.has_internship = True
            desc += " 工作表现优异，获得实习证明！"
        elif action_idx == 5 and random.random() < 0.25:
            self.has_leadership_exp = True
            desc += " 展现了领导才能，获得领导经验成就！"
        
        self.action_history.append(f"第{self.semester}学期: {desc}")
        if not self._check_warning():
            self.perfect_semester_count += 1
        return desc
    
    def apply_random_event(self):
        desc_template, effects, award_flag = self.event_manager.get_random_event()
        delta_gpa, delta_social, delta_mental, delta_money = effects
        self.gpa = self._clamp(self.gpa + delta_gpa, 0, 100)
        self.social = self._clamp(self.social + delta_social, 0, 100)
        self.mental = self._clamp(self.mental + delta_mental, 0, 100)
        self.money = self._clamp(self.money + delta_money, -30, 200)
        if award_flag:
            if "领导" in desc_template:
                self.has_leadership_exp = True
            elif "学术" in desc_template or "论文" in desc_template:
                self.has_academic_award = True
        full_desc = f"{desc_template}"
        self.action_history.append(f"第{self.semester}学期 [随机事件]: {full_desc}")
        return full_desc
    
    def next_semester(self):
        self.semester += 1
        self._check_game_over()
    
    def is_game_over(self):
        return self.game_over
    
    def get_summary(self):
        def bar(value, max_val=100, length=20):
            filled = int(length * value / max_val)
            return "█" * filled + "░" * (length - filled)
        def colored(val, max_val=100):
            if val <= 30:
                color = "31"
            elif val <= 60:
                color = "33"
            else:
                color = "32"
            return f"\033[{color}m{val}\033[0m"
        gpa_disp = colored(self.gpa)
        social_disp = colored(self.social)
        mental_disp = colored(self.mental)
        money_disp = colored(self.money, 200)
        status = f"""
╔══════════════════════════════════════════════════════════════════╗
║                      📅 第{self.semester}/8学期                              ║
╠══════════════════════════════════════════════════════════════════╣
║  📖 GPA : {gpa_disp}  {bar(self.gpa)}                                    ║
║  👥 社交 : {social_disp}  {bar(self.social)}                                    ║
║  🧠 心理 : {mental_disp}  {bar(self.mental)}                                   ║
║  💰 金钱 : {money_disp}  {bar(self.money+30, 230)}  (安全线:-30)                 ║
╠══════════════════════════════════════════════════════════════════╣
║  成就: {'🏅学术奖 ' if self.has_academic_award else ''}{'🏅领导力 ' if self.has_leadership_exp else ''}{'🏅实习 ' if self.has_internship else ''}
║  完美学期(无警告): {self.perfect_semester_count}/8
╚══════════════════════════════════════════════════════════════════╝
"""
        warns = self._check_warning()
        if warns:
            status += f"\n\033[31m⚠️ 警告：{' '.join(warns)}！请尽快改善！\033[0m\n"
        return status

# ==================== console_game.py ====================
# 大学人生模拟器 - 全功能控制台版本
# 架构：Model (UniversityGame) - View (ConsoleRenderer) - Controller (GameController)
# AI使用率：约20%（仅辅助生成存档JSON结构和一些颜色代码示例）

import subprocess
import os
import json
import random
from game_core_new import UniversityGame

# 设置控制台支持颜色
if os.name == 'nt':
    os.system('color')  # Windows启用ANSI支持（部分终端需要）

def clear_screen():
    subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)

class ConsoleRenderer:
    """负责所有界面渲染"""
    @staticmethod
    def print_header():
        print("\033[1;36m" + "="*60 + "\033[0m")
        print("\033[1;33m       🎓 大学人生模拟器 - 我命由我 × 随机宿命 🎲\033[0m")
        print("\033[1;36m" + "="*60 + "\033[0m")
    
    @staticmethod
    def print_menu():
        print("\n\033[1;34m【主菜单】\033[0m")
        print("  1. 新游戏")
        print("  2. 读取存档")
        print("  3. 退出")
        return input("请选择: ").strip()
    
    @staticmethod
    def print_actions(game):
        actions = game.get_actions()
        print("\n\033[1;34m📌 本学期行动 (输入编号):\033[0m")
        for idx, act in enumerate(actions):
            name = act[0]
            desc = act[1]
            print(f"  {idx+1}. {name:12} \033[2m- {desc}\033[0m")
    
    @staticmethod
    def print_status(game):
        print(game.get_summary())
    
    @staticmethod
    def print_event(desc):
        print(f"\n\033[1;35m🎲 随机宿命事件：{desc}\033[0m")
    
    @staticmethod
    def print_action_result(desc):
        print(f"\033[1;32m🎯 行动结果：{desc}\033[0m")
    
    @staticmethod
    def print_warning(msg):
        print(f"\033[31m{msg}\033[0m")
    
    @staticmethod
    def print_game_over(comment):
        print("\n" + "="*60)
        print("\033[1;31m【游戏结局】\033[0m")
        print(comment)
        print("="*60)
        print("\n感谢游玩！记住：人生既需要主动选择，也要坦然面对随机风云。")
    
    @staticmethod
    def show_history(history):
        if not history:
            print("暂无历史记录。")
            return
        print("\n\033[1;34m📜 近期人生履历 (最近15条):\033[0m")
        for i, h in enumerate(history[-15:], 1):
            print(f"  {i}. {h}")

class GameController:
    def __init__(self):
        self.game = None
    
    def choose_difficulty(self):
        print("\n选择难度:")
        print("  1. 简单 (收益增加，惩罚减轻)")
        print("  2. 普通 (平衡)")
        print("  3. 困难 (收益减少，惩罚加重)")
        choice = input("请输入 (1-3) [默认2]: ").strip()
        if choice == '1':
            return "easy"
        elif choice == '3':
            return "hard"
        else:
            return "normal"
    
    def save_game(self):
        if not self.game or self.game.game_over:
            print("无法存档：游戏未开始或已结束。")
            return
        state = self.game.get_state()
        state['difficulty_name'] = {1.2:"easy", 1.0:"normal", 0.8:"hard"}.get(state['difficulty'], "normal")
        with open("save_game.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print("\033[32m✅ 游戏已保存到 save_game.json\033[0m")
    
    def load_game(self):
        if not os.path.exists("save_game.json"):
            print("没有找到存档文件。")
            return False
        try:
            with open("save_game.json", "r", encoding="utf-8") as f:
                state = json.load(f)
            # 从存档恢复难度名称
            diff = state.get("difficulty_name", "normal")
            self.game = UniversityGame(diff)
            self.game.load_state(state)
            print("\033[32m✅ 读取存档成功！\033[0m")
            return True
        except Exception as e:
            print(f"载入失败: {e}")
            return False
    
    def new_game(self):
        diff = self.choose_difficulty()
        self.game = UniversityGame(diff)
        print(f"已选择难度: {diff.upper()}")
        input("按回车开始游戏...")
    
    def game_loop(self):
        renderer = ConsoleRenderer()
        while not self.game.is_game_over():
            clear_screen()
            renderer.print_header()
            renderer.print_status(self.game)
            
            if self.game.semester > 8:
                break
            
            renderer.print_actions(self.game)
            # 额外命令：输入 h 查看历史， s 存档， q 退出
            print("\n\033[2m(输入 h 查看历史, s 存档本回合, q 返回主菜单)\033[0m")
            user_input = input("\n请输入行动编号或命令: ").strip().lower()
            if user_input == 'h':
                renderer.show_history(self.game.action_history)
                input("按回车继续...")
                continue
            elif user_input == 's':
                self.save_game()
                input("按回车继续...")
                continue
            elif user_input == 'q':
                print("返回主菜单...")
                return  # 退出循环回主菜单
            else:
                try:
                    choice = int(user_input) - 1
                    if choice < 0 or choice >= len(self.game.get_actions()):
                        raise ValueError
                except:
                    print("无效输入，随机选择行动。")
                    choice = random.randint(0, len(self.game.get_actions())-1)
            
            # 执行行动
            action_desc = self.game.perform_action(choice)
            renderer.print_action_result(action_desc)
            
            # 随机事件
            input("\n⏎ 按回车键迎接随机事件...")
            event_desc = self.game.apply_random_event()
            renderer.print_event(event_desc)
            
            # 学期结束推进
            self.game.next_semester()
            if self.game.is_game_over():
                break
            
            if self.game.semester <= 8:
                input("\n⏎ 按回车键进入下一学期...")
        
        # 游戏结束显示结局
        clear_screen()
        renderer.print_header()
        renderer.print_status(self.game)
        renderer.print_game_over(self.game.final_comment)
        input("\n按回车返回主菜单...")
    
    def run(self):
        renderer = ConsoleRenderer()
        while True:
            clear_screen()
            renderer.print_header()
            choice = renderer.print_menu()
            if choice == '1':
                self.new_game()
                if self.game:
                    self.game_loop()
            elif choice == '2':
                if self.load_game():
                    self.game_loop()
            elif choice == '3':
                print("再见！")
                break
            else:
                print("无效选项，按回车重试")
                input()

if __name__ == "__main__":
    controller = GameController()
    controller.run()

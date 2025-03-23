import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import datetime

DATA_FILE = "tasks.json"
today = datetime.date.today()

# 预填充历史数据
def initialize_data():
    data = {"tasks": [], "history": {}}
    for i in range(1, 369):
        past_date = today - datetime.timedelta(days=i)
        data["history"][past_date.isoformat()] = {}
    save_data(data)
    return data


# 加载任务数据
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return initialize_data()


# 保存任务数据
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 任务管理类
class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("每日任务追踪")

        self.data = load_data()
        self.today = datetime.date.today().isoformat()

        # 设置当前年
        self.current_year = datetime.date.today().year

        self.create_widgets()
        self.load_tasks()
        self.draw_contribution_map()
        self.schedule_date_check()

    # 调整窗口
    def adjust_height(self):
        self.root.update_idletasks()  # 强制刷新窗口尺寸计算
        new_height = self.root.winfo_reqheight()  # 获取内容所需的高度
        self.root.geometry(f"400x{new_height}")  # 仅修改高度，宽度不变

    def create_widgets(self):
        # 📌 任务管理区域（加边框）
        self.task_frame = tk.LabelFrame(
            self.root, text="任务管理", font=("微软雅黑", 12, "bold"), padx=10, pady=10
        )
        self.task_frame.pack(fill="x", padx=10, pady=10)

        self.task_vars = {}
        self.task_checkbuttons = {}

        # 📌 在任务管理区域上方添加 "今日日期"
        self.date_label = tk.Label(
            self.task_frame,
            text=f"📅 今日日期: {self.today}",
            font=("微软雅黑", 12, "bold"),
            fg="black",
        )
        self.date_label.pack(anchor="w", pady=(0, 5))  # 🔹 让日期靠左，增加底部间距

        # ✅ 按钮行
        button_frame = tk.Frame(self.task_frame)
        button_frame.pack(fill="x", pady=5)

        self.add_task_button = tk.Button(
            button_frame,
            text="➕ 添加任务",
            font=("微软雅黑", 12, "bold"),
            padx=10,
            pady=5,
            command=self.add_task,
        )
        self.add_task_button.pack(side="left", padx=5, pady=5)

        self.save_button = tk.Button(
            button_frame,
            text="💾 保存进度",
            font=("微软雅黑", 12, "bold"),
            padx=10,
            pady=5,
            command=self.save_progress,
        )
        self.save_button.pack(side="left", padx=5, pady=5)

        # 📌 任务列表区域
        self.frame = tk.Frame(self.task_frame)
        self.frame.pack(fill="x")

        # ✅ 任务选择 & 删除按钮行
        task_delete_frame = tk.Frame(self.task_frame)
        task_delete_frame.pack(fill="x", pady=5)

        # 📌 任务删除按钮
        self.delete_task_button = tk.Button(
            task_delete_frame,
            text="🗑 删除任务",
            font=("微软雅黑", 12, "bold"),
            padx=10,
            pady=5,
            command=self.delete_task,
        )
        self.delete_task_button.pack(side="left", padx=5, pady=5)  # 🔹 让按钮靠左，间距相同

        # 📌 任务选择 OptionMenu
        self.task_list = self.data["tasks"] if self.data["tasks"] else ["暂无任务"]  # ✅ 确保不为空
        self.task_var = tk.StringVar(value=self.task_list[0])  # ✅ 设置默认选项

        self.task_menu = tk.OptionMenu(task_delete_frame, self.task_var, *self.task_list)
        self.task_menu.config(font=("微软雅黑", 12, "bold"), padx=10, pady=5, width=8)
        self.task_menu.pack(side="left", padx=5, pady=5)  # 🔹 让 OptionMenu 靠左


        # 📌 热力图区域（用 LabelFrame 包裹，保证布局稳定，并添加标题和边框）
        self.canvas_container = tk.LabelFrame(
            self.root, text="热力图", font=("微软雅黑", 12, "bold"), bd=2, relief="ridge"
        )  # ✅ 使用 LabelFrame
        self.canvas_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 📌 年份选择框 + 任务进度悬停提示（放在同一行）
        self.year_hover_frame = tk.Frame(
            self.canvas_container
        )  # 🔹 创建一个新 Frame 作为容器
        self.year_hover_frame.pack(
            side="top", anchor="w", fill="x", padx=10, pady=5
        )  # 🔹 让它位于热力图顶部

        # 📌 年份选择框（左侧）
        self.year_var = tk.StringVar(value=str(datetime.date.today().year))
        self.year_menu = tk.OptionMenu(
            self.year_hover_frame,
            self.year_var,
            *self.get_available_years(),
            command=self.change_year,
        )
        self.year_menu.config(font=("微软雅黑", 12, "bold"), padx=10, pady=5)
        self.year_menu.pack(side="left", padx=5)  # 🔹 让年份选择框靠左

        # 📌 空白填充 Frame → 让 hover 提示居中
        self.spacer = tk.Label(self.year_hover_frame)
        self.spacer.pack(
            side="left", expand=True
        )  # 🔹 自动填充空白区域，使 hover 提示居中

        # 📌 任务进度悬停提示（居中）
        self.hover_text = tk.StringVar()
        self.hover_label = tk.Label(
            self.year_hover_frame,
            textvariable=self.hover_text,
            font=("微软雅黑", 12, "bold"),
            fg="black",
        )
        self.hover_label.pack(side="left")  # 🔹 放在中间区域

        # 📌 右侧填充 Frame → 确保 hover_text 保持居中
        self.spacer_right = tk.Label(self.year_hover_frame)
        self.spacer_right.pack(
            side="right", expand=True
        )  # 🔹 自动填充空白区域，使 hover 提示居中

        # 📌 Canvas 热力图区域（现在在年份选择框下方）
        self.canvas_frame = tk.Frame(self.canvas_container)
        self.canvas_frame.pack(
            side="top", fill="both", expand=True, padx=15, pady=15
        )  # 🔹 让它位于年份选择框下方

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=800,
            height=160,
            bg="white",
            scrollregion=(0, 0, 2000, 150),
        )
        self.scroll_x = tk.Scrollbar(
            self.canvas_frame, orient="horizontal", command=self.canvas.xview
        )
        self.canvas.configure(xscrollcommand=self.scroll_x.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scroll_x.pack(side="bottom", fill="x")

        self.canvas.bind("<Motion>", self.on_hover)
        
    def load_tasks(self):
        """加载任务并更新任务列表"""
        for widget in self.frame.winfo_children():
            widget.destroy()  # 先清空之前的任务
        self.task_vars.clear()
        self.task_checkbuttons.clear()

        self.frame.columnconfigure(0, weight=1)  # 让任务居中

        for row, task in enumerate(self.data["tasks"]):
            var = tk.IntVar(value=self.data["history"].get(self.today, {}).get(task, 0))

            # 统一字体 & 让文本居中
            chk = tk.Checkbutton(
                self.frame,
                text=task,
                variable=var,
                font=("微软雅黑", 12, "bold"),
                anchor="center",
                padx=10,
            )
            chk.grid(row=row, column=0, sticky="nsew", padx=5, pady=0)  # 让它填充整列

            # 绑定点击事件（此时 chk 已经创建）
            chk.config(command=lambda chk=chk, var=var: self.toggle_color(chk, var))

            self.task_vars[task] = var
            self.task_checkbuttons[task] = chk

            # **初始化颜色**
            self.toggle_color(chk, var)

        # ✅ 更新任务下拉菜单
        self.update_task_menu()

    def toggle_color(self, chk, var):
        """切换任务状态时更改颜色"""
        if var.get():
            chk.config(fg="green")  # 任务完成 → 绿色
        else:
            chk.config(fg="red")  # 任务未完成 → 红色



    def update_task_menu(self):
        """更新任务选择的下拉菜单"""
        menu = self.task_menu["menu"]
        menu.delete(0, "end")  # 清空菜单

        for task in self.data["tasks"]:
            menu.add_command(label=task, command=lambda value=task: self.task_var.set(value))

        # 如果任务列表不为空，则选择第一个任务
        if self.data["tasks"]:
            self.task_var.set(self.data["tasks"][0])
        else:
            self.task_var.set("选择任务")


    def add_task(self):
        task = simpledialog.askstring("添加任务", "输入新任务:")
        if task and task not in self.data["tasks"]:
            self.data["tasks"].append(task)
            self.load_tasks()
            save_data(self.data)
            self.adjust_height()  # 调整窗口高度

    def save_progress(self):
        self.data["history"].setdefault(self.today, {})

        completed_tasks = sum(var.get() for var in self.task_vars.values())  # 计算完成的任务数
        total_tasks = len(self.task_vars)  # 计算当天的任务总数

        self.data["history"][self.today]["completed"] = completed_tasks
        self.data["history"][self.today]["total"] = total_tasks

        save_data(self.data)
        self.draw_contribution_map()
        messagebox.showinfo("保存成功", "今日任务进度已保存！")

    def delete_task(self):
        selected_task = self.task_var.get()  # 获取当前选中的任务
        if selected_task == "选择任务":
            messagebox.showwarning("未选择任务", "请选择要删除的任务")
            return

        # 确认删除
        confirm = messagebox.askyesno("确认删除", f"确定要删除任务: {selected_task} 吗？")
        if confirm:
            self.data["tasks"].remove(selected_task)  # 从任务列表删除
            self.data["history"] = {  # 从所有历史数据中删除该任务
                date: {task: value for task, value in history.items() if task != selected_task}
                for date, history in self.data["history"].items()
            }
            save_data(self.data)  # 保存更新后的数据
            self.load_tasks()  # 重新加载任务
            self.update_task_menu()  # 更新 OptionMenu 选项
            self.adjust_height()  # 重新调整窗口高度



    def draw_month_labels(self, dates, start_x, cell_size, spacing):
        month_positions = {}

        # ✅ 右移月份 1.8 个 cell（仅限第二个及之后的月份）
        month_offset_x = start_x + int(1.6 * (cell_size + spacing))
        first_month = None  # 记录第一个出现的月份

        for i, date in enumerate(dates):
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            month = date_obj.strftime("%b")
            year_month = date_obj.strftime("%Y-%b")  # 区分不同年份的相同月份
            col = i // 7

            if year_month not in month_positions:  # 确保同年同月不会被覆盖
                if first_month is None:
                    first_month = month  # 记录第一个出现的月份
                    month_positions[year_month] = (
                        start_x
                        + int(0.6 * (cell_size + spacing))
                        + col * (cell_size + spacing)
                    )  # ✅ 首月稍微右移
                else:
                    month_positions[year_month] = month_offset_x + col * (
                        cell_size + spacing
                    )  # ✅ 其他月份右移

        # ✅ 绘制月份名称
        for year_month, x in month_positions.items():
            month = year_month.split("-")[1]  # 只提取月份名
            self.canvas.create_text(x, 10, text=month, font=("微软雅黑", 10))

        # ✅ 仅显示 "Mon", "Wed", "Fri"，并左移防止重叠
        offset_x = 8  # 左移 8 个像素
        offset_y = 45  # 下移 8 个像素
        self.canvas.create_text(
            offset_x, offset_y, text="Mon", font=("微软雅黑", 10), anchor="w"
        )
        self.canvas.create_text(
            offset_x,
            offset_y + (cell_size + spacing) * 2,
            text="Wed",
            font=("微软雅黑", 10),
            anchor="w",
        )
        self.canvas.create_text(
            offset_x,
            offset_y + (cell_size + spacing) * 4,
            text="Fri",
            font=("微软雅黑", 10),
            anchor="w",
        )

    def on_hover(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)  # 适配滚动条
        for (x1, y1, x2, y2), (date, completed, total) in self.date_rects.items():
            if x1 <= x <= x2 and y1 <= y <= y2:  # 判断鼠标是否在格子范围内
                self.hover_text.set(f"{date}: {completed}/{total} 任务完成")
                self.hover_label.lift()  # 🔹 确保 label 不会被其他 UI 遮挡
                return
        self.hover_text.set("")
    

    def change_year(self, selected_year):
        self.current_year = int(selected_year)
        self.draw_contribution_map()

    def create_rounded_rect(
        self, x1, y1, x2, y2, radius, fill_color, border_color="#D3D3D3", border_width=2
    ):
        """创建带圆角且带边框的矩形"""
        # 计算边框偏移
        offset = border_width / 2

        # 1️⃣ 绘制比实际稍大的边框
        self.canvas.create_oval(
            x1 - offset,
            y1 - offset,
            x1 + radius * 2 + offset,
            y1 + radius * 2 + offset,
            fill=border_color,
            outline=border_color,
        )  # 左上角
        self.canvas.create_oval(
            x2 - radius * 2 - offset,
            y1 - offset,
            x2 + offset,
            y1 + radius * 2 + offset,
            fill=border_color,
            outline=border_color,
        )  # 右上角
        self.canvas.create_oval(
            x1 - offset,
            y2 - radius * 2 - offset,
            x1 + radius * 2 + offset,
            y2 + offset,
            fill=border_color,
            outline=border_color,
        )  # 左下角
        self.canvas.create_oval(
            x2 - radius * 2 - offset,
            y2 - radius * 2 - offset,
            x2 + offset,
            y2 + offset,
            fill=border_color,
            outline=border_color,
        )  # 右下角

        self.canvas.create_rectangle(
            x1 + radius - offset,
            y1 - offset,
            x2 - radius + offset,
            y2 + offset,
            fill=border_color,
            outline=border_color,
        )
        self.canvas.create_rectangle(
            x1 - offset,
            y1 + radius - offset,
            x2 + offset,
            y2 - radius + offset,
            fill=border_color,
            outline=border_color,
        )

        # 2️⃣ 再绘制实际的圆角矩形（内部颜色）
        self.canvas.create_oval(
            x1,
            y1,
            x1 + radius * 2,
            y1 + radius * 2,
            fill=fill_color,
            outline=fill_color,
        )  # 左上角
        self.canvas.create_oval(
            x2 - radius * 2,
            y1,
            x2,
            y1 + radius * 2,
            fill=fill_color,
            outline=fill_color,
        )  # 右上角
        self.canvas.create_oval(
            x1,
            y2 - radius * 2,
            x1 + radius * 2,
            y2,
            fill=fill_color,
            outline=fill_color,
        )  # 左下角
        self.canvas.create_oval(
            x2 - radius * 2,
            y2 - radius * 2,
            x2,
            y2,
            fill=fill_color,
            outline=fill_color,
        )  # 右下角

        self.canvas.create_rectangle(
            x1 + radius, y1, x2 - radius, y2, fill=fill_color, outline=fill_color
        )
        self.canvas.create_rectangle(
            x1, y1 + radius, x2, y2 - radius, fill=fill_color, outline=fill_color
        )

    def draw_contribution_map(self):
        self.canvas.delete("all")
        history = self.data["history"]


        # ========== 📌 计算当前模式的日期范围 ==========
        if self.current_year == today.year:
            # ✅ 今年模式：显示 “今天” 之前的数据（动态计算）
            end_date = today  # 截止日期是今天
            start_date = today - datetime.timedelta(
                days=7 * 52 + today.weekday() + 1
            )  # 52周+最后一列天数

            # ✅ 计算最后一列的行数（今天是星期几 - 周日）
            weekday_today = today.weekday()  # 0 = Monday, ..., 6 = Sunday
            last_col_rows = (weekday_today + 1) % 7 + 1  # 让 Sunday=0, Saturday=6

            all_dates = [
                (start_date + datetime.timedelta(days=i)).isoformat()
                for i in range((end_date - start_date).days + 1)
            ]
            cols = 53  # 固定52列，最后一列的行数动态计算
            rows = 7
        else:
            # ✅ 过往年份模式：显示 “当年01-01 到 12-31”
            start_date = datetime.date(self.current_year, 1, 1)
            end_date = datetime.date(self.current_year, 12, 31)
            num_days = (end_date - start_date).days + 1

            # ✅ 计算该年 01-01 是星期几
            start_weekday = start_date.weekday()  # 0 = Monday, ..., 6 = Sunday
            start_weekday = (start_weekday + 1) % 7  # 转换成 Sun - Sat 模式

            all_dates = [
                (start_date + datetime.timedelta(days=i)).isoformat()
                for i in range(num_days)
            ]
            cols = (num_days + start_weekday) // 7 + 1  # 计算列数
            rows = 7
            last_col_rows = num_days % 7  # 最后一列的行数

        # ========== 📌 计算每个格子的位置 ==========
        cell_size = 15
        radius = 3  # 圆角半径
        spacing = 4
        start_x, start_y = 10 + 1.8 * (cell_size + spacing), 20  # 右移 2 个 cell
        colors = [
            "#ebedf0",  # 0%  (无任务)
            "#c6e48b",  # 10%
            "#7bc96f",  # 25%
            "#40c463",  # 50%
            "#30a14e",  # 75%
            "#216e39",  # 100%
        ]           
        self.date_rects = {}

        for i, date in enumerate(all_dates):
            count = sum(history.get(date, {}).values()) if date in history else 0
            data = history.get(date, {})
            completed = data.get("completed", 0)
            total = data.get("total", 0)  

            if(completed == 0):
                completion_ratio = 0
            else:
                completion_ratio = completed / total

            color_index = min(int(completion_ratio * (len(colors) - 1)), len(colors) - 1)
            color = colors[color_index]

            # ✅ 计算列、行索引
            if self.current_year == today.year:
                col = i // rows  # 普通列的计算
                row = i % rows

                if col == 52:  # 最后一列
                    row = i - (52 * rows)  # 修正最后一列的行数

            else:
                col = (i + start_weekday) // rows  # 适配 01-01 是星期几
                row = (i + start_weekday) % rows

            # 计算坐标
            x1 = start_x + col * (cell_size + spacing)
            y1 = start_y + row * (cell_size + spacing)
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            # 使用自定义函数绘制圆角矩形
            self.create_rounded_rect(x1, y1, x2, y2, radius, color)

            # 记录坐标
            self.date_rects[(x1, y1, x2, y2)] = (date, completed, total)

        self.draw_month_labels(all_dates, start_x, cell_size, spacing)

        # ✅ 计算正确的 `scrollregion`
        max_width = start_x + cols * (cell_size + spacing)
        self.canvas.config(scrollregion=(0, 0, max_width, 150))

        # ✅ 默认滚动到最右侧
        self.canvas.update_idletasks()  # 确保 Canvas 完成渲染
        self.canvas.xview_moveto(1)  # 滚动到最右端

    def get_available_years(self):
        years = set()
        for date in self.data["history"]:
            year = date.split("-")[0]
            years.add(year)
        return sorted(years, reverse=True)  # 最新年份优先
    
    def schedule_date_check(self):
        """每分钟检查日期是否变化，若变化则刷新 UI 并清除任务勾选"""
        current_date = datetime.date.today().isoformat()
        if current_date != self.today:
            self.today = current_date
            self.date_label.config(text=f"📅 今日日期: {self.today}")
            self.data["history"].setdefault(self.today, {})  # 初始化今日数据为空
            for task in self.data["tasks"]:
                self.data["history"][self.today][task] = 0
            save_data(self.data)
            self.load_tasks()
            self.draw_contribution_map()
            print(f"🕒 日期已更新为 {self.today}，已清空勾选状态")
    
        # 再次安排下一次检查（60秒后）
        self.root.after(60000, self.schedule_date_check)


def generate_test_data():
    data = {"tasks": ["测试任务"], "history": {}}
    today = datetime.date.today()
    current_year = today.year

    for year in range(2022, current_year + 1):
        start_date = datetime.date(year, 1, 1)

        if year == current_year:
            days = (today - start_date).days + 1
        else:
            days = 365

        for i in range(days):
            date = (start_date + datetime.timedelta(days=i)).isoformat()
            completed = i % 5  # 随机完成数量
            total = 5  # 假设每天总共有 5 个任务
            data["history"][date] = {"completed": completed, "total": total}

    save_data(data)

if __name__ == "__main__":
    # generate_test_data()

    root = tk.Tk()

    # 🔹 先设置默认宽度 500px，高度随意（之后会自动调整）
    root.geometry("400x100")

    # 置顶
    root.attributes("-topmost", True)

    app = TaskManager(root)  # 运行 Tkinter 主程序

    # 使用 `after()` 方法，等界面完全加载后再调整高度
    root.after(10, app.adjust_height)  # 100ms 后执行调整

    root.mainloop()

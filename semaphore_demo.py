import tkinter as tk
from tkinter import ttk
import threading
import time
from visualization import SemaphoreVisualization


class Semaphore:
    """信号量实现"""

    def __init__(self, value=1):
        self.value = value
        self.waiting_queue = []
        self.lock = threading.Lock()

    def P(self, thread_name, update_callback):
        """P操作"""
        with self.lock:
            if self.value > 0:
                self.value -= 1
                update_callback(thread_name, "acquire", self.value, self.waiting_queue)
                return True
            else:
                self.waiting_queue.append(thread_name)
                update_callback(thread_name, "block", self.value, self.waiting_queue)
                return False

    def V(self, update_callback):
        """V操作"""
        with self.lock:
            if self.waiting_queue:
                thread_name = self.waiting_queue.pop(0)
                update_callback(thread_name, "release", self.value, self.waiting_queue)
                return thread_name
            else:
                self.value += 1
                update_callback(None, "release", self.value, self.waiting_queue)
                return None


class SemaphoreDemo:
    def __init__(self, parent, status_var):
        self.parent = parent
        self.status_var = status_var
        self.semaphore = Semaphore(3)  # 初始值为3
        self.threads = []
        self.running = False
        self.thread_counter = 1

        self.setup_ui()
        self.visualization = SemaphoreVisualization(self.canvas)

    def setup_ui(self):
        """设置信号量界面"""
        # 控制面板
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="创建线程",
                   command=self.create_thread).pack(side='left', padx=5)
        ttk.Button(control_frame, text="开始竞争",
                   command=self.start_competition).pack(side='left', padx=5)
        ttk.Button(control_frame, text="停止",
                   command=self.stop).pack(side='left', padx=5)
        ttk.Button(control_frame, text="执行V操作",
                   command=self.do_v_operation).pack(side='left', padx=5)

        # 信号量参数
        param_frame = ttk.LabelFrame(self.parent, text="信号量参数")
        param_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(param_frame, text="初始值:").grid(row=0, column=0, padx=5)
        self.sem_value = ttk.Entry(param_frame, width=10)
        self.sem_value.insert(0, "3")
        self.sem_value.grid(row=0, column=1, padx=5)

        ttk.Button(param_frame, text="设置",
                   command=self.set_semaphore).grid(row=0, column=2, padx=5)

        # 线程列表
        thread_frame = ttk.LabelFrame(self.parent, text="线程状态")
        thread_frame.pack(fill='both', expand=True, padx=5, pady=5)

        columns = ('线程名', '状态', '操作')
        self.thread_tree = ttk.Treeview(thread_frame, columns=columns, show='headings')

        for col in columns:
            self.thread_tree.heading(col, text=col)
            self.thread_tree.column(col, width=150)

        self.thread_tree.pack(fill='both', expand=True)

        # 可视化画布
        canvas_frame = ttk.LabelFrame(self.parent, text="信号量状态可视化")
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg='white', height=300)
        self.canvas.pack(fill='both', expand=True)

        # 信号量状态显示
        self.sem_status_var = tk.StringVar(value="信号量值: 3")
        status_label = ttk.Label(self.parent, textvariable=self.sem_status_var)
        status_label.pack(pady=5)

    def create_thread(self):
        """创建新线程"""
        thread_name = f"Thread-{self.thread_counter}"
        self.thread_counter += 1

        thread_info = {
            'name': thread_name,
            'state': '就绪',
            'thread': None
        }

        self.threads.append(thread_info)
        self.update_thread_list()
        self.visualization.update_semaphore_state(
            self.semaphore.value,
            self.semaphore.waiting_queue,
            [t for t in self.threads if t['state'] == '运行']
        )

        self.status_var.set(f"创建线程: {thread_name}")

    def start_competition(self):
        """开始线程竞争信号量"""
        if not self.threads:
            messagebox.showwarning("警告", "没有可执行的线程")
            return

        self.running = True
        for thread_info in self.threads:
            if thread_info['state'] == '就绪':
                thread_info['thread'] = threading.Thread(
                    target=self.thread_worker,
                    args=(thread_info,)
                )
                thread_info['thread'].daemon = True
                thread_info['thread'].start()

        self.status_var.set("开始线程竞争")

    def thread_worker(self, thread_info):
        """线程工作函数"""
        thread_info['state'] = '运行'
        self.parent.after(0, self.update_thread_list)

        # 尝试获取信号量
        acquired = self.semaphore.P(thread_info['name'], self.semaphore_callback)

        if acquired:
            thread_info['state'] = '持有信号量'
            self.parent.after(0, self.update_thread_list)

            # 模拟临界区操作
            time.sleep(3)

            # 释放信号量
            self.semaphore.V(self.semaphore_callback)
            thread_info['state'] = '完成'
            self.parent.after(0, self.update_thread_list)
        else:
            thread_info['state'] = '阻塞'
            self.parent.after(0, self.update_thread_list)

    def do_v_operation(self):
        """手动执行V操作"""
        released_thread = self.semaphore.V(self.semaphore_callback)
        if released_thread:
            self.status_var.set(f"V操作释放线程: {released_thread}")
        else:
            self.status_var.set("V操作增加信号量值")

    def semaphore_callback(self, thread_name, operation, value, waiting_queue):
        """信号量操作回调"""
        self.parent.after(0, lambda: self.update_semaphore_display(
            thread_name, operation, value, waiting_queue
        ))

    def update_semaphore_display(self, thread_name, operation, value, waiting_queue):
        """更新信号量显示"""
        self.sem_status_var.set(f"信号量值: {value}")

        # 更新线程状态
        for thread_info in self.threads:
            if thread_info['name'] == thread_name:
                if operation == "acquire":
                    thread_info['state'] = '持有信号量'
                elif operation == "block":
                    thread_info['state'] = '阻塞'
                elif operation == "release":
                    if thread_info['state'] == '持有信号量':
                        thread_info['state'] = '完成'

        self.update_thread_list()
        self.visualization.update_semaphore_state(
            value, waiting_queue,
            [t for t in self.threads if t['state'] == '持有信号量']
        )

    def set_semaphore(self):
        """设置信号量初始值"""
        try:
            value = int(self.sem_value.get())
            self.semaphore = Semaphore(value)
            self.sem_status_var.set(f"信号量值: {value}")
            self.visualization.update_semaphore_state(value, [], [])
            self.status_var.set(f"信号量初始值设置为: {value}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def stop(self):
        """停止所有线程"""
        self.running = False
        self.status_var.set("已停止所有线程")

    def update_thread_list(self):
        """更新线程列表"""
        for item in self.thread_tree.get_children():
            self.thread_tree.delete(item)

        for thread_info in self.threads:
            operation = "P操作" if thread_info['state'] in ['就绪', '运行'] else "V操作"
            self.thread_tree.insert('', 'end', values=(
                thread_info['name'],
                thread_info['state'],
                operation
            ))
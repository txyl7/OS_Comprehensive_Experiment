import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from process_manager import ProcessManager
from ipc_demo import IPCDemo
from semaphore_demo import SemaphoreDemo
from scheduler import SchedulerDemo

# 进程数据结构（模拟 PCB）
process = {
    'pid': self.next_pid,
    'state': '就绪',  # 初始状态
    'priority': priority,
    'exec_time': exec_time,
    'progress': 0,  # 执行进度（0% → 100%）
    'thread': None
}


# 启动执行：就绪 → 运行，并创建线程
def start_execution(self):
    for p in self.processes:
        if p['state'] == '就绪':
            p['state'] = '运行'
            p['thread'] = threading.Thread(target=self.execute_process, args=(p,))
            p['thread'].start()


# 模拟进程执行（核心状态推进逻辑）
def execute_process(self, process):
    while process['progress'] < 100 and self.running:
        time.sleep(0.1)  # 模拟 CPU 时间片
        increment = 100 / (process['exec_time'] * 10)
        process['progress'] += increment

        # 线程安全地更新 UI
        self.parent.after(0, self.update_process_list)
        self.parent.after(0, lambda: self.visualization.update_processes(self.processes))

    process['state'] = '完成'  # 运行 → 完成


class OSVisualizationPlatform:
    def __init__(self, root):
        self.root = root
        self.root.title("操作系统原理可视化实验平台")
        self.root.geometry("1200x800")
        
        # 先创建状态变量
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        
        # 创建选项卡
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 初始化各个模块
        self.init_process_tab()
        self.init_ipc_tab()
        self.init_semaphore_tab()
        self.init_scheduler_tab()
        
        # 状态栏
        status_bar = tk.Label(root, textvariable=self.status_var, 
                            relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')
    
    def init_process_tab(self):
        """进程线程管理选项卡"""
        self.process_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.process_frame, text="进程线程管理")
        self.process_manager = ProcessManager(self.process_frame, self.status_var)
    
    def init_ipc_tab(self):
        """进程间通信选项卡"""
        self.ipc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ipc_frame, text="进程间通信")
        self.ipc_demo = IPCDemo(self.ipc_frame, self.status_var)
    
    def init_semaphore_tab(self):
        """信号量同步选项卡"""
        self.semaphore_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.semaphore_frame, text="信号量同步")
        self.semaphore_demo = SemaphoreDemo(self.semaphore_frame, self.status_var)
    
    def init_scheduler_tab(self):
        """CPU调度选项卡"""
        self.scheduler_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scheduler_frame, text="CPU调度算法")
        self.scheduler_demo = SchedulerDemo(self.scheduler_frame, self.status_var)

def main():
    root = tk.Tk()
    app = OSVisualizationPlatform(root)
    root.mainloop()

if __name__ == "__main__":
    main()
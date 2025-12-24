import tkinter as tk
from tkinter import ttk
import threading
import time
import random
from visualization import ProcessVisualization

class ProcessManager:
    def __init__(self, parent, status_var):
        self.parent = parent
        self.status_var = status_var
        self.processes = []
        self.next_pid = 1
        self.running = False
        
        self.setup_ui()
        self.visualization = ProcessVisualization(self.canvas)
    
    def setup_ui(self):
        """设置用户界面"""
        # 控制面板
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="创建进程", 
                  command=self.create_process).pack(side='left', padx=5)
        ttk.Button(control_frame, text="开始执行", 
                  command=self.start_execution).pack(side='left', padx=5)
        ttk.Button(control_frame, text="暂停", 
                  command=self.pause_execution).pack(side='left', padx=5)
        ttk.Button(control_frame, text="重置", 
                  command=self.reset).pack(side='left', padx=5)
        
        # 进程参数
        param_frame = ttk.LabelFrame(self.parent, text="进程参数")
        param_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(param_frame, text="执行时间:").grid(row=0, column=0, padx=5)
        self.exec_time = ttk.Entry(param_frame, width=10)
        self.exec_time.insert(0, "3")
        self.exec_time.grid(row=0, column=1, padx=5)
        
        ttk.Label(param_frame, text="优先级:").grid(row=0, column=2, padx=5)
        self.priority = ttk.Entry(param_frame, width=10)
        self.priority.insert(0, "1")
        self.priority.grid(row=0, column=3, padx=5)
        
        # 进程列表
        list_frame = ttk.LabelFrame(self.parent, text="进程列表")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('PID', '状态', '优先级', '执行时间', '进度')
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100)
        
        self.process_tree.pack(fill='both', expand=True)
        
        # 可视化画布
        canvas_frame = ttk.LabelFrame(self.parent, text="进程状态可视化")
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', height=300)
        self.canvas.pack(fill='both', expand=True)
    
    def create_process(self):
        """创建新进程"""
        try:
            exec_time = int(self.exec_time.get())
            priority = int(self.priority.get())
            
            process = {
                'pid': self.next_pid,
                'state': '就绪',
                'priority': priority,
                'exec_time': exec_time,
                'progress': 0,
                'thread': None
            }
            
            self.processes.append(process)
            self.update_process_list()
            self.visualization.update_processes(self.processes)
            
            self.next_pid += 1
            self.status_var.set(f"创建进程 PID: {process['pid']}")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def start_execution(self):
        """开始执行所有进程"""
        if not self.processes:
            messagebox.showwarning("警告", "没有可执行的进程")
            return
        
        self.running = True
        for process in self.processes:
            if process['state'] == '就绪':
                process['state'] = '运行'
                process['thread'] = threading.Thread(
                    target=self.execute_process, 
                    args=(process,)
                )
                process['thread'].start()
        
        self.update_process_list()
        self.visualization.update_processes(self.processes)
        self.status_var.set("开始执行所有进程")
    
    def execute_process(self, process):
        """模拟进程执行"""
        while process['progress'] < 100 and self.running:
            time.sleep(0.1)  # 模拟执行时间
            increment = 100 / (process['exec_time'] * 10)
            process['progress'] = min(100, process['progress'] + increment)
            
            # 更新UI（需要在主线程中执行）
            self.parent.after(0, self.update_process_list)
            self.parent.after(0, lambda: self.visualization.update_processes(self.processes))
            
            if process['progress'] >= 100:
                process['state'] = '完成'
                break
        
        self.parent.after(0, self.update_process_list)
        self.parent.after(0, lambda: self.visualization.update_processes(self.processes))
    
    def pause_execution(self):
        """暂停执行"""
        self.running = False
        self.status_var.set("执行已暂停")
    
    def reset(self):
        """重置所有进程"""
        self.running = False
        time.sleep(0.2)  # 等待线程结束
        
        for process in self.processes:
            process['state'] = '就绪'
            process['progress'] = 0
            process['thread'] = None
        
        self.update_process_list()
        self.visualization.update_processes(self.processes)
        self.status_var.set("系统已重置")
    
    def update_process_list(self):
        """更新进程列表显示"""
        # 清空现有项
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # 添加新项
        for process in self.processes:
            self.process_tree.insert('', 'end', values=(
                process['pid'],
                process['state'],
                process['priority'],
                process['exec_time'],
                f"{process['progress']:.1f}%"
            ))


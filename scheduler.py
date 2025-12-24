import tkinter as tk
from tkinter import ttk
import heapq
import time
from visualization import SchedulerVisualization

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=1):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0

class SchedulerDemo:
    def __init__(self, parent, status_var):
        self.parent = parent
        self.status_var = status_var
        self.processes = []
        self.scheduled_processes = []
        self.next_pid = 1
        self.current_time = 0
        self.is_running = False
        
        self.setup_ui()
        self.visualization = SchedulerVisualization(self.canvas)
    
    def setup_ui(self):
        """设置调度器界面"""
        # 控制面板
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="添加进程", 
                  command=self.add_process).pack(side='left', padx=5)
        ttk.Button(control_frame, text="FCFS调度", 
                  command=lambda: self.run_scheduler('FCFS')).pack(side='left', padx=5)
        ttk.Button(control_frame, text="SJF调度", 
                  command=lambda: self.run_scheduler('SJF')).pack(side='left', padx=5)
        ttk.Button(control_frame, text="RR调度", 
                  command=lambda: self.run_scheduler('RR')).pack(side='left', padx=5)
        ttk.Button(control_frame, text="优先级调度", 
                  command=lambda: self.run_scheduler('Priority')).pack(side='left', padx=5)
        ttk.Button(control_frame, text="重置", 
                  command=self.reset).pack(side='left', padx=5)
        
        # 进程参数
        param_frame = ttk.LabelFrame(self.parent, text="进程参数")
        param_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(param_frame, text="到达时间:").grid(row=0, column=0, padx=5)
        self.arrival_time = ttk.Entry(param_frame, width=8)
        self.arrival_time.insert(0, "0")
        self.arrival_time.grid(row=0, column=1, padx=5)
        
        ttk.Label(param_frame, text="执行时间:").grid(row=0, column=2, padx=5)
        self.burst_time = ttk.Entry(param_frame, width=8)
        self.burst_time.insert(0, "5")
        self.burst_time.grid(row=0, column=3, padx=5)
        
        ttk.Label(param_frame, text="优先级:").grid(row=0, column=4, padx=5)
        self.priority = ttk.Entry(param_frame, width=8)
        self.priority.insert(0, "1")
        self.priority.grid(row=0, column=5, padx=5)
        
        # RR时间片设置
        ttk.Label(param_frame, text="时间片:").grid(row=0, column=6, padx=5)
        self.time_quantum = ttk.Entry(param_frame, width=8)
        self.time_quantum.insert(0, "2")
        self.time_quantum.grid(row=0, column=7, padx=5)
        
        # 进程列表
        list_frame = ttk.LabelFrame(self.parent, text="进程列表")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('PID', '到达时间', '执行时间', '优先级', '状态')
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100)
        
        self.process_tree.pack(fill='both', expand=True)
        
        # 可视化画布
        canvas_frame = ttk.LabelFrame(self.parent, text="调度过程可视化")
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', height=200)
        self.canvas.pack(fill='both', expand=True)
        
        # 性能指标
        metrics_frame = ttk.LabelFrame(self.parent, text="性能指标")
        metrics_frame.pack(fill='x', padx=5, pady=5)
        
        self.avg_wait_var = tk.StringVar(value="平均等待时间: --")
        self.avg_turnaround_var = tk.StringVar(value="平均周转时间: --")
        
        ttk.Label(metrics_frame, textvariable=self.avg_wait_var).pack(side='left', padx=20)
        ttk.Label(metrics_frame, textvariable=self.avg_turnaround_var).pack(side='left', padx=20)
    
    def add_process(self):
        """添加新进程"""
        try:
            arrival = int(self.arrival_time.get())
            burst = int(self.burst_time.get())
            priority = int(self.priority.get())
            
            process = Process(self.next_pid, arrival, burst, priority)
            self.processes.append(process)
            self.next_pid += 1
            
            self.update_process_list()
            self.status_var.set(f"添加进程 PID: {process.pid}")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def run_scheduler(self, algorithm):
        """运行调度算法"""
        if not self.processes:
            messagebox.showwarning("警告", "没有可调度的进程")
            return
        
        self.is_running = True
        self.scheduled_processes = []
        
        if algorithm == 'FCFS':
            self.fcfs_scheduler()
        elif algorithm == 'SJF':
            self.sjf_scheduler()
        elif algorithm == 'RR':
            self.rr_scheduler()
        elif algorithm == 'Priority':
            self.priority_scheduler()
        
        self.calculate_metrics()
        self.status_var.set(f"完成 {algorithm} 调度")
    
    def fcfs_scheduler(self):
        """先来先服务调度"""
        # 按到达时间排序
        ready_queue = sorted(self.processes, key=lambda p: p.arrival_time)
        current_time = 0
        
        for process in ready_queue:
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            process.start_time = current_time
            process.finish_time = current_time + process.burst_time
            process.waiting_time = current_time - process.arrival_time
            process.turnaround_time = process.finish_time - process.arrival_time
            
            # 记录调度过程
            self.scheduled_processes.append({
                'pid': process.pid,
                'start': current_time,
                'end': process.finish_time
            })
            
            current_time = process.finish_time
        
        self.visualization.draw_gantt_chart(self.scheduled_processes)
    
    def sjf_scheduler(self):
        """最短作业优先调度"""
        current_time = 0
        completed = 0
        n = len(self.processes)
        
        # 复制进程列表
        processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in self.processes]
        
        while completed < n:
            # 找出已到达且剩余时间最短的进程
            available = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
            
            if not available:
                current_time += 1
                continue
            
            # 选择剩余时间最短的进程
            shortest = min(available, key=lambda p: p.remaining_time)
            
            if shortest.start_time is None:
                shortest.start_time = current_time
            
            # 执行进程
            execution_time = shortest.remaining_time
            shortest.remaining_time = 0
            current_time += execution_time
            
            shortest.finish_time = current_time
            shortest.waiting_time = shortest.start_time - shortest.arrival_time
            shortest.turnaround_time = shortest.finish_time - shortest.arrival_time
            
            # 记录调度过程
            self.scheduled_processes.append({
                'pid': shortest.pid,
                'start': shortest.start_time,
                'end': current_time
            })
            
            completed += 1
        
        self.visualization.draw_gantt_chart(self.scheduled_processes)
    
    def rr_scheduler(self):
        """时间片轮转调度"""
        try:
            time_quantum = int(self.time_quantum.get())
        except ValueError:
            time_quantum = 2
        
        current_time = 0
        ready_queue = []
        processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in self.processes]
        
        # 按到达时间排序
        processes.sort(key=lambda p: p.arrival_time)
        index = 0
        n = len(processes)
        
        while index < n or ready_queue:
            # 添加到达的进程
            while index < n and processes[index].arrival_time <= current_time:
                ready_queue.append(processes[index])
                index += 1
            
            if not ready_queue:
                current_time += 1
                continue
            
            current_process = ready_queue.pop(0)
            
            if current_process.start_time is None:
                current_process.start_time = current_time
            
            # 执行时间片
            execution_time = min(time_quantum, current_process.remaining_time)
            start_time = current_time
            current_time += execution_time
            current_process.remaining_time -= execution_time
            
            # 记录调度过程
            self.scheduled_processes.append({
                'pid': current_process.pid,
                'start': start_time,
                'end': current_time
            })
            
            # 添加新到达的进程
            while index < n and processes[index].arrival_time <= current_time:
                ready_queue.append(processes[index])
                index += 1
            
            # 如果进程未完成，重新加入队列
            if current_process.remaining_time > 0:
                ready_queue.append(current_process)
            else:
                current_process.finish_time = current_time
                current_process.waiting_time = current_process.start_time - current_process.arrival_time
                current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
        
        self.visualization.draw_gantt_chart(self.scheduled_processes)
    
    def priority_scheduler(self):
        """优先级调度（数字越小优先级越高）"""
        current_time = 0
        completed = 0
        n = len(self.processes)
        processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in self.processes]
        
        while completed < n:
            # 找出已到达且优先级最高的进程
            available = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
            
            if not available:
                current_time += 1
                continue
            
            # 选择优先级最高的进程（数字越小优先级越高）
            highest_priority = min(available, key=lambda p: p.priority)
            
            if highest_priority.start_time is None:
                highest_priority.start_time = current_time
            
            # 执行进程直到完成
            execution_time = highest_priority.remaining_time
            highest_priority.remaining_time = 0
            current_time += execution_time
            
            highest_priority.finish_time = current_time
            highest_priority.waiting_time = highest_priority.start_time - highest_priority.arrival_time
            highest_priority.turnaround_time = highest_priority.finish_time - highest_priority.arrival_time
            
            # 记录调度过程
            self.scheduled_processes.append({
                'pid': highest_priority.pid,
                'start': highest_priority.start_time,
                'end': current_time
            })
            
            completed += 1
        
        self.visualization.draw_gantt_chart(self.scheduled_processes)
    
    def calculate_metrics(self):
        """计算性能指标"""
        total_waiting = sum(p.waiting_time for p in self.processes)
        total_turnaround = sum(p.turnaround_time for p in self.processes)
        n = len(self.processes)
        
        avg_waiting = total_waiting / n if n > 0 else 0
        avg_turnaround = total_turnaround / n if n > 0 else 0
        
        self.avg_wait_var.set(f"平均等待时间: {avg_waiting:.2f}")
        self.avg_turnaround_var.set(f"平均周转时间: {avg_turnaround:.2f}")
    
    def reset(self):
        """重置调度器"""
        self.processes.clear()
        self.scheduled_processes.clear()
        self.next_pid = 1
        self.update_process_list()
        self.visualization.clear()
        self.avg_wait_var.set("平均等待时间: --")
        self.avg_turnaround_var.set("平均周转时间: --")
        self.status_var.set("调度器已重置")
    
    def update_process_list(self):
        """更新进程列表"""
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        for process in self.processes:
            state = "就绪"
            if hasattr(process, 'finish_time') and process.finish_time:
                state = "完成"
            elif hasattr(process, 'start_time') and process.start_time:
                state = "运行"
            
            self.process_tree.insert('', 'end', values=(
                process.pid,
                process.arrival_time,
                process.burst_time,
                process.priority,
                state
            ))
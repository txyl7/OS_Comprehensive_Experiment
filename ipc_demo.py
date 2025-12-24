import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
from visualization import IPCVisualization

class IPCDemo:
    def __init__(self, parent, status_var):
        self.parent = parent
        self.status_var = status_var
        self.message_queue = queue.Queue(maxsize=10)
        self.buffer = []
        self.buffer_size = 5
        self.running = False
        
        self.setup_ui()
        self.visualization = IPCVisualization(self.canvas)
    
    def setup_ui(self):
        """设置IPC界面"""
        # 控制面板
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="启动生产者", 
                  command=self.start_producer).pack(side='left', padx=5)
        ttk.Button(control_frame, text="启动消费者", 
                  command=self.start_consumer).pack(side='left', padx=5)
        ttk.Button(control_frame, text="停止所有", 
                  command=self.stop_all).pack(side='left', padx=5)
        
        # 消息输入
        msg_frame = ttk.Frame(self.parent)
        msg_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(msg_frame, text="消息:").pack(side='left')
        self.message_entry = ttk.Entry(msg_frame, width=20)
        self.message_entry.pack(side='left', padx=5)
        ttk.Button(msg_frame, text="发送消息", 
                  command=self.send_message).pack(side='left', padx=5)
        
        # 缓冲区显示
        buffer_frame = ttk.LabelFrame(self.parent, text="共享缓冲区")
        buffer_frame.pack(fill='x', padx=5, pady=5)
        
        self.buffer_text = tk.Text(buffer_frame, height=4, width=80)
        self.buffer_text.pack(fill='x', padx=5, pady=5)
        
        # 可视化画布
        canvas_frame = ttk.LabelFrame(self.parent, text="IPC通信可视化")
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', height=300)
        self.canvas.pack(fill='both', expand=True)
        
        # 统计信息
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.produced_var = tk.StringVar(value="生产消息: 0")
        self.consumed_var = tk.StringVar(value="消费消息: 0")
        
        ttk.Label(stats_frame, textvariable=self.produced_var).pack(side='left', padx=10)
        ttk.Label(stats_frame, textvariable=self.consumed_var).pack(side='left', padx=10)
        
        self.produced_count = 0
        self.consumed_count = 0
    
    def start_producer(self):
        """启动生产者线程"""
        self.running = True
        producer = threading.Thread(target=self.producer_worker)
        producer.daemon = True
        producer.start()
        self.status_var.set("生产者已启动")
    
    def start_consumer(self):
        """启动消费者线程"""
        self.running = True
        consumer = threading.Thread(target=self.consumer_worker)
        consumer.daemon = True
        consumer.start()
        self.status_var.set("消费者已启动")
    
    def producer_worker(self):
        """生产者工作函数"""
        messages = ["数据A", "数据B", "数据C", "数据D", "数据E"]
        message_index = 0
        
        while self.running:
            try:
                if len(self.buffer) < self.buffer_size:
                    message = f"{messages[message_index]}_{self.produced_count}"
                    self.buffer.append(message)
                    self.produced_count += 1
                    
                    # 更新UI
                    self.parent.after(0, self.update_display)
                    self.parent.after(0, lambda: self.visualization.update_communication(
                        "producer", message, self.buffer
                    ))
                    
                    message_index = (message_index + 1) % len(messages)
                    self.status_var.set(f"生产消息: {message}")
                
                time.sleep(1.5)  # 生产间隔
                
            except Exception as e:
                break
    
    def consumer_worker(self):
        """消费者工作函数"""
        while self.running:
            try:
                if self.buffer:
                    message = self.buffer.pop(0)
                    self.consumed_count += 1
                    
                    # 更新UI
                    self.parent.after(0, self.update_display)
                    self.parent.after(0, lambda: self.visualization.update_communication(
                        "consumer", message, self.buffer
                    ))
                    
                    self.status_var.set(f"消费消息: {message}")
                
                time.sleep(2)  # 消费间隔
                
            except Exception as e:
                break
    
    def send_message(self):
        """手动发送消息"""
        message = self.message_entry.get().strip()
        if message and len(self.buffer) < self.buffer_size:
            self.buffer.append(message)
            self.produced_count += 1
            self.update_display()
            self.visualization.update_communication("manual", message, self.buffer)
            self.message_entry.delete(0, 'end')
            self.status_var.set(f"手动发送: {message}")
    
    def stop_all(self):
        """停止所有线程"""
        self.running = False
        self.status_var.set("IPC通信已停止")
    
    def update_display(self):
        """更新显示"""
        # 更新缓冲区显示
        self.buffer_text.delete('1.0', 'end')
        for i, item in enumerate(self.buffer):
            self.buffer_text.insert('end', f"[{i}] {item}\n")
        
        # 更新统计信息
        self.produced_var.set(f"生产消息: {self.produced_count}")
        self.consumed_var.set(f"消费消息: {self.consumed_count}")
import tkinter as tk
import random

class ProcessVisualization:
    def __init__(self, canvas):
        self.canvas = canvas
        self.process_rects = {}
    
    def update_processes(self, processes):
        """更新进程可视化"""
        self.canvas.delete("all")
        self.process_rects.clear()
        
        if not processes:
            self.canvas.create_text(300, 150, text="暂无进程", font=("Arial", 16))
            return
        
        # 绘制状态图例
        self.draw_legend()
        
        # 绘制进程状态
        x, y = 50, 100
        for i, process in enumerate(processes):
            color = self.get_state_color(process['state'])
            
            # 绘制进程矩形
            rect = self.canvas.create_rectangle(x, y, x+80, y+40, fill=color, outline='black')
            self.canvas.create_text(x+40, y+20, text=f"PID: {process['pid']}", font=("Arial", 10))
            
            # 绘制进度条
            progress_x = x
            progress_y = y + 45
            self.canvas.create_rectangle(progress_x, progress_y, progress_x+80, progress_y+10, outline='gray')
            fill_width = 80 * process['progress'] / 100
            self.canvas.create_rectangle(progress_x, progress_y, progress_x+fill_width, progress_y+10, fill='blue')
            
            self.process_rects[process['pid']] = rect
            
            x += 100
            if x > 700:
                x = 50
                y += 80
    
    def get_state_color(self, state):
        """根据状态返回颜色"""
        colors = {
            '就绪': 'lightgreen',
            '运行': 'lightblue',
            '阻塞': 'lightcoral',
            '完成': 'lightgray'
        }
        return colors.get(state, 'white')
    
    def draw_legend(self):
        """绘制图例"""
        states = ['就绪', '运行', '阻塞', '完成']
        colors = ['lightgreen', 'lightblue', 'lightcoral', 'lightgray']
        
        x, y = 50, 30
        for state, color in zip(states, colors):
            self.canvas.create_rectangle(x, y, x+20, y+20, fill=color, outline='black')
            self.canvas.create_text(x+40, y+10, text=state, anchor='w', font=("Arial", 10))
            x += 100

class IPCVisualization:
    def __init__(self, canvas):
        self.canvas = canvas
    
    def update_communication(self, role, message, buffer):
        """更新IPC通信可视化"""
        self.canvas.delete("all")
        
        # 绘制生产者和消费者
        self.canvas.create_rectangle(100, 100, 200, 200, fill='lightblue', outline='black')
        self.canvas.create_text(150, 150, text="生产者", font=("Arial", 12))
        
        self.canvas.create_rectangle(600, 100, 700, 200, fill='lightgreen', outline='black')
        self.canvas.create_text(650, 150, text="消费者", font=("Arial", 12))
        
        # 绘制缓冲区
        buffer_x, buffer_y = 300, 120
        self.canvas.create_rectangle(buffer_x, buffer_y, buffer_x+200, buffer_y+60, fill='white', outline='black')
        self.canvas.create_text(buffer_x+100, buffer_y-10, text="共享缓冲区", font=("Arial", 10))
        
        # 绘制缓冲区内容
        for i, item in enumerate(buffer):
            self.canvas.create_rectangle(buffer_x+10+i*40, buffer_y+10, 
                                       buffer_x+40+i*40, buffer_y+40, 
                                       fill='yellow', outline='black')
            self.canvas.create_text(buffer_x+25+i*40, buffer_y+25, text=item[:3], font=("Arial", 8))
        
        # 绘制箭头
        if role == "producer":
            self.draw_arrow(200, 150, 300, 150, "red", message)
        elif role == "consumer":
            self.draw_arrow(500, 150, 600, 150, "blue", message)
    
    def draw_arrow(self, x1, y1, x2, y2, color, message):
        """绘制箭头和消息"""
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=color, width=2)
        self.canvas.create_text((x1+x2)/2, y1-20, text=message, fill=color, font=("Arial", 10))

class SemaphoreVisualization:
    def __init__(self, canvas):
        self.canvas = canvas
    
    def update_semaphore_state(self, sem_value, waiting_queue, running_threads):
        """更新信号量状态可视化"""
        self.canvas.delete("all")
        
        # 绘制信号量
        self.canvas.create_rectangle(350, 50, 450, 150, fill='lightyellow', outline='black')
        self.canvas.create_text(400, 100, text=f"信号量\n{sem_value}", font=("Arial", 12))
        
        # 绘制运行中的线程
        x, y = 50, 200
        for i, thread in enumerate(running_threads):
            self.canvas.create_rectangle(x, y, x+120, y+40, fill='lightgreen', outline='black')
            self.canvas.create_text(x+60, y+20, text=thread['name'], font=("Arial", 10))
            self.canvas.create_line(x+60, y+40, 400, 150, arrow=tk.LAST)
            x += 140
        
        # 绘制等待队列
        if waiting_queue:
            self.canvas.create_text(400, 180, text="阻塞队列", font=("Arial", 12))
            queue_x, queue_y = 200, 220
            for i, thread in enumerate(waiting_queue):
                self.canvas.create_rectangle(queue_x, queue_y, queue_x+120, queue_y+40, fill='lightcoral', outline='black')
                self.canvas.create_text(queue_x+60, queue_y+20, text=thread, font=("Arial", 10))
                self.canvas.create_line(queue_x+60, queue_y, 400, 150, arrow=tk.LAST, dash=(4, 2))
                queue_y += 50

class SchedulerVisualization:
    def __init__(self, canvas):
        self.canvas = canvas
    
    def draw_gantt_chart(self, scheduled_processes):
        """绘制甘特图"""
        self.canvas.delete("all")
        
        if not scheduled_processes:
            self.canvas.create_text(300, 100, text="暂无调度数据", font=("Arial", 16))
            return
        
        # 计算时间范围
        max_time = max(p['end'] for p in scheduled_processes)
        
        # 设置坐标参数
        margin_x = 50
        margin_y = 50
        chart_width = 700
        chart_height = 100
        time_scale = chart_width / max(1, max_time)
        
        # 绘制时间轴
        for time in range(0, max_time + 1, max(1, max_time // 10)):
            x = margin_x + time * time_scale
            self.canvas.create_line(x, margin_y + chart_height, x, margin_y + chart_height + 10)
            self.canvas.create_text(x, margin_y + chart_height + 15, text=str(time), font=("Arial", 8))
        
        # 绘制进程条
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        
        y_positions = {}
        current_y = margin_y
        
        for i, process in enumerate(scheduled_processes):
            pid = process['pid']
            if pid not in y_positions:
                y_positions[pid] = current_y
                current_y += 25
            
            y = y_positions[pid]
            x1 = margin_x + process['start'] * time_scale
            x2 = margin_x + process['end'] * time_scale
            
            color = colors[pid % len(colors)]
            self.canvas.create_rectangle(x1, y, x2, y+20, fill=color, outline='black')
            self.canvas.create_text((x1+x2)/2, y+10, text=f"P{pid}", font=("Arial", 8))
        
        # 绘制图例
        legend_x, legend_y = margin_x, margin_y + chart_height + 40
        for pid, y in y_positions.items():
            color = colors[pid % len(colors)]
            self.canvas.create_rectangle(legend_x, legend_y, legend_x+20, legend_y+15, fill=color, outline='black')
            self.canvas.create_text(legend_x+25, legend_y+7, text=f"P{pid}", anchor='w', font=("Arial", 8))
            legend_x += 60
    
    def clear(self):
        """清空画布"""
        self.canvas.delete("all")
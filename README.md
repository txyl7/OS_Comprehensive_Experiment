# OS_Comprehensive_Experiment
Experimental demonstration software for a runnable operating system based on Python

Group members：陶莎（222023335032030）、刘珂宏（222023335032026）、邹翔羽（222023319210089）

## 📌 Features

1. **Process & Thread Management**
   - Simulate multiple processes with configurable execution times
   - Real-time visualization of process states (Ready / Running / Completed)
   - Color-coded status indicators and progress bars
   - Start, pause, and reset controls

2. **Inter-Process Communication (IPC)**
   - Producer–Consumer model simulation
   - Configurable shared buffer size
   - Animated message flow and real-time buffer content display
   - Manual message sending support

3. **Semaphore Synchronization**
   - Customizable initial semaphore value (e.g., 0, 1, 3)
   - Multi-threaded P/V (wait/signal) operations
   - Visual representation of running threads and blocked queue
   - Manual "V" operation to release resources

4. **CPU Scheduling Algorithms**
   - Four classic scheduling policies:
     - **FCFS** (First-Come, First-Served)
     - **SJF** (Shortest Job First)
     - **RR** (Round Robin, with configurable time slice)
     - **Priority Scheduling**
   - Dynamic Gantt chart visualization
   - Automatic calculation of average waiting time and turnaround time

## 🧰 Tech Stack

- **Language**: Python 3.x  
- **GUI Framework**: `tkinter` (standard library)  
- **Concurrency**: `threading`, `queue`  
- **Visualization**: Custom Canvas-based rendering (Gantt charts, state diagrams, data flow)

> ✅ **No external dependencies** — only Python standard libraries are used. Ready to run out of the box!

## ▶️ Quick Start

### 1. Clone or download the project

```bash
git clone https://github.com/your-username/os-visualization-platform.git
cd os-visualization-platform

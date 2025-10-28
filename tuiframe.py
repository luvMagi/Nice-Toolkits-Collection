from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, TextArea, Footer, Static
from textual.binding import Binding
import threading
import time
from datetime import datetime

class LogDisplay(TextArea):
“”“自定义日志显示组件”””
def **init**(self):
super().**init**(read_only=True)
self.show_line_numbers = False

```
def add_log(self, message: str):
    """添加日志消息"""
    current_text = self.text
    if current_text:
        self.text = f"{current_text}\n{message}"
    else:
        self.text = message
    # 滚动到底部
    self.scroll_end()
```

class StatusBar(Static):
“”“状态栏组件”””
def **init**(self):
super().**init**(“就绪”)
self.add_class(“status-bar”)

```
def update_status(self, status: str):
    """更新状态"""
    self.update(status)
```

class MyApp(App):
“”“Textual 应用主类”””

```
CSS = """
Screen {
    background: $surface;
}

#button-group {
    height: auto;
    padding: 1;
    background: $panel;
}

#button-group Button {
    margin-right: 1;
}

#log-container {
    height: 1fr;
    padding: 1;
}

#log-display {
    border: solid $primary;
    height: 100%;
}

.status-bar {
    height: 1;
    padding: 0 1;
    background: $panel;
    color: $text;
}
"""

BINDINGS = [
    Binding("q", "quit", "退出", show=True),
]

def compose(self) -> ComposeResult:
    """构建UI布局"""
    # 顶部按钮组
    with Horizontal(id="button-group"):
        yield Button("按钮 1", id="btn1", variant="primary")
        yield Button("按钮 2", id="btn2", variant="success")
        yield Button("按钮 3", id="btn3", variant="warning")
        yield Button("清空日志", id="btn_clear", variant="error")
    
    # 中间日志显示区域
    with Container(id="log-container"):
        yield LogDisplay().data_bind(id="log-display")
    
    # 底部状态栏
    yield StatusBar().data_bind(id="status-bar")

def on_mount(self):
    """应用启动时"""
    self.log_display = self.query_one("#log-display", LogDisplay)
    self.status_bar = self.query_one("#status-bar", StatusBar)
    self.add_log("应用已启动")
    self.update_status("就绪")

def add_log(self, message: str):
    """线程安全的日志添加函数"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    self.call_from_thread(self.log_display.add_log, log_message)

def update_status(self, status: str):
    """线程安全的状态更新函数"""
    self.call_from_thread(self.status_bar.update_status, f"状态: {status}")

def task_worker_1(self):
    """按钮1的工作线程"""
    self.update_status("正在执行任务 1...")
    self.add_log("任务 1 开始执行")
    
    # 模拟耗时操作
    for i in range(3):
        time.sleep(1)
        self.add_log(f"任务 1 - 步骤 {i+1}/3")
    
    self.add_log("任务 1 完成")
    self.update_status("就绪")

def task_worker_2(self):
    """按钮2的工作线程"""
    self.update_status("正在执行任务 2...")
    self.add_log("任务 2 开始执行")
    
    # 模拟耗时操作
    for i in range(5):
        time.sleep(0.5)
        self.add_log(f"任务 2 - 处理中 {i+1}/5")
    
    self.add_log("任务 2 完成")
    self.update_status("就绪")

def task_worker_3(self):
    """按钮3的工作线程"""
    self.update_status("正在执行任务 3...")
    self.add_log("任务 3 开始执行")
    
    # 模拟耗时操作
    time.sleep(2)
    self.add_log("任务 3 - 数据处理中...")
    time.sleep(1)
    self.add_log("任务 3 - 完成数据处理")
    
    self.add_log("任务 3 完成")
    self.update_status("就绪")

def on_button_pressed(self, event: Button.Pressed) -> None:
    """处理按钮点击事件"""
    button_id = event.button.id
    
    if button_id == "btn1":
        # 启动线程执行任务1
        thread = threading.Thread(target=self.task_worker_1, daemon=True)
        thread.start()
        
    elif button_id == "btn2":
        # 启动线程执行任务2
        thread = threading.Thread(target=self.task_worker_2, daemon=True)
        thread.start()
        
    elif button_id == "btn3":
        # 启动线程执行任务3
        thread = threading.Thread(target=self.task_worker_3, daemon=True)
        thread.start()
        
    elif button_id == "btn_clear":
        self.log_display.text = ""
        self.add_log("日志已清空")
        self.update_status("日志已清空")
```

if **name** == “**main**”:
app = MyApp()
app.run()

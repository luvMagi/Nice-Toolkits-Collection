import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, DirectoryTree, Button, Static
from textual.screen import Screen
from textual.message import Message
from textual.widgets.tree import TreeNode
from textual.notifications import Notification


class FolderBrowserScreen(Screen):
    BINDINGS = [("escape", "pop_screen", "Back")]

    def __init__(self, init_root: str = Path.cwd(), is_folder=False, is_file=False) -> None:
        super().__init__()
        self.selected_path = None
        if os.path.isdir(init_root):
            self.init_root = init_root
        else:
            self.init_root = r'C:\\'


    def compose(self) -> ComposeResult:
        yield Header()
        self.title = "Select Folder"
        yield DirectoryTree(self.init_root, id='directory-tree')
        with Horizontal():
            yield Button("Confirm", id="confirm")
            yield Button("Back", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            directory_tree = self.query_one('#directory-tree', DirectoryTree)
            if hasattr(directory_tree, 'cursor_node') and directory_tree.cursor_node:
                self.selected_path = directory_tree.cursor_node.data.path
                self.selected_path = str(self.selected_path.absolute())
                self.dismiss(self.selected_path)
            else:
                self.notify("Please select a folder", severity="warning")
        else:
            self.dismiss()


class MainScreen(Screen):
    BINDINGS = [("ctrl+o", "open_browser", "Browse")]

    def compose(self) -> ComposeResult:
        self.title = "Selected folder will appear here"
        yield Button("Select Folder", id="select")
        yield Header()
        yield Static("No folder selected", id="path_display")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select":
            self.app.push_screen(FolderBrowserScreen(r'C:\Users\Magi\Mercury\00_Transfer'), self.handle_return_result)

    def handle_return_result(self, result: str | None) -> None:
        if result:

            self.query_one("#path_display", Static).update(result)
        else:
            self.query_one("#path_display", Static).update("No folder selected")

class FolderBrowserApp(App):
    def on_mount(self) -> None:
        self.push_screen(MainScreen())


if __name__ == "__main__":
    app = FolderBrowserApp()
    app.run()

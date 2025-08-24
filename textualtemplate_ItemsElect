from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import ListView, ListItem, Button, Label, Header
# from textual.app import App


class SubScreenLeftRight(Screen):
    CSS = """
        Horizontal {
            width: 100%;
            height: 100%;
        }
        .list-container {
            width: 45%;
            margin: 1 2;
            height: 100%;
        }
        .button-container {
            width: auto;
            min-width: 10%;
            margin: 1 2;
            align: center middle;
            height: 100%;
            content-align-horizontal: center;
        }
        Button {
            content-align: center middle;
            text-align: center;
            align: center middle;
            height: 3;
            width: 8;
            min-width: 8;
            text-style: bold;
            padding: 0;
            margin: 1 1;
        }
    """

    # <editor-fold desc="Usage Example">
    # main_screen
    # When Call
    #   self.push_screen(SubScreenLeftRight(test_items), self.handle_selection_result)

    # When Return
    #   def handle_selection_result(self, selected_items):
    #       """Handle selection results returned from sub-screen"""
    #       if selected_items:
    #           self.query_one("#result", Label).update(f"Selected: {selected_items}")
    #       else:
    #           self.query_one("#result", Label).update("Selected: None")
    #   </editor-fold>

    def __init__(self, items: list, left_label='Options', right_label='Selected', title="SubScreenLeftRight"):
        super().__init__()
        self.initial_items = items
        self.selected_items = []
        self.title = title
        self.left_label = left_label
        self.right_label = right_label

    def compose(self) -> ComposeResult:
        self.title = self.title
        yield Header()
        with Horizontal():
            with Vertical(classes="list-container"):
                yield Label(self.left_label)
                yield ListView(id="left_list")
            with Vertical(classes="button-container"):
                yield Button(">>", id="move_right")
                yield Button("<<", id="move_left")
                yield Button("Confirm", id="confirm")
                yield Button("Return", id="return")
            with Vertical(classes="list-container"):
                yield Label(self.right_label)
                yield ListView(id="right_list")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "left_list":
            # Get a selected item index
            selected_index = event.list_view.index
            if selected_index is not None and selected_index < len(event.list_view.children):
                # Get selected item text
                item = event.list_view.children[selected_index]
                if hasattr(item, 'children') and len(item.children) > 0:
                    label = item.children[0]
                    if hasattr(label, 'renderable'):
                        item_text = str(label.renderable)
                        # Remove original item
                        item.remove()
                        # Create new item and add to right side
                        self.query_one("#right_list", ListView).append(ListItem(Label(item_text)))
        elif event.list_view.id == "right_list":
            # Get a selected item index
            selected_index = event.list_view.index
            if selected_index is not None and selected_index < len(event.list_view.children):
                # Get selected item text
                item = event.list_view.children[selected_index]
                if hasattr(item, 'children') and len(item.children) > 0:
                    label = item.children[0]
                    if hasattr(label, 'renderable'):
                        item_text = str(label.renderable)
                        # Remove original item
                        item.remove()
                        # Create new item and add to left side
                        self.query_one("#left_list", ListView).append(ListItem(Label(item_text)))

    def on_mount(self) -> None:
        left_list = self.query_one("#left_list", ListView)
        for item in self.initial_items:
            left_list.append(ListItem(Label(item)))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        left_list = self.query_one("#left_list", ListView)
        right_list = self.query_one("#right_list", ListView)

        if event.button.id == "move_right":
            # Collect all item text from the left side
            items_text = []
            for item in left_list.children:
                if hasattr(item, 'children') and len(item.children) > 0:
                    label = item.children[0]
                    if hasattr(label, 'renderable'):
                        items_text.append(str(label.renderable))

            # Clear left list
            left_list.clear()

            # Add all items to the right list
            for text in items_text:
                right_list.append(ListItem(Label(text)))

        elif event.button.id == "move_left":
            # Collect all item text from the right side
            items_text = []
            for item in right_list.children:
                if hasattr(item, 'children') and len(item.children) > 0:
                    label = item.children[0]
                    if hasattr(label, 'renderable'):
                        items_text.append(str(label.renderable))

            # Clear right list
            right_list.clear()

            # Add all items to the left list
            for text in items_text:
                left_list.append(ListItem(Label(text)))

        elif event.button.id == "confirm":
            # Get all item text from the right list
            selected_items = []
            for item in right_list.children:
                if hasattr(item, 'children') and len(item.children) > 0:
                    label = item.children[0]
                    if hasattr(label, 'renderable'):
                        selected_items.append(str(label.renderable))
            self.selected_items = selected_items
            # Use dismissing to return data to the main screen
            self.dismiss(self.selected_items)
        elif event.button.id == "return":
            self.dismiss()


# class TestMain(App):
#     def compose(self) -> ComposeResult:
#         yield Button("Open Selection", id="open_select")
#         yield Label("Selected: ", id="result")
#
#     def on_button_pressed(self, event: Button.Pressed) -> None:
#         if event.button.id == "open_select":
#             test_items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
#             # Use callback function to handle returned data
#             self.push_screen(SubScreenLeftRight(test_items), self.handle_selection_result)
#
#     def handle_selection_result(self, selected_items):
#         """Handle selection results returned from sub-screen"""
#         if selected_items:
#             self.query_one("#result", Label).update(f"Selected: {selected_items}")
#         else:
#             self.query_one("#result", Label).update("Selected: None")
#
#     def on_mount(self) -> None:
#         self.title = "SubScreen Test"
#
#
# if __name__ == "__main__":
#     app = TestMain()
#     app.run()

import tkinter as tk

class BoardWidget(tk.Frame):
    def __init__(self, master, size="normal", **kwargs):

        self.colors = {
            "bg": "#2c3e50",
            "tile": "#34495e",
            "text": "#ecf0f1",
            "empty": "#2c3e50",
            "highlight": "#e67e22" # Màu Node đang xét
        }
        bd_value = kwargs.pop('bd', 2)
        relief_value = kwargs.pop('relief', tk.RIDGE)
        
        super().__init__(master, bg=self.colors["bg"], bd=bd_value, relief=relief_value, **kwargs)
        self.labels = []
        
        font_size = 14 if size == "normal" else 8
        w = 4 if size == "normal" else 2
        h = 2 if size == "normal" else 1

        for i in range(3):
            row_labels = []
            for j in range(3):
                lbl = tk.Label(
                    self, text="", width=w, height=h, 
                    font=('Helvetica', font_size, 'bold'),
                    bg=self.colors["bg"], fg=self.colors["text"]
                )
                lbl.grid(row=i, column=j, padx=1, pady=1)
                row_labels.append(lbl)
            self.labels.append(row_labels)

    def update_board(self, board_tuple, highlight=False):
        """Cập nhật các con số lên bảng. Nếu board_tuple rỗng, làm mờ bảng."""
        if not board_tuple:
            for i in range(3):
                for j in range(3):
                    self.labels[i][j].config(text="", bg="#7f8c8d") # Bảng bị vô hiệu hóa (Cụt đường)
            return

        for i in range(3):
            for j in range(3):
                val = board_tuple[i * 3 + j]
                if val == 0:
                    self.labels[i][j].config(text="", bg=self.colors["empty"])
                else:
                    bg_col = self.colors["highlight"] if highlight else self.colors["tile"]
                    self.labels[i][j].config(text=str(val), bg=bg_col)
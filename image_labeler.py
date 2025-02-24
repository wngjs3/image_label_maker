import os

os.environ["TK_SILENCE_DEPRECATION"] = "1"  # Tkinter 경고 메시지 숨기기

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import csv
from datetime import datetime


class ImageLabeler:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Program")

        # 변수 초기화
        self.folder_path = ""
        self.image_files = []
        self.current_index = 0
        self.csv_filename = ""
        self.current_task = ""
        self.labeled_files = set()
        self.label_info = {}  # {파일명: (task, level)} 형식으로 저장

        # UI 구성
        self.create_ui()

        # 키보드 바인딩
        # 일반 숫자 키
        self.root.bind("1", lambda event: self.label_image(1))
        self.root.bind("2", lambda event: self.label_image(2))
        self.root.bind("3", lambda event: self.label_image(3))

        # 숫자패드 키
        self.root.bind("<KP_1>", lambda event: self.label_image(1))
        self.root.bind("<KP_2>", lambda event: self.label_image(2))
        self.root.bind("<KP_3>", lambda event: self.label_image(3))

        # 방향키
        self.root.bind("<Left>", lambda event: self.navigate_image(-1))
        self.root.bind("<Right>", lambda event: self.navigate_image(1))
        # 숫자패드 방향키
        self.root.bind("<KP_Left>", lambda event: self.navigate_image(-1))
        self.root.bind("<KP_Right>", lambda event: self.navigate_image(1))

    def create_ui(self):
        # 메인 프레임
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 왼쪽 프레임 (파일 목록)
        left_frame = tk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # 파일 목록 레이블
        tk.Label(left_frame, text="File List:").pack(anchor=tk.W)

        # 파일 목록 프레임 (스크롤바 포함)
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 스크롤바
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 파일 목록 리스트박스
        self.file_listbox = tk.Listbox(
            list_frame,
            width=40,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=("Arial", 9),  # 폰트 크기 조정
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # 미리보기 레이블
        tk.Label(left_frame, text="Preview:").pack(anchor=tk.W, pady=(10, 0))
        self.preview_label = tk.Label(left_frame)
        self.preview_label.pack(pady=5)

        # 오른쪽 프레임 (기존 UI)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 상단 프레임
        top_frame = tk.Frame(right_frame)
        top_frame.pack(pady=10)

        # 폴더 선택 버튼
        self.folder_btn = tk.Button(
            top_frame, text="Select Folder", command=self.select_folder
        )
        self.folder_btn.pack(side=tk.LEFT, padx=5)

        # Task 입력 프레임
        task_frame = tk.Frame(right_frame)
        task_frame.pack(pady=5)

        tk.Label(task_frame, text="Task:").pack(side=tk.LEFT, padx=5)
        self.task_entry = tk.Entry(task_frame, state="disabled")
        self.task_entry.pack(side=tk.LEFT, padx=5)

        # Task 수정/지정 버튼
        self.task_edit_btn = tk.Button(
            task_frame, text="Edit Task", command=self.enable_task_edit
        )
        self.task_edit_btn.pack(side=tk.LEFT, padx=5)

        self.task_confirm_btn = tk.Button(
            task_frame, text="Confirm Task", command=self.update_task, state="disabled"
        )
        self.task_confirm_btn.pack(side=tk.LEFT, padx=5)

        # 이미지 표시 영역
        self.image_label = tk.Label(right_frame)
        self.image_label.pack(pady=10)

        # 상태 표시
        self.status_label = tk.Label(right_frame, text="Please select a folder")
        self.status_label.pack(pady=5)

        # 라벨링 안내
        instruction = "Press 1, 2, 3 to select Intention Level"
        tk.Label(right_frame, text=instruction).pack(pady=5)

        # 라벨링 히스토리 프레임
        self.history_frame = tk.Frame(right_frame)
        self.history_frame.pack(pady=5, fill=tk.X, padx=10)

        tk.Label(self.history_frame, text="Label:").pack(side=tk.LEFT, padx=5)
        self.history_label = tk.Label(self.history_frame, text="")
        self.history_label.pack(side=tk.LEFT, padx=5)

        # 레벨 라벨을 위한 변수
        self.level_history_label = None

        # 라벨링 버튼 프레임
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=10, side=tk.BOTTOM)

        # 라벨링 버튼들
        self.level_buttons = []
        self.level_colors = {
            1: "#FF3B30",  # 빨간색
            2: "#FF9500",  # 주황색
            3: "#34C759",  # 초록색
        }
        button_texts = {1: "Level 1\nLow", 2: "Level 2\nMedium", 3: "Level 3\nHigh"}

        for i in range(1, 4):
            btn = tk.Button(
                button_frame,
                text=button_texts[i],
                command=lambda x=i: self.label_image(x),
                width=10,
                height=3,
                font=("Arial", 12, "bold"),
            )
            btn.pack(side=tk.LEFT, padx=10)
            self.level_buttons.append(btn)

        # 로딩 프레임 추가 (중앙 정렬을 위해)
        self.loading_frame = tk.Frame(self.root)
        self.loading_frame.pack(expand=True, fill=tk.BOTH)

        self.loading_label = tk.Label(
            self.loading_frame,
            text="Loading files...",
            font=("Arial", 14, "bold"),
            fg="blue",
            bg="white",
            padx=20,
            pady=10,
        )

        # 리스트박스 선택 이벤트 바인딩
        self.file_listbox.bind("<<ListboxSelect>>", self.on_select_file)
        self.file_listbox.bind("<Double-Button-1>", self.on_double_click)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            # 로딩 표시 시작 - UI 비활성화
            self.loading_frame.pack(expand=True, fill=tk.BOTH)
            self.loading_label.pack(expand=True)
            self.root.update()

            # 모든 위젯 비활성화
            for widget in self.root.winfo_children():
                if widget != self.loading_frame:
                    widget.pack_forget()

            try:
                # CSV 파일 설정
                self.csv_filename = os.path.join(
                    self.folder_path,
                    "label_data.csv",
                )

                # 이미지 파일 목록 가져오기
                valid_extensions = {".png", ".jpg", ".jpeg"}
                self.image_files = [
                    f
                    for f in os.listdir(self.folder_path)
                    if os.path.splitext(f.lower())[1] in valid_extensions
                ]
                self.image_files.sort()

                # 라벨링된 파일 목록과 정보 가져오기
                self.labeled_files = set()
                self.label_info = {}
                if os.path.exists(self.csv_filename):
                    with open(self.csv_filename, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        next(reader)  # 헤더 건너뛰기
                        for row in reader:
                            filename, task, level = row
                            self.labeled_files.add(filename)
                            self.label_info[filename] = (task, int(level))

                # UI 업데이트
                if self.image_files:
                    # 모든 위젯 다시 표시
                    for widget in self.root.winfo_children():
                        if widget != self.loading_frame:
                            widget.pack()

                    self.update_file_list()
                    self.show_current_image()

                    # Task 관련 UI 활성화
                    self.task_entry.config(state="normal")
                    self.task_edit_btn.config(state="normal")
                    self.task_entry.focus_set()
                else:
                    messagebox.showinfo("Notice", "No image files in selected folder")

            finally:
                # 로딩 표시 제거
                self.loading_frame.pack_forget()
                self.loading_label.pack_forget()
                self.root.update()

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.image_files:
            # 기본 파일명
            display_text = file

            # 라벨링 정보가 있으면 추가
            if file in self.label_info:
                task, level = self.label_info[file]
                display_text = f"{file} [Task: {task}, Level: {level}]"
                # 레벨에 따른 색상 적용
                self.file_listbox.insert(tk.END, display_text)
                self.file_listbox.itemconfig(
                    tk.END, {"fg": "white", "bg": self.level_colors[level]}
                )
            else:
                # 라벨링되지 않은 파일은 기본 색상
                self.file_listbox.insert(tk.END, display_text)

    def on_select_file(self, event):
        if not self.file_listbox.curselection():
            return

        # 미리보기 업데이트
        selected_idx = self.file_listbox.curselection()[0]
        selected_file = self.image_files[selected_idx]  # 원래 파일명만 사용
        self.show_preview(selected_file)

    def on_double_click(self, event):
        if not self.file_listbox.curselection():
            return

        # 선택한 파일로 이동
        selected_idx = self.file_listbox.curselection()[0]
        self.current_index = selected_idx
        self.show_current_image()

    def show_preview(self, filename):
        image_path = os.path.join(self.folder_path, filename)
        image = Image.open(image_path)

        # 미리보기 크기
        preview_size = (150, 150)
        image.thumbnail(preview_size, Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(image)
        self.preview_label.config(image=photo)
        self.preview_label.image = photo

    def show_current_image(self):
        if 0 <= self.current_index < len(self.image_files):
            image_path = os.path.join(
                self.folder_path, self.image_files[self.current_index]
            )
            image = Image.open(image_path)

            # 이미지 리사이즈 (필요한 경우)
            max_size = (800, 600)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo

            status = f"Image {self.current_index + 1}/{len(self.image_files)}: {self.image_files[self.current_index]}"
            self.status_label.config(text=status)

            current_image = self.image_files[self.current_index]

            # 현재 이미지의 라벨링 정보 표시
            if current_image in self.label_info:
                task, level = self.label_info[current_image]
                self.history_label.config(
                    text=f"'{current_image}' → Task: {task}", font=("Arial", 10)
                )

                # 기존 레벨 라벨 제거
                if self.level_history_label:
                    self.level_history_label.destroy()

                # 레벨 라벨 생성
                self.level_history_label = tk.Label(
                    self.history_frame,
                    text=f"Level: {level}",
                    bg=self.level_colors[level],
                    fg="white",
                    font=("Arial", 10, "bold"),
                    padx=5,
                )
                self.level_history_label.pack(side=tk.LEFT)
            else:
                # 라벨링되지 않은 이미지는 라벨 정보 초기화
                self.history_label.config(text="Not labeled yet")
                if self.level_history_label:
                    self.level_history_label.destroy()
                    self.level_history_label = None
        else:
            self.image_label.config(image="")
            self.status_label.config(text="All images are labeled")

    def enable_task_edit(self):
        """Task 수정 활성화"""
        self.task_entry.config(state="normal")
        self.task_edit_btn.config(state="disabled")
        self.task_confirm_btn.config(state="normal")
        # 포커스 설정
        self.task_entry.focus_set()

    def update_task(self):
        """Task 업데이트"""
        new_task = self.task_entry.get().strip()
        if new_task:
            self.current_task = new_task
            self.task_entry.config(state="disabled")
            self.task_edit_btn.config(state="normal")
            self.task_confirm_btn.config(state="disabled")
        else:
            messagebox.showerror("Error", "Please enter a task")
            # 실패시 다시 입력할 수 있도록 포커스 설정
            self.task_entry.focus_set()

    def label_image(self, level):
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder first")
            return

        if not self.image_files or self.current_index >= len(self.image_files):
            return

        if not self.current_task:
            messagebox.showerror("Error", "Please enter and confirm the task first")
            return

        current_image = self.image_files[self.current_index]

        # 라벨링 정보 저장
        self.label_info[current_image] = (self.current_task, level)
        self.labeled_files.add(current_image)

        # CSV 파일에 라벨 저장
        file_exists = os.path.exists(self.csv_filename)
        with open(self.csv_filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Filename", "Task", "Intention Level"])
            writer.writerow([current_image, self.current_task, level])

        # 파일 리스트 업데이트 (현재 인덱스 저장)
        self.update_file_list()
        self.file_listbox.see(self.current_index)

        # 라벨링 히스토리 UI 업데이트
        self.history_label.config(
            text=f"'{current_image}' → Task: {self.current_task}", font=("Arial", 10)
        )

        if self.level_history_label:
            self.level_history_label.destroy()

        self.level_history_label = tk.Label(
            self.history_frame,
            text=f"Level: {level}",
            bg=self.level_colors[level],
            fg="white",
            font=("Arial", 10, "bold"),
            padx=5,
        )
        self.level_history_label.pack(side=tk.LEFT)

        # 다음 이미지로 이동
        self.current_index += 1
        self.show_current_image()

    def navigate_image(self, direction):
        new_index = self.current_index + direction
        if 0 <= new_index < len(self.image_files):
            self.current_index = new_index
            self.show_current_image()


def main():
    root = tk.Tk()
    app = ImageLabeler(root)
    root.mainloop()


if __name__ == "__main__":
    main()

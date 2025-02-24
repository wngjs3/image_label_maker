import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import csv
from datetime import datetime


class ImageLabeler:
    def __init__(self, root):
        self.root = root
        self.root.title("이미지 라벨링 프로그램")

        # 변수 초기화
        self.folder_path = ""
        self.image_files = []
        self.current_index = 0
        self.csv_filename = ""
        self.current_task = ""
        self.labeled_files = set()

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
        tk.Label(left_frame, text="파일 목록:").pack(anchor=tk.W)

        # 파일 목록 프레임 (스크롤바 포함)
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 스크롤바
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 파일 목록 리스트박스
        self.file_listbox = tk.Listbox(
            list_frame, width=40, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # 미리보기 레이블
        tk.Label(left_frame, text="미리보기:").pack(anchor=tk.W, pady=(10, 0))
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
            top_frame, text="폴더 선택", command=self.select_folder
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
            task_frame, text="Task 수정하기", command=self.enable_task_edit
        )
        self.task_edit_btn.pack(side=tk.LEFT, padx=5)

        self.task_confirm_btn = tk.Button(
            task_frame, text="Task 지정하기", command=self.update_task, state="disabled"
        )
        self.task_confirm_btn.pack(side=tk.LEFT, padx=5)

        # 이미지 표시 영역
        self.image_label = tk.Label(right_frame)
        self.image_label.pack(pady=10)

        # 상태 표시
        self.status_label = tk.Label(right_frame, text="폴더를 선택해주세요")
        self.status_label.pack(pady=5)

        # 라벨링 안내
        instruction = "키보드 1, 2, 3을 눌러 Intention Level을 선택하세요"
        tk.Label(right_frame, text=instruction).pack(pady=5)

        # 라벨링 히스토리 프레임
        history_frame = tk.Frame(right_frame)
        history_frame.pack(pady=5, fill=tk.X, padx=10)

        tk.Label(history_frame, text="최근 라벨링:").pack(side=tk.LEFT, padx=5)
        self.history_label = tk.Label(history_frame, text="")
        self.history_label.pack(side=tk.LEFT, padx=5)

        # 리스트박스 선택 이벤트 바인딩
        self.file_listbox.bind("<<ListboxSelect>>", self.on_select_file)
        self.file_listbox.bind("<Double-Button-1>", self.on_double_click)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            # CSV 파일 설정 - 고정된 파일명 사용
            self.csv_filename = os.path.join(
                self.folder_path,
                "label_data.csv",
            )

            # 이미지 파일 목록 가져오기
            self.image_files = [
                f
                for f in os.listdir(self.folder_path)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
            self.image_files.sort()

            # 라벨링된 파일 목록 가져오기
            self.labeled_files = set()
            if os.path.exists(self.csv_filename):
                with open(self.csv_filename, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader)  # 헤더 건너뛰기
                    self.labeled_files = {row[0] for row in reader}

            # 파일 목록 업데이트
            self.update_file_list()

            if self.image_files:
                self.show_current_image()
            else:
                messagebox.showinfo("알림", "선택한 폴더에 이미지 파일이 없습니다")

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.image_files:
            self.file_listbox.insert(tk.END, file)
            if file in self.labeled_files:
                self.file_listbox.itemconfig(tk.END, {"fg": "gray"})

    def on_select_file(self, event):
        if not self.file_listbox.curselection():
            return

        # 미리보기 업데이트
        selected_idx = self.file_listbox.curselection()[0]
        selected_file = self.image_files[selected_idx]
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

            status = f"이미지 {self.current_index + 1}/{len(self.image_files)}: {self.image_files[self.current_index]}"
            self.status_label.config(text=status)
        else:
            self.image_label.config(image="")
            self.status_label.config(text="모든 이미지의 라벨링이 완료되었습니다")

    def enable_task_edit(self):
        self.task_entry.config(state="normal")
        self.task_edit_btn.config(state="disabled")
        self.task_confirm_btn.config(state="normal")

    def update_task(self):
        new_task = self.task_entry.get().strip()
        if new_task:
            self.current_task = new_task
            self.task_entry.config(state="disabled")
            self.task_edit_btn.config(state="normal")
            self.task_confirm_btn.config(state="disabled")
        else:
            messagebox.showerror("오류", "Task를 입력해주세요")

    def label_image(self, level):
        if not self.folder_path:
            messagebox.showerror("오류", "먼저 폴더를 선택해주세요")
            return

        if not self.image_files or self.current_index >= len(self.image_files):
            return

        if not self.current_task:
            messagebox.showerror(
                "오류", "Task를 입력하고 'Task 수정' 버튼을 눌러주세요"
            )
            return

        current_image = self.image_files[self.current_index]

        # CSV 파일에 라벨 저장
        file_exists = os.path.exists(self.csv_filename)
        with open(self.csv_filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["파일명", "Task", "Intention Level"])
            writer.writerow([current_image, self.current_task, level])

        # 라벨링 히스토리 업데이트
        self.history_label.config(
            text=f"'{current_image}' → Task: {self.current_task}, Level: {level}"
        )

        # 라벨링된 파일 표시 업데이트
        self.labeled_files.add(current_image)
        self.update_file_list()
        self.file_listbox.see(self.current_index)  # 현재 파일이 보이도록 스크롤

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

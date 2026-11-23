# Student GPA Lab

## Chạy trên Windows

Mở thư mục chứa `run_gpa.py` trong File Explorer. Gõ `powershell` vào thanh địa chỉ rồi nhấn Enter. Dùng Python 3.12.

```powershell
Get-Location
Get-ChildItem run_gpa.py
python run_gpa.py --sample
```

Trong menu, chọn **5** để xem kết quả học kỳ mẫu để đối chiếu điểm môn **8,20** và GPA **7,72** (Khá). Thoát rồi chạy lệnh sau để nhập điểm của bạn.

```powershell
python run_gpa.py
```

Chọn **1** để thêm học kỳ, **3** để thêm môn có 3 tín chỉ, rồi **4** để nhập điểm của môn. Nhập lần lượt **7, 8, 7, 9**. Khi xem kết quả, môn có điểm **8,20** và điểm nhân tín chỉ **24,60**. Thêm một môn 2 tín chỉ có cả bốn điểm bằng 7 để tự kiểm tra GPA 7,72. Điểm đã nhập được lưu khi mở lại. Chế độ mẫu dùng `database/sample.db`. Chế độ cá nhân dùng `database/student.db`. Khi sửa điểm, nhập `=` để giữ điểm hiện tại hoặc để trống để xóa đầu điểm.

## Công thức và xếp loại

| Đầu điểm | Trọng số |
|---|---:|
| Quá trình 1 | 10% |
| Quá trình 2 | 20% |
| Giữa kỳ | 20% |
| Cuối kỳ | 50% |

Điểm môn là tổng bốn điểm nhân trọng số tương ứng. GPA học kỳ là tổng **điểm môn × tín chỉ** chia tổng tín chỉ. GPA dùng thang 10. Điểm 0 hợp lệ, còn đầu điểm chưa nhập được lưu là `NULL`. Kết quả cho biết cần bổ sung đầu điểm nào. Kỳ trống hoặc kỳ có môn thiếu điểm sẽ báo chưa đủ dữ liệu tính GPA.

| GPA thực | Xếp loại |
|---|---|
| Từ 8,0 đến 10 | Giỏi |
| Từ 6,0 đến dưới 8,0 | Khá |
| Từ 5,0 đến dưới 6,0 | Trung bình |
| Dưới 5,0 | Kém |

Chương trình dùng GPA thực để xếp loại và hiển thị đến hai chữ số thập phân. Giá trị thực **7,999** có thể hiển thị **8,00** và được xếp **Khá**.

## Học SQL với notebook

```powershell
python -m pip install notebook
python -m notebook notebooks/gpa.ipynb
```

Nhấn **Shift+Enter** từ ô đầu. Notebook tạo SQLite mẫu trong bộ nhớ và dùng `JOIN` để xem môn theo kỳ, sau đó dùng `SUM` để tính tổng tín chỉ và điểm nhân tín chỉ. Xem [năm bài tập](docs/exercises.md) rồi đối chiếu với [lời giải](docs/solutions.md).

`semesters` chứa một dòng cho mỗi học kỳ. `courses` chứa một dòng cho mỗi môn của kỳ, gồm mã, tên, tín chỉ và bốn điểm. Mã môn duy nhất trong một kỳ. Điểm 8,25 được lưu thành 825 để tính chính xác đến 0,01 điểm. Database cá nhân nằm trong thư mục dữ liệu được bỏ qua khi dùng Git.

```powershell
python -m unittest discover -s tests -v
```


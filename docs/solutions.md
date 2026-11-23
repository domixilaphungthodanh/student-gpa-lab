# Lời giải

1. 7 × 0,1 + 8 × 0,2 + 7 × 0,2 + 9 × 0,5 = **8,20**.
2. Dùng `SELECT c.code, s.name FROM courses AS c JOIN semesters AS s ON c.semester_id = s.id`.
3. Dùng `SELECT s.id, COALESCE(SUM(c.credits), 0) FROM semesters AS s LEFT JOIN courses AS c ON c.semester_id = s.id GROUP BY s.id`.
4. Tổng điểm nhân tín chỉ là 24,60 + 14,00 = 38,60. Chia 5 tín chỉ được **7,72**, xếp **Khá**.
5. Đếm số môn có đủ điểm và so với tổng số môn. Phép cộng điểm có đầu điểm `NULL` cho ra `NULL`. Cuối kỳ bằng 0 vẫn là một điểm đã nhập và đóng góp 0 điểm vào tổng trọng số môn.


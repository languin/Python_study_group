import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def calculate_roots():
    try:
        a = float(entry_a.get())
        b = float(entry_b.get())
        c = float(entry_c.get())
    except ValueError:
        messagebox.showerror("Ошибка ввода", "Пожалуйста, введите числовые значения для коэффициентов a, b и c.")
        return

    if a == 0:
        messagebox.showerror("Ошибка", "Коэффициент a не может быть равен нулю для квадратного уравнения.")
        return

    discriminant = b ** 2 - 4 * a * c
    result_lines = [f"Дискриминант: {discriminant:.4f}"]

    if discriminant > 0:
        sqrt_d = discriminant ** 0.5
        x1 = (-b + sqrt_d) / (2 * a)
        x2 = (-b - sqrt_d) / (2 * a)
        result_lines.append("Два действительных корня:")
        result_lines.append(f"x₁ = {x1:.4f}")
        result_lines.append(f"x₂ = {x2:.4f}")
    elif discriminant == 0:
        x = -b / (2 * a)
        result_lines.append("Один действительный корень:")
        result_lines.append(f"x₁ = x₂ = {x:.4f}")
    else:
        result_lines.append("Действительных корней нет (мнимые корни)")

    result_text.configure(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "\n".join(result_lines))
    result_text.configure(state="disabled")


root = tk.Tk()
root.title("Расчёт корней квадратного уравнения")
root.resizable(False, False)

mainframe = ttk.Frame(root, padding="20 15 20 15")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

# Labels and entries for coefficients
ttk.Label(mainframe, text="Коэффициент a:").grid(column=0, row=0, sticky=tk.W)
ttk.Label(mainframe, text="Коэффициент b:").grid(column=0, row=1, sticky=tk.W)
ttk.Label(mainframe, text="Коэффициент c:").grid(column=0, row=2, sticky=tk.W)

entry_a = ttk.Entry(mainframe, width=20)
entry_a.grid(column=1, row=0, padx=(10, 0), pady=5)
entry_b = ttk.Entry(mainframe, width=20)
entry_b.grid(column=1, row=1, padx=(10, 0), pady=5)
entry_c = ttk.Entry(mainframe, width=20)
entry_c.grid(column=1, row=2, padx=(10, 0), pady=5)

calculate_button = ttk.Button(mainframe, text="Рассчитать", command=calculate_roots)
calculate_button.grid(column=0, row=3, columnspan=2, pady=10)

result_label = ttk.Label(mainframe, text="Результат:")
result_label.grid(column=0, row=4, columnspan=2, sticky=tk.W, pady=(10, 0))

result_text = tk.Text(mainframe, width=40, height=5, state="disabled", wrap="word")
result_text.grid(column=0, row=5, columnspan=2, pady=(5, 0))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

entry_a.focus()
root.mainloop()
